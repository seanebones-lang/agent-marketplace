"""
Production-Grade Retry Logic with Exponential Backoff
Intelligent retry strategies for different failure scenarios
"""

import asyncio
import time
import random
from typing import Optional, Callable, Any, Type, Tuple
from functools import wraps
import logging

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    wait_random_exponential,
    retry_if_exception_type,
    retry_if_not_exception_type,
    before_sleep_log,
    after_log,
    RetryCallState
)

from core.exceptions import (
    AgentMarketplaceException,
    LLMRateLimitError,
    LLMProviderError,
    DatabaseError,
    DatabaseTimeoutError,
    ExternalServiceError,
    AgentExecutionError,
    AgentTimeoutError,
    CircuitBreakerOpenError,
    ErrorSeverity
)

logger = logging.getLogger(__name__)


# Exceptions that should be retried
RETRYABLE_EXCEPTIONS = (
    LLMRateLimitError,
    LLMProviderError,
    DatabaseError,
    DatabaseTimeoutError,
    ExternalServiceError,
    AgentExecutionError,
    ConnectionError,
    TimeoutError,
    asyncio.TimeoutError,
)

# Exceptions that should NOT be retried
NON_RETRYABLE_EXCEPTIONS = (
    CircuitBreakerOpenError,  # Circuit breaker handles this
    AgentTimeoutError,  # Already timed out, don't retry
    ValueError,  # Invalid input
    TypeError,  # Programming error
    KeyError,  # Programming error
)


def should_retry_exception(exception: Exception) -> bool:
    """
    Determine if an exception should be retried.
    
    Args:
        exception: The exception to check
    
    Returns:
        True if should retry, False otherwise
    """
    # Check if it's a known non-retryable exception
    if isinstance(exception, NON_RETRYABLE_EXCEPTIONS):
        return False
    
    # Check if it's a known retryable exception
    if isinstance(exception, RETRYABLE_EXCEPTIONS):
        return True
    
    # Check if it's our custom exception with retryable flag
    if isinstance(exception, AgentMarketplaceException):
        return exception.retryable
    
    # Default: retry on connection/timeout errors
    exc_str = str(exception).lower()
    if any(keyword in exc_str for keyword in ["connection", "timeout", "unavailable", "rate limit"]):
        return True
    
    # Don't retry by default
    return False


def log_retry_attempt(retry_state: RetryCallState):
    """Log retry attempts with detailed information"""
    if retry_state.outcome and retry_state.outcome.failed:
        exception = retry_state.outcome.exception()
        logger.warning(
            f"Retry attempt {retry_state.attempt_number} failed",
            extra={
                "attempt": retry_state.attempt_number,
                "exception_type": type(exception).__name__,
                "exception_message": str(exception),
                "elapsed_time": retry_state.seconds_since_start,
                "next_wait": retry_state.next_action.sleep if retry_state.next_action else None
            },
            exc_info=True
        )


def log_retry_success(retry_state: RetryCallState):
    """Log successful retry completion"""
    if retry_state.attempt_number > 1:
        logger.info(
            f"Retry succeeded after {retry_state.attempt_number} attempts",
            extra={
                "attempts": retry_state.attempt_number,
                "total_time": retry_state.seconds_since_start
            }
        )


# Retry decorator for LLM API calls
def retry_llm_call(
    max_attempts: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 60.0
):
    """
    Retry decorator for LLM API calls with exponential backoff.
    
    Handles rate limits and transient errors from LLM providers.
    
    Args:
        max_attempts: Maximum number of retry attempts
        min_wait: Minimum wait time between retries (seconds)
        max_wait: Maximum wait time between retries (seconds)
    
    Usage:
        @retry_llm_call(max_attempts=5)
        async def call_anthropic():
            return await anthropic_client.messages.create(...)
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_random_exponential(multiplier=1, min=min_wait, max=max_wait),
        retry=retry_if_exception_type((
            LLMRateLimitError,
            LLMProviderError,
            ConnectionError,
            TimeoutError,
            asyncio.TimeoutError
        )),
        before_sleep=log_retry_attempt,
        after=log_retry_success,
        reraise=True
    )


# Retry decorator for database operations
def retry_database_operation(
    max_attempts: int = 3,
    min_wait: float = 0.5,
    max_wait: float = 10.0
):
    """
    Retry decorator for database operations.
    
    Handles connection errors, timeouts, and deadlocks.
    
    Args:
        max_attempts: Maximum number of retry attempts
        min_wait: Minimum wait time between retries (seconds)
        max_wait: Maximum wait time between retries (seconds)
    
    Usage:
        @retry_database_operation(max_attempts=3)
        async def save_to_db(session, data):
            session.add(data)
            session.commit()
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        retry=retry_if_exception_type((
            DatabaseError,
            DatabaseTimeoutError,
            ConnectionError,
        )),
        before_sleep=log_retry_attempt,
        after=log_retry_success,
        reraise=True
    )


