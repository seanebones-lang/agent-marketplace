"""
Distributed Tracing with OpenTelemetry
Integrates with Jaeger, Tempo, and other OTLP-compatible backends
"""

import logging
import os
from typing import Optional, Dict, Any, Callable
from functools import wraps
from contextlib import contextmanager

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.trace import Status, StatusCode
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

logger = logging.getLogger(__name__)


class TelemetryConfig:
    """Telemetry configuration"""
    
    def __init__(self):
        self.service_name = os.getenv("SERVICE_NAME", "agent-marketplace")
        self.service_version = os.getenv("SERVICE_VERSION", "2.1.0")
        self.environment = os.getenv("ENVIRONMENT", "development")
        
        # OTLP endpoint configuration
        self.otlp_endpoint = os.getenv("OTLP_ENDPOINT", "http://localhost:4317")
        self.jaeger_endpoint = os.getenv("JAEGER_ENDPOINT", "http://localhost:14268/api/traces")
        self.tempo_endpoint = os.getenv("TEMPO_ENDPOINT", "http://localhost:4317")
        
        # Feature flags
        self.tracing_enabled = os.getenv("TRACING_ENABLED", "true").lower() == "true"
        self.metrics_enabled = os.getenv("METRICS_ENABLED", "true").lower() == "true"
        self.console_export = os.getenv("CONSOLE_EXPORT", "false").lower() == "true"
        
        # Sampling configuration
        self.sampling_rate = float(os.getenv("SAMPLING_RATE", "1.0"))  # 1.0 = 100%


class TelemetryManager:
    """
    Centralized telemetry management for tracing and metrics
    """
    
    def __init__(self, config: Optional[TelemetryConfig] = None):
        self.config = config or TelemetryConfig()
        self.tracer_provider: Optional[TracerProvider] = None
        self.meter_provider: Optional[MeterProvider] = None
        self.tracer: Optional[trace.Tracer] = None
        self.meter: Optional[metrics.Meter] = None
        
        self._initialize()
    
    def _initialize(self):
        """Initialize OpenTelemetry providers"""
        # Create resource with service information
        resource = Resource.create({
            SERVICE_NAME: self.config.service_name,
            SERVICE_VERSION: self.config.service_version,
            "environment": self.config.environment,
            "deployment.environment": self.config.environment
        })
        
        # Initialize tracing
        if self.config.tracing_enabled:
            self._initialize_tracing(resource)
        
        # Initialize metrics
        if self.config.metrics_enabled:
            self._initialize_metrics(resource)
    
    def _initialize_tracing(self, resource: Resource):
        """Initialize distributed tracing"""
        self.tracer_provider = TracerProvider(resource=resource)
        
        # Add OTLP exporter
        otlp_exporter = OTLPSpanExporter(
            endpoint=self.config.otlp_endpoint,
            insecure=True  # Use TLS in production
        )
        self.tracer_provider.add_span_processor(
            BatchSpanProcessor(otlp_exporter)
        )
        
        # Add console exporter for debugging
        if self.config.console_export:
            console_exporter = ConsoleSpanExporter()
            self.tracer_provider.add_span_processor(
                BatchSpanProcessor(console_exporter)
            )
        
        # Set global tracer provider
        trace.set_tracer_provider(self.tracer_provider)
        self.tracer = trace.get_tracer(__name__)
        
        logger.info(
            f"Tracing initialized: {self.config.service_name} -> {self.config.otlp_endpoint}"
        )
    
    def _initialize_metrics(self, resource: Resource):
        """Initialize metrics collection"""
        # Create OTLP metric exporter
        otlp_metric_exporter = OTLPMetricExporter(
            endpoint=self.config.otlp_endpoint,
            insecure=True
        )
        
        # Create metric reader
        metric_reader = PeriodicExportingMetricReader(
            otlp_metric_exporter,
            export_interval_millis=60000  # Export every 60 seconds
        )
        
        # Add console exporter for debugging
        if self.config.console_export:
            console_metric_exporter = ConsoleMetricExporter()
            console_reader = PeriodicExportingMetricReader(
                console_metric_exporter,
                export_interval_millis=60000
            )
            self.meter_provider = MeterProvider(
                resource=resource,
                metric_readers=[metric_reader, console_reader]
            )
        else:
            self.meter_provider = MeterProvider(
                resource=resource,
                metric_readers=[metric_reader]
            )
        
        # Set global meter provider
        metrics.set_meter_provider(self.meter_provider)
        self.meter = metrics.get_meter(__name__)
        
        logger.info(f"Metrics initialized: {self.config.service_name}")
    
    def instrument_app(self, app):
        """Instrument FastAPI application"""
        if self.config.tracing_enabled:
            FastAPIInstrumentor.instrument_app(app)
            logger.info("FastAPI instrumentation enabled")
    
    def instrument_redis(self, redis_client):
        """Instrument Redis client"""
        if self.config.tracing_enabled:
            RedisInstrumentor().instrument(redis_client=redis_client)
            logger.info("Redis instrumentation enabled")
    
    def instrument_sqlalchemy(self, engine):
        """Instrument SQLAlchemy engine"""
        if self.config.tracing_enabled:
            SQLAlchemyInstrumentor().instrument(engine=engine)
            logger.info("SQLAlchemy instrumentation enabled")
    
    @contextmanager
    def trace_span(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        kind: trace.SpanKind = trace.SpanKind.INTERNAL
    ):
        """
        Context manager for creating spans
        
        Usage:
            with telemetry.trace_span("process_data", {"user_id": 123}):
                # Your code here
                pass
        """
        if not self.tracer:
            yield None
            return
        
        with self.tracer.start_as_current_span(name, kind=kind) as span:
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, value)
            
            try:
                yield span
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise
    
    def trace_function(
        self,
        name: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None
    ):
        """
        Decorator for tracing functions
        
        Usage:
            @telemetry.trace_function(name="my_function", attributes={"type": "processing"})
            async def my_function():
                pass
        """
        def decorator(func: Callable) -> Callable:
            span_name = name or func.__name__
            
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                with self.trace_span(span_name, attributes):
                    return await func(*args, **kwargs)
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                with self.trace_span(span_name, attributes):
                    return func(*args, **kwargs)
            
            # Return appropriate wrapper based on function type
            import asyncio
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
    
    def create_counter(
        self,
        name: str,
        description: str = "",
        unit: str = "1"
    ) -> Optional[metrics.Counter]:
        """Create a counter metric"""
        if not self.meter:
            return None
        
        return self.meter.create_counter(
            name=name,
            description=description,
            unit=unit
        )
    
    def create_histogram(
        self,
        name: str,
        description: str = "",
        unit: str = "ms"
    ) -> Optional[metrics.Histogram]:
        """Create a histogram metric"""
        if not self.meter:
            return None
        
        return self.meter.create_histogram(
            name=name,
            description=description,
            unit=unit
        )
    
    def create_gauge(
        self,
        name: str,
        description: str = "",
        unit: str = "1"
    ) -> Optional[metrics.ObservableGauge]:
        """Create a gauge metric"""
        if not self.meter:
            return None
        
        return self.meter.create_observable_gauge(
            name=name,
            description=description,
            unit=unit
        )
    
    def shutdown(self):
        """Shutdown telemetry providers"""
        if self.tracer_provider:
            self.tracer_provider.shutdown()
        
        if self.meter_provider:
            self.meter_provider.shutdown()
        
        logger.info("Telemetry shutdown complete")


