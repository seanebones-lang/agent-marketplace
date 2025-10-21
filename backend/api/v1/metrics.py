"""
Metrics API Endpoints
Exposes Prometheus metrics and health checks
"""

from fastapi import APIRouter, Response
from fastapi.responses import PlainTextResponse

from core.metrics import get_metrics, get_metrics_content_type
from core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("", response_class=PlainTextResponse)
async def prometheus_metrics():
    """
    Prometheus metrics endpoint.
    
    Returns metrics in Prometheus text format for scraping.
    
    Example metrics:
    - http_requests_total
    - agent_executions_total
    - rate_limit_hits_total
    - circuit_breaker_state
    - db_query_duration_seconds
    
    Usage:
        curl http://localhost:8000/api/v1/metrics
    """
    try:
        metrics_data = get_metrics()
        return Response(
            content=metrics_data,
            media_type=get_metrics_content_type()
        )
    except Exception as e:
        logger.error(f"Failed to generate metrics: {e}", exc_info=True)
        return Response(
            content=f"# Error generating metrics: {str(e)}",
            media_type="text/plain"
        )