# Retry decorator for agent execution
def retry_agent_execution(
    max_attempts: int = 2,
    min_wait: float = 2.0,
    max_wait: float = 30.0
):
    """
    Retry decorator for agent execution.
    
    Limited retries for agent execution to avoid long wait times.
    
    Args:
        max_attempts: Maximum number of retry attempts
        min_wait: Minimum wait time between retries (seconds)
        max_wait: Maximum wait time between retries (seconds)
    
    Usage:
        @retry_agent_execution(max_attempts=2)
        async def execute_agent(package_id, task):
            return await agent_engine.execute(package_id, task)
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=2, min=min_wait, max=max_wait),
        retry=retry_if_exception_type((
            AgentExecutionError,
            LLMRateLimitError,
            LLMProviderError,
        )),
        before_sleep=log_retry_attempt,
        after=log_retry_success,
        reraise=True
    )


# Retry decorator for external service calls
def retry_external_service(
    max_attempts: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 30.0
):
    """
    Retry decorator for external service calls.
    
    Handles transient errors from external services.
    
    Args:
        max_attempts: Maximum number of retry attempts
        min_wait: Minimum wait time between retries (seconds)
        max_wait: Maximum wait time between retries (seconds)
    
    Usage:
        @retry_external_service(max_attempts=3)
        async def call_stripe_api():
            return await stripe.Customer.create(...)
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_random_exponential(multiplier=1, min=min_wait, max=max_wait),
        retry=retry_if_exception_type((
            ExternalServiceError,
            ConnectionError,
            TimeoutError,
            asyncio.TimeoutError,
        )),
        before_sleep=log_retry_attempt,
        after=log_retry_success,
        reraise=True
    )