# Global telemetry instance
_telemetry_manager: Optional[TelemetryManager] = None


def get_telemetry() -> TelemetryManager:
    """Get or create global telemetry manager"""
    global _telemetry_manager
    
    if _telemetry_manager is None:
        _telemetry_manager = TelemetryManager()
    
    return _telemetry_manager


def initialize_telemetry(config: Optional[TelemetryConfig] = None) -> TelemetryManager:
    """Initialize global telemetry manager"""
    global _telemetry_manager
    
    _telemetry_manager = TelemetryManager(config)
    return _telemetry_manager


# Convenience decorators
def trace(name: Optional[str] = None, attributes: Optional[Dict[str, Any]] = None):
    """Convenience decorator for tracing"""
    telemetry = get_telemetry()
    return telemetry.trace_function(name, attributes)


# Example usage
if __name__ == "__main__":
    import asyncio
    
    # Initialize telemetry
    telemetry = initialize_telemetry()
    
    # Create metrics
    request_counter = telemetry.create_counter(
        name="http_requests_total",
        description="Total HTTP requests",
        unit="1"
    )
    
    request_duration = telemetry.create_histogram(
        name="http_request_duration",
        description="HTTP request duration",
        unit="ms"
    )
    
    # Use tracing
    @trace(name="process_task", attributes={"task_type": "example"})
    async def process_task(task_id: str):
        with telemetry.trace_span("database_query", {"query": "SELECT"}):
            await asyncio.sleep(0.1)
        
        with telemetry.trace_span("external_api_call", {"api": "openai"}):
            await asyncio.sleep(0.2)
        
        return f"Processed {task_id}"
    
    # Run example
    async def main():
        result = await process_task("task_123")
        print(result)
    
    asyncio.run(main())
    
    # Shutdown
    telemetry.shutdown()

