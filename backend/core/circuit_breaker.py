"""
Circuit Breaker Pattern for Resilient Service Calls
Prevents cascading failures and provides graceful degradation
"""

import logging
import time
from typing import Callable, Optional, Any
from functools import wraps
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    def __init__(
        self,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold  # Failures before opening
        self.success_threshold = success_threshold  # Successes before closing
        self.timeout = timeout  # Seconds before trying half-open
        self.expected_exception = expected_exception


class CircuitBreaker:
    """
    Circuit breaker implementation for protecting service calls
    """
    
    def __init__(self, config: Optional[CircuitBreakerConfig] = None):
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.last_state_change: float = time.time()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
        
        Returns:
            Function result
        
        Raises:
            CircuitBreakerError: If circuit is open
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit breaker entering HALF_OPEN state")
            else:
                raise CircuitBreakerError(
                    f"Circuit breaker is OPEN. "
                    f"Retry after {self._get_retry_after()}s"
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        
        except self.config.expected_exception as e:
            self._on_failure()
            raise
    
    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """Async version of call"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit breaker entering HALF_OPEN state")
            else:
                raise CircuitBreakerError(
                    f"Circuit breaker is OPEN. "
                    f"Retry after {self._get_retry_after()}s"
                )
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        
        except self.config.expected_exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            
            if self.success_count >= self.config.success_threshold:
                self._close_circuit()
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        self.success_count = 0
        
        if self.failure_count >= self.config.failure_threshold:
            self._open_circuit()
    
    def _open_circuit(self):
        """Open the circuit"""
        self.state = CircuitState.OPEN
        self.last_state_change = time.time()
        logger.warning(
            f"Circuit breaker opened after {self.failure_count} failures"
        )
    
    def _close_circuit(self):
        """Close the circuit"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_state_change = time.time()
        logger.info("Circuit breaker closed - service recovered")
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        return (time.time() - self.last_state_change) >= self.config.timeout
    
    def _get_retry_after(self) -> int:
        """Get seconds until retry is allowed"""
        elapsed = time.time() - self.last_state_change
        return max(0, int(self.config.timeout - elapsed))
    
    def get_state(self) -> dict:
        """Get current circuit breaker state"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time,
            "retry_after": self._get_retry_after() if self.state == CircuitState.OPEN else None
        }
    
    def reset(self):
        """Manually reset circuit breaker"""
        self._close_circuit()
        logger.info("Circuit breaker manually reset")


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open"""
    pass


class CircuitBreakerRegistry:
    """
    Registry for managing multiple circuit breakers
    """
    
    def __init__(self):
        self._breakers: dict[str, CircuitBreaker] = {}
    
    def get_breaker(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ) -> CircuitBreaker:
        """Get or create circuit breaker"""
        if name not in self._breakers:
            self._breakers[name] = CircuitBreaker(config)
        return self._breakers[name]
    
    def get_all_states(self) -> dict:
        """Get states of all circuit breakers"""
        return {
            name: breaker.get_state()
            for name, breaker in self._breakers.items()
        }
    
    def reset_all(self):
        """Reset all circuit breakers"""
        for breaker in self._breakers.values():
            breaker.reset()


# Global registry
_registry = CircuitBreakerRegistry()


def get_circuit_breaker(
    name: str,
    config: Optional[CircuitBreakerConfig] = None
) -> CircuitBreaker:
    """Get circuit breaker from global registry"""
    return _registry.get_breaker(name, config)


def circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    success_threshold: int = 2,
    timeout: int = 60
):
    """
    Decorator for circuit breaker protection
    
    Usage:
        @circuit_breaker(name="external_api", failure_threshold=3, timeout=30)
        async def call_external_api():
            # API call logic
            pass
    """
    config = CircuitBreakerConfig(
        failure_threshold=failure_threshold,
        success_threshold=success_threshold,
        timeout=timeout
    )
    
    breaker = get_circuit_breaker(name, config)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await breaker.call_async(func, *args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Graceful shutdown handler
class GracefulShutdown:
    """
    Handles graceful shutdown of application components
    """
    
    def __init__(self):
        self.shutdown_handlers: list[Callable] = []
        self.is_shutting_down = False
    
    def register(self, handler: Callable):
        """Register shutdown handler"""
        self.shutdown_handlers.append(handler)
        logger.info(f"Registered shutdown handler: {handler.__name__}")
    
    async def shutdown(self):
        """Execute all shutdown handlers"""
        if self.is_shutting_down:
            logger.warning("Shutdown already in progress")
            return
        
        self.is_shutting_down = True
        logger.info("Starting graceful shutdown...")
        
        for handler in self.shutdown_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
                logger.info(f"Shutdown handler completed: {handler.__name__}")
            except Exception as e:
                logger.error(f"Error in shutdown handler {handler.__name__}: {e}")
        
        logger.info("Graceful shutdown complete")


# Global shutdown handler
_shutdown_handler = GracefulShutdown()


def get_shutdown_handler() -> GracefulShutdown:
    """Get global shutdown handler"""
    return _shutdown_handler


def on_shutdown(func: Callable) -> Callable:
    """
    Decorator to register shutdown handler
    
    Usage:
        @on_shutdown
        async def cleanup_resources():
            await db.close()
            await cache.close()
    """
    _shutdown_handler.register(func)
    return func


# Example usage
if __name__ == "__main__":
    import asyncio
    import random
    
    # Example: External API with circuit breaker
    @circuit_breaker(name="external_api", failure_threshold=3, timeout=10)
    async def call_external_api():
        # Simulate random failures
        if random.random() < 0.7:
            raise Exception("API call failed")
        return {"status": "success"}
    
    # Example: Shutdown handler
    @on_shutdown
    async def cleanup():
        print("Cleaning up resources...")
        await asyncio.sleep(1)
        print("Cleanup complete")
    
    # Test circuit breaker
    async def test_circuit_breaker():
        for i in range(10):
            try:
                result = await call_external_api()
                print(f"Call {i+1}: {result}")
            except CircuitBreakerError as e:
                print(f"Call {i+1}: Circuit breaker open - {e}")
            except Exception as e:
                print(f"Call {i+1}: Failed - {e}")
            
            await asyncio.sleep(1)
        
        # Check breaker state
        breaker = get_circuit_breaker("external_api")
        print(f"\nCircuit breaker state: {breaker.get_state()}")
        
        # Test shutdown
        shutdown = get_shutdown_handler()
        await shutdown.shutdown()
    
    asyncio.run(test_circuit_breaker())

