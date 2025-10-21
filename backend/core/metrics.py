"""
Production-Grade Metrics Collection
Prometheus-compatible metrics for monitoring and alerting
"""

import time
from typing import Dict, Any, Optional, Callable
from functools import wraps
from datetime import datetime
import asyncio
import logging

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Summary,
    Info,
    CollectorRegistry,
    generate_latest,
    CONTENT_TYPE_LATEST
)

from core.logging import get_logger

logger = get_logger(__name__)


# Create custom registry for better control
registry = CollectorRegistry()


# ============================================================================
# REQUEST METRICS
# ============================================================================

# HTTP request counter
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code'],
    registry=registry
)

# HTTP request duration
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=registry
)

# HTTP request size
http_request_size_bytes = Summary(
    'http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint'],
    registry=registry
)

# HTTP response size
http_response_size_bytes = Summary(
    'http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint'],
    registry=registry
)


# ============================================================================
# AGENT EXECUTION METRICS
# ============================================================================

# Agent execution counter
agent_executions_total = Counter(
    'agent_executions_total',
    'Total agent executions',
    ['package_id', 'tier', 'status'],
    registry=registry
)

# Agent execution duration
agent_execution_duration_seconds = Histogram(
    'agent_execution_duration_seconds',
    'Agent execution duration in seconds',
    ['package_id', 'tier'],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0),
    registry=registry
)

# Agent token usage
agent_tokens_used_total = Counter(
    'agent_tokens_used_total',
    'Total tokens used by agents',
    ['package_id', 'tier', 'token_type'],  # token_type: input, output
    registry=registry
)

# Agent cost
agent_cost_usd_total = Counter(
    'agent_cost_usd_total',
    'Total cost in USD for agent executions',
    ['package_id', 'tier'],
    registry=registry
)

# Active agent executions
agent_executions_active = Gauge(
    'agent_executions_active',
    'Number of currently active agent executions',
    ['package_id', 'tier'],
    registry=registry
)


# ============================================================================
# RATE LIMITING METRICS
# ============================================================================

# Rate limit hits
rate_limit_hits_total = Counter(
    'rate_limit_hits_total',
    'Total rate limit hits (requests blocked)',
    ['tier', 'limit_type'],  # limit_type: request, agent, concurrent, token
    registry=registry
)

# Rate limit usage
rate_limit_usage_ratio = Gauge(
    'rate_limit_usage_ratio',
    'Current rate limit usage as ratio (0-1)',
    ['customer_id', 'tier', 'limit_type'],
    registry=registry
)


# ============================================================================
# CIRCUIT BREAKER METRICS
# ============================================================================

# Circuit breaker state
circuit_breaker_state = Gauge(
    'circuit_breaker_state',
    'Circuit breaker state (0=closed, 1=half_open, 2=open)',
    ['name'],
    registry=registry
)

# Circuit breaker failures
circuit_breaker_failures_total = Counter(
    'circuit_breaker_failures_total',
    'Total circuit breaker failures',
    ['name'],
    registry=registry
)

# Circuit breaker successes
circuit_breaker_successes_total = Counter(
    'circuit_breaker_successes_total',
    'Total circuit breaker successes',
    ['name'],
    registry=registry
)

# Circuit breaker rejections
circuit_breaker_rejections_total = Counter(
    'circuit_breaker_rejections_total',
    'Total circuit breaker rejections (requests blocked)',
    ['name'],
    registry=registry
)


# ============================================================================
# DATABASE METRICS
# ============================================================================

# Database query duration
db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['operation', 'table'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
    registry=registry
)

# Database connections
db_connections_active = Gauge(
    'db_connections_active',
    'Number of active database connections',
    registry=registry
)

# Database errors
db_errors_total = Counter(
    'db_errors_total',
    'Total database errors',
    ['operation', 'error_type'],
    registry=registry
)


# ============================================================================
# REDIS METRICS
# ============================================================================

# Redis operations
redis_operations_total = Counter(
    'redis_operations_total',
    'Total Redis operations',
    ['operation', 'status'],
    registry=registry
)

# Redis operation duration
redis_operation_duration_seconds = Histogram(
    'redis_operation_duration_seconds',
    'Redis operation duration in seconds',
    ['operation'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1),
    registry=registry
)


# ============================================================================
# LLM PROVIDER METRICS
# ============================================================================

