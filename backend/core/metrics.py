"""
Metrics Collection Module

This module provides metrics collection for monitoring.
"""

from typing import Dict, List
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: datetime
    value: float
    tags: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """
    Collects and aggregates application metrics.
    
    In production, integrate with Prometheus, DataDog, or similar.
    """
    
    def __init__(self):
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[MetricPoint]] = defaultdict(list)
        self._timers: Dict[str, List[float]] = defaultdict(list)
    
    def increment(self, metric: str, value: float = 1.0, tags: Dict[str, str] = None):
        """
        Increment a counter metric.
        
        Args:
            metric: Metric name
            value: Value to increment by
            tags: Optional tags
        """
        key = self._make_key(metric, tags)
        self._counters[key] += value
    
    def gauge(self, metric: str, value: float, tags: Dict[str, str] = None):
        """
        Set a gauge metric.
        
        Args:
            metric: Metric name
            value: Current value
            tags: Optional tags
        """
        key = self._make_key(metric, tags)
        self._gauges[key] = value
    
    def histogram(self, metric: str, value: float, tags: Dict[str, str] = None):
        """
        Record a histogram value.
        
        Args:
            metric: Metric name
            value: Value to record
            tags: Optional tags
        """
        key = self._make_key(metric, tags)
        point = MetricPoint(
            timestamp=datetime.utcnow(),
            value=value,
            tags=tags or {}
        )
        self._histograms[key].append(point)
        
        # Keep only last hour of data
        cutoff = datetime.utcnow() - timedelta(hours=1)
        self._histograms[key] = [
            p for p in self._histograms[key]
            if p.timestamp > cutoff
        ]
    
    def timing(self, metric: str, duration_ms: float, tags: Dict[str, str] = None):
        """
        Record a timing metric.
        
        Args:
            metric: Metric name
            duration_ms: Duration in milliseconds
            tags: Optional tags
        """
        key = self._make_key(metric, tags)
        self._timers[key].append(duration_ms)
        
        # Keep only last 1000 measurements
        if len(self._timers[key]) > 1000:
            self._timers[key] = self._timers[key][-1000:]
    
    def get_counter(self, metric: str, tags: Dict[str, str] = None) -> float:
        """Get counter value"""
        key = self._make_key(metric, tags)
        return self._counters.get(key, 0.0)
    
    def get_gauge(self, metric: str, tags: Dict[str, str] = None) -> float:
        """Get gauge value"""
        key = self._make_key(metric, tags)
        return self._gauges.get(key, 0.0)
    
    def get_histogram_stats(self, metric: str, tags: Dict[str, str] = None) -> Dict:
        """Get histogram statistics"""
        key = self._make_key(metric, tags)
        values = [p.value for p in self._histograms.get(key, [])]
        
        if not values:
            return {"count": 0}
        
        sorted_values = sorted(values)
        count = len(sorted_values)
        
        return {
            "count": count,
            "min": sorted_values[0],
            "max": sorted_values[-1],
            "mean": sum(sorted_values) / count,
            "p50": sorted_values[int(count * 0.5)],
            "p95": sorted_values[int(count * 0.95)],
            "p99": sorted_values[int(count * 0.99)]
        }
    
    def get_timing_stats(self, metric: str, tags: Dict[str, str] = None) -> Dict:
        """Get timing statistics"""
        key = self._make_key(metric, tags)
        values = self._timers.get(key, [])
        
        if not values:
            return {"count": 0}
        
        sorted_values = sorted(values)
        count = len(sorted_values)
        
        return {
            "count": count,
            "min_ms": sorted_values[0],
            "max_ms": sorted_values[-1],
            "mean_ms": sum(sorted_values) / count,
            "p50_ms": sorted_values[int(count * 0.5)],
            "p95_ms": sorted_values[int(count * 0.95)],
            "p99_ms": sorted_values[int(count * 0.99)]
        }
    
    def get_all_metrics(self) -> Dict:
        """Get all metrics"""
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histograms": {
                key: self.get_histogram_stats(key)
                for key in self._histograms.keys()
            },
            "timers": {
                key: self.get_timing_stats(key)
                for key in self._timers.keys()
            }
        }
    
    def reset(self):
        """Reset all metrics"""
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()
        self._timers.clear()
    
    @staticmethod
    def _make_key(metric: str, tags: Dict[str, str] = None) -> str:
        """Create metric key from name and tags"""
        if not tags:
            return metric
        
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{metric}[{tag_str}]"


# Global metrics collector
metrics = MetricsCollector()