# Smart retry decorator that adapts based on exception type
def smart_retry(
    max_attempts: int = 3,
    base_wait: float = 1.0,
    max_wait: float = 60.0,
    jitter: bool = True
):
    """
    Smart retry decorator that adapts retry strategy based on exception type.
    
    - LLM rate limits: Longer waits with jitter
    - Database errors: Quick retries
    - External services: Exponential backoff with jitter
    - Non-retryable errors: No retry
    
    Args:
        max_attempts: Maximum number of retry attempts
        base_wait: Base wait time between retries (seconds)
        max_wait: Maximum wait time between retries (seconds)
        jitter: Add random jitter to wait times
    
    Usage:
        @smart_retry(max_attempts=5)
        async def my_function():
            # Your code here
            pass
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    if asyncio.iscoroutinefunction(func):
                        result = await func(*args, **kwargs)
                    else:
                        result = func(*args, **kwargs)
                    
                    # Log success if this was a retry
                    if attempt > 1:
                        logger.info(
                            f"Function {func.__name__} succeeded after {attempt} attempts",
                            extra={"function": func.__name__, "attempts": attempt}
                        )
                    
                    return result
                
                except Exception as e:
                    last_exception = e
                    
                    # Check if we should retry
                    if not should_retry_exception(e):
                        logger.debug(
                            f"Exception {type(e).__name__} is not retryable",
                            extra={"function": func.__name__, "exception": str(e)}
                        )
                        raise
                    
                    # Check if we have more attempts
                    if attempt >= max_attempts:
                        logger.error(
                            f"Function {func.__name__} failed after {max_attempts} attempts",
                            extra={
                                "function": func.__name__,
                                "attempts": max_attempts,
                                "final_exception": str(e)
                            },
                            exc_info=True
                        )
                        raise
                    
                    # Calculate wait time based on exception type
                    if isinstance(e, LLMRateLimitError):
                        # LLM rate limits: Longer exponential backoff
                        wait_time = min(base_wait * (3 ** (attempt - 1)), max_wait)
                    elif isinstance(e, DatabaseError):
                        # Database errors: Quick retries
                        wait_time = min(base_wait * (1.5 ** (attempt - 1)), max_wait / 2)
                    else:
                        # Default: Exponential backoff
                        wait_time = min(base_wait * (2 ** (attempt - 1)), max_wait)
                    
                    # Add jitter to prevent thundering herd
                    if jitter:
                        wait_time = wait_time * (0.5 + random.random())
                    
                    logger.warning(
                        f"Retry attempt {attempt}/{max_attempts} for {func.__name__}",
                        extra={
                            "function": func.__name__,
                            "attempt": attempt,
                            "max_attempts": max_attempts,
                            "exception_type": type(e).__name__,
                            "exception_message": str(e),
                            "wait_time": wait_time
                        }
                    )
                    
                    # Wait before next attempt
                    await asyncio.sleep(wait_time)
            
            # Should never reach here, but just in case
            if last_exception:
                raise last_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    result = func(*args, **kwargs)
                    
                    if attempt > 1:
                        logger.info(
                            f"Function {func.__name__} succeeded after {attempt} attempts",
                            extra={"function": func.__name__, "attempts": attempt}
                        )
                    
                    return result
                
                except Exception as e:
                    last_exception = e
                    
                    if not should_retry_exception(e):
                        raise
                    
                    if attempt >= max_attempts:
                        logger.error(
                            f"Function {func.__name__} failed after {max_attempts} attempts",
                            extra={
                                "function": func.__name__,
                                "attempts": max_attempts,
                                "final_exception": str(e)
                            },
                            exc_info=True
                        )
                        raise
                    
                    # Calculate wait time
                    if isinstance(e, LLMRateLimitError):
                        wait_time = min(base_wait * (3 ** (attempt - 1)), max_wait)
                    elif isinstance(e, DatabaseError):
                        wait_time = min(base_wait * (1.5 ** (attempt - 1)), max_wait / 2)
                    else:
                        wait_time = min(base_wait * (2 ** (attempt - 1)), max_wait)
                    
                    if jitter:
                        wait_time = wait_time * (0.5 + random.random())
                    
                    logger.warning(
                        f"Retry attempt {attempt}/{max_attempts} for {func.__name__}",
                        extra={
                            "function": func.__name__,
                            "attempt": attempt,
                            "max_attempts": max_attempts,
                            "exception_type": type(e).__name__,
                            "wait_time": wait_time
                        }
                    )
                    
                    time.sleep(wait_time)
            
            if last_exception:
                raise last_exception
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Utility function for manual retry logic
async def retry_with_backoff(
    func: Callable,
    max_attempts: int = 3,
    base_wait: float = 1.0,
    max_wait: float = 60.0,
    retryable_exceptions: Tuple[Type[Exception], ...] = RETRYABLE_EXCEPTIONS,
    *args,
    **kwargs
) -> Any:
    """
    Manually retry a function with exponential backoff.
    
    Useful when you can't use decorators.
    
    Args:
        func: Function to retry
        max_attempts: Maximum number of attempts
        base_wait: Base wait time between retries
        max_wait: Maximum wait time
        retryable_exceptions: Tuple of exceptions to retry on
        *args: Arguments for func
        **kwargs: Keyword arguments for func
    
    Returns:
        Result of func
    
    Raises:
        Last exception if all retries fail
    
    Usage:
        result = await retry_with_backoff(
            my_function,
            max_attempts=5,
            arg1="value1",
            arg2="value2"
        )
    """
    last_exception = None
    
    for attempt in range(1, max_attempts + 1):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        
        except retryable_exceptions as e:
            last_exception = e
            
            if attempt >= max_attempts:
                logger.error(
                    f"Retry failed after {max_attempts} attempts",
                    extra={"attempts": max_attempts, "exception": str(e)},
                    exc_info=True
                )
                raise
            
            wait_time = min(base_wait * (2 ** (attempt - 1)), max_wait)
            wait_time = wait_time * (0.5 + random.random())  # Add jitter
            
            logger.warning(
                f"Retry attempt {attempt}/{max_attempts}",
                extra={
                    "attempt": attempt,
                    "exception": str(e),
                    "wait_time": wait_time
                }
            )
            
            await asyncio.sleep(wait_time)
    
    if last_exception:
        raise last_exception