# LLM API calls
llm_api_calls_total = Counter(
    'llm_api_calls_total',
    'Total LLM API calls',
    ['provider', 'model', 'status'],
    registry=registry
)

# LLM API duration
llm_api_duration_seconds = Histogram(
    'llm_api_duration_seconds',
    'LLM API call duration in seconds',
    ['provider', 'model'],
    buckets=(0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0),
    registry=registry
)

# LLM API errors
llm_api_errors_total = Counter(
    'llm_api_errors_total',
    'Total LLM API errors',
    ['provider', 'error_type'],
    registry=registry
)


# ============================================================================
# BUSINESS METRICS
# ============================================================================

# Customer signups
customer_signups_total = Counter(
    'customer_signups_total',
    'Total customer signups',
    ['tier'],
    registry=registry
)

# Revenue
revenue_usd_total = Counter(
    'revenue_usd_total',
    'Total revenue in USD',
    ['tier', 'source'],  # source: subscription, usage, overage
    registry=registry
)

# Active customers
customers_active = Gauge(
    'customers_active',
    'Number of active customers',
    ['tier'],
    registry=registry
)


# ============================================================================
# SYSTEM METRICS
# ============================================================================

# Application info
app_info = Info(
    'app',
    'Application information',
    registry=registry
)

# Set application info
app_info.info({
    'name': 'Agent Marketplace Platform',
    'version': '1.0.0',
    'environment': 'production'
})

# Uptime
app_uptime_seconds = Gauge(
    'app_uptime_seconds',
    'Application uptime in seconds',
    registry=registry
)

# Start time for uptime calculation
_start_time = time.time()


def update_uptime():
    """Update application uptime metric"""
    app_uptime_seconds.set(time.time() - _start_time)


# ============================================================================
# METRIC DECORATORS
# ============================================================================

def track_request_metrics(endpoint: str):
    """
    Decorator to track HTTP request metrics.
    
    Usage:
        @track_request_metrics("/api/v1/marketplace/packages")
        async def list_packages():
            pass
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            status_code = 500
            
            try:
                # Get request from args/kwargs
                request = None
                for arg in args:
                    if hasattr(arg, 'method'):
                        request = arg
                        break
                if not request:
                    request = kwargs.get('request')
                
                method = request.method if request else "UNKNOWN"
                
                # Execute function
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                status_code = getattr(result, 'status_code', 200)
                
                return result
            
            finally:
                duration = time.time() - start_time
                
                # Record metrics
                http_requests_total.labels(
                    method=method,
                    endpoint=endpoint,
                    status_code=status_code
                ).inc()
                
                http_request_duration_seconds.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(duration)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            status_code = 500
            
            try:
                result = func(*args, **kwargs)
                status_code = getattr(result, 'status_code', 200)
                return result
            
            finally:
                duration = time.time() - start_time
                method = "UNKNOWN"
                
                http_requests_total.labels(
                    method=method,
                    endpoint=endpoint,
                    status_code=status_code
                ).inc()
                
                http_request_duration_seconds.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(duration)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def track_agent_execution(package_id: str, tier: str):
    """
    Decorator to track agent execution metrics.
    
    Usage:
        @track_agent_execution("ticket-resolver", "premium")
        async def execute_agent():
            pass
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Increment active executions
            agent_executions_active.labels(
                package_id=package_id,
                tier=tier
            ).inc()
            
            start_time = time.time()
            status = "failed"
            
            try:
                result = await func(*args, **kwargs)
                status = getattr(result, 'status', 'success')
                
                # Track tokens and cost if available
                if hasattr(result, 'tokens_used'):
                    agent_tokens_used_total.labels(
                        package_id=package_id,
                        tier=tier,
                        token_type='total'
                    ).inc(result.tokens_used)
                
                if hasattr(result, 'input_tokens'):
                    agent_tokens_used_total.labels(
                        package_id=package_id,
                        tier=tier,
                        token_type='input'
                    ).inc(result.input_tokens)
                
                if hasattr(result, 'output_tokens'):
                    agent_tokens_used_total.labels(
                        package_id=package_id,
                        tier=tier,
                        token_type='output'
                    ).inc(result.output_tokens)
                
                if hasattr(result, 'cost'):
                    agent_cost_usd_total.labels(
                        package_id=package_id,
                        tier=tier
                    ).inc(result.cost)
                
                return result
            
            finally:
                duration = time.time() - start_time
                
                # Decrement active executions
                agent_executions_active.labels(
                    package_id=package_id,
                    tier=tier
                ).dec()
                
                # Record metrics
                agent_executions_total.labels(
                    package_id=package_id,
                    tier=tier,
                    status=status
                ).inc()
                
                agent_execution_duration_seconds.labels(
                    package_id=package_id,
                    tier=tier
                ).observe(duration)
        
        return async_wrapper
    
    return decorator


