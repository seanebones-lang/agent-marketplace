"""
Production-Grade Circuit Breaker Implementation
Prevents cascading failures and provides graceful degradation
"""

import time
import asyncio
from typing import Optional, Callable, Any, Dict
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

from core.exceptions import CircuitBreakerOpenError

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5  # Number of failures before opening
    success_threshold: int = 2  # Number of successes in half-open before closing
    timeout: int = 60  # Seconds to wait before trying again (half-open)
    window_size: int = 60  # Time window for counting failures (seconds)
    excluded_exceptions: tuple = ()  # Exceptions that don't count as failures


@dataclass
class CircuitBreakerMetrics:
    """Metrics for circuit breaker monitoring"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    state_changes: int = 0
    current_state: CircuitState = CircuitState.CLOSED
    consecutive_failures: int = 0
    consecutive_successes: int = 0


class CircuitBreaker:
    """
    Production-grade circuit breaker for external service calls.
    
    Implements the circuit breaker pattern to prevent cascading failures
    and provide graceful degradation when external services fail.
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Service is failing, requests are rejected immediately
    - HALF_OPEN: Testing if service recovered, limited requests allowed
    
    Usage:
        breaker = CircuitBreaker("anthropic_api", config)
        
        async with breaker:
            result = await call_anthropic_api()
    """
    
    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.metrics = CircuitBreakerMetrics()
        self.opened_at: Optional[float] = None
        self.failure_times: list[float] = []
        self._lock = asyncio.Lock()
    
    async def __aenter__(self):
        """Context manager entry - check if call should be allowed"""
        await self._before_call()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - record success or failure"""
        if exc_type is None:
            await self._on_success()
        elif not isinstance(exc_val, self.config.excluded_exceptions):
            await self._on_failure(exc_val)
        return False  # Don't suppress exceptions
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function with circuit breaker protection.
        
        Args:
            func: Async function to call
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
        
        Returns:
            Result of func
        
        Raises:
            CircuitBreakerOpenError: If circuit is open
            Original exception: If func raises
        """
        async with self:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
    
    async def _before_call(self):
        """Check if call should be allowed based on circuit state"""
        async with self._lock:
            self.metrics.total_calls += 1
            
            # Clean up old failure times outside window
            current_time = time.time()
            window_start = current_time - self.config.window_size
            self.failure_times = [t for t in self.failure_times if t > window_start]
            
            # Check state and decide if call should proceed
            if self.state == CircuitState.OPEN:
                # Check if timeout has passed
                if self.opened_at and (current_time - self.opened_at) >= self.config.timeout:
                    # Transition to half-open
                    await self._transition_to_half_open()
                else:
                    # Still open, reject call
                    self.metrics.rejected_calls += 1
                    logger.warning(
                        f"Circuit breaker '{self.name}' is OPEN. Rejecting call.",
                        extra={
                            "circuit": self.name,
                            "state": self.state.value,
                            "failures": len(self.failure_times),
                            "opened_at": self.opened_at
                        }
                    )
                    raise CircuitBreakerOpenError(
                        service=self.name,
                        details={
                            "state": self.state.value,
                            "opened_at": self.opened_at,
                            "retry_after": int(self.config.timeout - (current_time - self.opened_at)) if self.opened_at else self.config.timeout
                        }
                    )
            
            elif self.state == CircuitState.HALF_OPEN:
                # Allow limited calls to test service
                logger.info(
                    f"Circuit breaker '{self.name}' is HALF_OPEN. Testing service recovery.",
                    extra={"circuit": self.name, "state": self.state.value}
                )
    
    async def _on_success(self):
        """Record successful call"""
        async with self._lock:
            self.metrics.successful_calls += 1
            self.metrics.last_success_time = time.time()
            self.metrics.consecutive_failures = 0
            self.metrics.consecutive_successes += 1
            
            if self.state == CircuitState.HALF_OPEN:
                # Check if we have enough successes to close circuit
                if self.metrics.consecutive_successes >= self.config.success_threshold:
                    await self._transition_to_closed()
            
            logger.debug(
                f"Circuit breaker '{self.name}' recorded success",
                extra={
                    "circuit": self.name,
                    "state": self.state.value,
                    "consecutive_successes": self.metrics.consecutive_successes
                }
            )
    
    async def _on_failure(self, exception: Exception):
        """Record failed call"""
        async with self._lock:
            current_time = time.time()
            self.metrics.failed_calls += 1
            self.metrics.last_failure_time = current_time
            self.metrics.consecutive_successes = 0
            self.metrics.consecutive_failures += 1
            self.failure_times.append(current_time)
            
            logger.warning(
                f"Circuit breaker '{self.name}' recorded failure: {type(exception).__name__}",
                extra={
                    "circuit": self.name,
                    "state": self.state.value,
                    "consecutive_failures": self.metrics.consecutive_failures,
                    "failures_in_window": len(self.failure_times),
                    "exception": str(exception)
                }
            )
            
            # Check if we should open the circuit
            if self.state == CircuitState.CLOSED:
                if len(self.failure_times) >= self.config.failure_threshold:
                    await self._transition_to_open()
            
            elif self.state == CircuitState.HALF_OPEN:
                # Any failure in half-open state reopens circuit
                await self._transition_to_open()
    
    async def _transition_to_open(self):
        """Transition circuit to OPEN state"""
        if self.state != CircuitState.OPEN:
            self.state = CircuitState.OPEN
            self.opened_at = time.time()
            self.metrics.state_changes += 1
            self.metrics.current_state = CircuitState.OPEN
            
            logger.error(
                f"Circuit breaker '{self.name}' transitioned to OPEN",
                extra={
                    "circuit": self.name,
                    "state": self.state.value,
                    "failures": len(self.failure_times),
                    "consecutive_failures": self.metrics.consecutive_failures,
                    "timeout": self.config.timeout
                }
            )
    
    async def _transition_to_half_open(self):
        """Transition circuit to HALF_OPEN state"""
        if self.state != CircuitState.HALF_OPEN:
            self.state = CircuitState.HALF_OPEN
            self.metrics.state_changes += 1
            self.metrics.current_state = CircuitState.HALF_OPEN
            self.metrics.consecutive_successes = 0
            
            logger.info(
                f"Circuit breaker '{self.name}' transitioned to HALF_OPEN",
                extra={
                    "circuit": self.name,
                    "state": self.state.value,
                    "opened_duration": time.time() - self.opened_at if self.opened_at else 0
                }
            )
    
    async def _transition_to_closed(self):
        """Transition circuit to CLOSED state"""
        if self.state != CircuitState.CLOSED:
            self.state = CircuitState.CLOSED
            self.opened_at = None
            self.failure_times.clear()
            self.metrics.state_changes += 1
            self.metrics.current_state = CircuitState.CLOSED
            self.metrics.consecutive_failures = 0
            
            logger.info(
                f"Circuit breaker '{self.name}' transitioned to CLOSED",
                extra={
                    "circuit": self.name,
                    "state": self.state.value,
                    "consecutive_successes": self.metrics.consecutive_successes
                }
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current circuit breaker metrics"""
        return {
            "name": self.name,
            "state": self.state.value,
            "total_calls": self.metrics.total_calls,
            "successful_calls": self.metrics.successful_calls,
            "failed_calls": self.metrics.failed_calls,
            "rejected_calls": self.metrics.rejected_calls,
            "success_rate": (
                self.metrics.successful_calls / self.metrics.total_calls * 100
                if self.metrics.total_calls > 0 else 0
            ),
            "consecutive_failures": self.metrics.consecutive_failures,
            "consecutive_successes": self.metrics.consecutive_successes,
            "failures_in_window": len(self.failure_times),
            "state_changes": self.metrics.state_changes,
            "last_failure_time": (
                datetime.fromtimestamp(self.metrics.last_failure_time).isoformat()
                if self.metrics.last_failure_time else None
            ),
            "last_success_time": (
                datetime.fromtimestamp(self.metrics.last_success_time).isoformat()
                if self.metrics.last_success_time else None
            ),
            "opened_at": (
                datetime.fromtimestamp(self.opened_at).isoformat()
                if self.opened_at else None
            ),
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "success_threshold": self.config.success_threshold,
                "timeout": self.config.timeout,
                "window_size": self.config.window_size
            }
        }
    
    async def reset(self):
        """Reset circuit breaker to initial state (for testing/admin)"""
        async with self._lock:
            self.state = CircuitState.CLOSED
            self.opened_at = None
            self.failure_times.clear()
            self.metrics = CircuitBreakerMetrics()
            
            logger.info(
                f"Circuit breaker '{self.name}' has been reset",
                extra={"circuit": self.name}
            )