def track_db_query(operation: str, table: str):
    """
    Decorator to track database query metrics.
    
    Usage:
        @track_db_query("select", "customers")
        def get_customer(customer_id):
            pass
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                db_errors_total.labels(
                    operation=operation,
                    error_type=type(e).__name__
                ).inc()
                raise
            finally:
                duration = time.time() - start_time
                db_query_duration_seconds.labels(
                    operation=operation,
                    table=table
                ).observe(duration)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                db_errors_total.labels(
                    operation=operation,
                    error_type=type(e).__name__
                ).inc()
                raise
            finally:
                duration = time.time() - start_time
                db_query_duration_seconds.labels(
                    operation=operation,
                    table=table
                ).observe(duration)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# ============================================================================
# METRIC HELPERS
# ============================================================================

class MetricsCollector:
    """Helper class for collecting and updating metrics"""
    
    @staticmethod
    def record_rate_limit_hit(tier: str, limit_type: str):
        """Record a rate limit hit"""
        rate_limit_hits_total.labels(
            tier=tier,
            limit_type=limit_type
        ).inc()
    
    @staticmethod
    def update_rate_limit_usage(customer_id: str, tier: str, limit_type: str, ratio: float):
        """Update rate limit usage ratio"""
        rate_limit_usage_ratio.labels(
            customer_id=customer_id,
            tier=tier,
            limit_type=limit_type
        ).set(ratio)
    
    @staticmethod
    def update_circuit_breaker_state(name: str, state: str):
        """Update circuit breaker state"""
        state_value = {'closed': 0, 'half_open': 1, 'open': 2}.get(state, 0)
        circuit_breaker_state.labels(name=name).set(state_value)
    
    @staticmethod
    def record_circuit_breaker_failure(name: str):
        """Record circuit breaker failure"""
        circuit_breaker_failures_total.labels(name=name).inc()
    
    @staticmethod
    def record_circuit_breaker_success(name: str):
        """Record circuit breaker success"""
        circuit_breaker_successes_total.labels(name=name).inc()
    
    @staticmethod
    def record_circuit_breaker_rejection(name: str):
        """Record circuit breaker rejection"""
        circuit_breaker_rejections_total.labels(name=name).inc()
    
    @staticmethod
    def record_llm_api_call(provider: str, model: str, status: str, duration: float):
        """Record LLM API call"""
        llm_api_calls_total.labels(
            provider=provider,
            model=model,
            status=status
        ).inc()
        
        llm_api_duration_seconds.labels(
            provider=provider,
            model=model
        ).observe(duration)
    
    @staticmethod
    def record_llm_api_error(provider: str, error_type: str):
        """Record LLM API error"""
        llm_api_errors_total.labels(
            provider=provider,
            error_type=error_type
        ).inc()
    
    @staticmethod
    def record_customer_signup(tier: str):
        """Record customer signup"""
        customer_signups_total.labels(tier=tier).inc()
    
    @staticmethod
    def record_revenue(tier: str, source: str, amount: float):
        """Record revenue"""
        revenue_usd_total.labels(tier=tier, source=source).inc(amount)
    
    @staticmethod
    def update_active_customers(tier: str, count: int):
        """Update active customer count"""
        customers_active.labels(tier=tier).set(count)
    
    @staticmethod
    def update_db_connections(count: int):
        """Update active database connections"""
        db_connections_active.set(count)


# Global metrics collector instance
metrics_collector = MetricsCollector()


# ============================================================================
# METRICS EXPORT
# ============================================================================

def get_metrics() -> bytes:
    """
    Get Prometheus metrics in text format.
    
    Returns:
        Metrics in Prometheus text format
    """
    update_uptime()
    return generate_latest(registry)


def get_metrics_content_type() -> str:
    """Get content type for metrics endpoint"""
    return CONTENT_TYPE_LATEST