class CircuitBreakerRegistry:
    """
    Registry for managing multiple circuit breakers.
    
    Provides centralized management and monitoring of all circuit breakers.
    """
    
    def __init__(self):
        self._breakers: Dict[str, CircuitBreaker] = {}
        self._lock = asyncio.Lock()
    
    async def get_or_create(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ) -> CircuitBreaker:
        """Get existing circuit breaker or create new one"""
        async with self._lock:
            if name not in self._breakers:
                self._breakers[name] = CircuitBreaker(name, config)
                logger.info(f"Created circuit breaker: {name}")
            return self._breakers[name]
    
    def get(self, name: str) -> Optional[CircuitBreaker]:
        """Get circuit breaker by name"""
        return self._breakers.get(name)
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics for all circuit breakers"""
        return {
            name: breaker.get_metrics()
            for name, breaker in self._breakers.items()
        }
    
    async def reset_all(self):
        """Reset all circuit breakers"""
        async with self._lock:
            for breaker in self._breakers.values():
                await breaker.reset()
            logger.info("All circuit breakers have been reset")
    
    def get_open_circuits(self) -> list[str]:
        """Get list of open circuit breaker names"""
        return [
            name for name, breaker in self._breakers.items()
            if breaker.state == CircuitState.OPEN
        ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status of all circuits"""
        total = len(self._breakers)
        open_count = len(self.get_open_circuits())
        half_open = sum(
            1 for b in self._breakers.values()
            if b.state == CircuitState.HALF_OPEN
        )
        closed = sum(
            1 for b in self._breakers.values()
            if b.state == CircuitState.CLOSED
        )
        
        return {
            "total_circuits": total,
            "open": open_count,
            "half_open": half_open,
            "closed": closed,
            "health_percentage": ((closed + half_open) / total * 100) if total > 0 else 100,
            "open_circuits": self.get_open_circuits()
        }


# Global registry instance
circuit_breaker_registry = CircuitBreakerRegistry()


# Convenience function for getting circuit breakers
async def get_circuit_breaker(
    name: str,
    config: Optional[CircuitBreakerConfig] = None
) -> CircuitBreaker:
    """Get or create a circuit breaker"""
    return await circuit_breaker_registry.get_or_create(name, config)
