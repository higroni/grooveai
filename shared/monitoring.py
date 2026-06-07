"""
Shared Monitoring and Metrics Infrastructure
Provides health checks, performance metrics, and monitoring utilities
"""

import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from threading import Lock
from collections import deque


@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: datetime
    value: float
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class HealthStatus:
    """Health check status"""
    status: str  # "healthy", "degraded", "unhealthy"
    message: str
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)


class MetricsCollector:
    """
    Thread-safe metrics collector for performance monitoring
    Stores time-series data with configurable retention
    """
    
    def __init__(self, retention_minutes: int = 60):
        """
        Args:
            retention_minutes: How long to keep metrics (default: 60 minutes)
        """
        self.retention_minutes = retention_minutes
        self.metrics: Dict[str, deque] = {}
        self.lock = Lock()
        self.logger = logging.getLogger(__name__)
    
    def record(self, metric_name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """
        Record a metric value
        
        Args:
            metric_name: Name of the metric (e.g., "request_duration_ms")
            value: Metric value
            labels: Optional labels for the metric (e.g., {"endpoint": "/extract"})
        """
        with self.lock:
            if metric_name not in self.metrics:
                self.metrics[metric_name] = deque(maxlen=10000)  # Max 10k points per metric
            
            point = MetricPoint(
                timestamp=datetime.utcnow(),
                value=value,
                labels=labels or {}
            )
            
            self.metrics[metric_name].append(point)
            
            # Clean old data
            self._cleanup_old_data(metric_name)
    
    def _cleanup_old_data(self, metric_name: str):
        """Remove data points older than retention period"""
        cutoff = datetime.utcnow() - timedelta(minutes=self.retention_minutes)
        
        while self.metrics[metric_name] and self.metrics[metric_name][0].timestamp < cutoff:
            self.metrics[metric_name].popleft()
    
    def get_stats(self, metric_name: str, minutes: int = 5) -> Dict[str, float]:
        """
        Get statistics for a metric over the last N minutes
        
        Args:
            metric_name: Name of the metric
            minutes: Time window in minutes (default: 5)
        
        Returns:
            Dictionary with min, max, avg, count, p50, p95, p99
        """
        with self.lock:
            if metric_name not in self.metrics:
                return {
                    "count": 0,
                    "min": 0,
                    "max": 0,
                    "avg": 0,
                    "p50": 0,
                    "p95": 0,
                    "p99": 0
                }
            
            cutoff = datetime.utcnow() - timedelta(minutes=minutes)
            values = [
                p.value for p in self.metrics[metric_name]
                if p.timestamp >= cutoff
            ]
            
            if not values:
                return {
                    "count": 0,
                    "min": 0,
                    "max": 0,
                    "avg": 0,
                    "p50": 0,
                    "p95": 0,
                    "p99": 0
                }
            
            sorted_values = sorted(values)
            count = len(sorted_values)
            
            return {
                "count": count,
                "min": sorted_values[0],
                "max": sorted_values[-1],
                "avg": sum(sorted_values) / count,
                "p50": sorted_values[int(count * 0.50)],
                "p95": sorted_values[int(count * 0.95)] if count > 1 else sorted_values[0],
                "p99": sorted_values[int(count * 0.99)] if count > 1 else sorted_values[0]
            }
    
    def get_all_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for all metrics"""
        with self.lock:
            return {
                metric_name: self.get_stats(metric_name)
                for metric_name in self.metrics.keys()
            }
    
    def clear(self):
        """Clear all metrics"""
        with self.lock:
            self.metrics.clear()


class HealthChecker:
    """
    Health check manager for service monitoring
    Tracks component health and provides aggregated status
    """
    
    def __init__(self):
        self.checks: Dict[str, HealthStatus] = {}
        self.lock = Lock()
        self.logger = logging.getLogger(__name__)
    
    def register_check(self, component: str, status: str, message: str, 
                      details: Optional[Dict[str, Any]] = None):
        """
        Register a health check result
        
        Args:
            component: Component name (e.g., "database", "classla", "cache")
            status: "healthy", "degraded", or "unhealthy"
            message: Human-readable status message
            details: Optional additional details
        """
        with self.lock:
            self.checks[component] = HealthStatus(
                status=status,
                message=message,
                timestamp=datetime.utcnow(),
                details=details or {}
            )
    
    def get_status(self, component: Optional[str] = None) -> Dict[str, Any]:
        """
        Get health status
        
        Args:
            component: Optional specific component name
        
        Returns:
            Health status dictionary
        """
        with self.lock:
            if component:
                if component not in self.checks:
                    return {
                        "status": "unknown",
                        "message": f"Component '{component}' not registered"
                    }
                
                check = self.checks[component]
                return {
                    "status": check.status,
                    "message": check.message,
                    "timestamp": check.timestamp.isoformat(),
                    "details": check.details
                }
            
            # Aggregate status for all components
            if not self.checks:
                return {
                    "status": "unknown",
                    "message": "No health checks registered",
                    "components": {}
                }
            
            # Determine overall status
            statuses = [check.status for check in self.checks.values()]
            if "unhealthy" in statuses:
                overall_status = "unhealthy"
            elif "degraded" in statuses:
                overall_status = "degraded"
            else:
                overall_status = "healthy"
            
            return {
                "status": overall_status,
                "message": f"{len(self.checks)} components checked",
                "timestamp": datetime.utcnow().isoformat(),
                "components": {
                    name: {
                        "status": check.status,
                        "message": check.message,
                        "timestamp": check.timestamp.isoformat(),
                        "details": check.details
                    }
                    for name, check in self.checks.items()
                }
            }
    
    def is_healthy(self) -> bool:
        """Check if all components are healthy"""
        with self.lock:
            return all(check.status == "healthy" for check in self.checks.values())


# Global instances (singleton pattern)
_metrics_collector: Optional[MetricsCollector] = None
_health_checker: Optional[HealthChecker] = None


def get_metrics_collector(retention_minutes: int = 60) -> MetricsCollector:
    """Get or create global metrics collector"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector(retention_minutes=retention_minutes)
    return _metrics_collector


def get_health_checker() -> HealthChecker:
    """Get or create global health checker"""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker


class PerformanceTimer:
    """
    Context manager for timing operations and recording metrics
    
    Usage:
        with PerformanceTimer("operation_name"):
            # do work
            pass
    """
    
    def __init__(self, metric_name: str, labels: Optional[Dict[str, str]] = None):
        self.metric_name = metric_name
        self.labels = labels or {}
        self.start_time = None
        self.metrics = get_metrics_collector()
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            duration_ms = (time.time() - self.start_time) * 1000
        else:
            duration_ms = 0.0
        self.metrics.record(self.metric_name, duration_ms, self.labels)
        return False


def record_request_metrics(endpoint: str, duration_ms: float, status_code: int):
    """
    Convenience function to record HTTP request metrics
    
    Args:
        endpoint: API endpoint path
        duration_ms: Request duration in milliseconds
        status_code: HTTP status code
    """
    metrics = get_metrics_collector()
    
    # Record duration
    metrics.record(
        "http_request_duration_ms",
        duration_ms,
        {"endpoint": endpoint, "status": str(status_code)}
    )
    
    # Record request count
    metrics.record(
        "http_request_count",
        1,
        {"endpoint": endpoint, "status": str(status_code)}
    )


def check_database_health(db_connection) -> HealthStatus:
    """
    Check database health
    
    Args:
        db_connection: Database connection object
    
    Returns:
        HealthStatus object
    """
    try:
        # Try a simple query
        cursor = db_connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        
        return HealthStatus(
            status="healthy",
            message="Database connection OK",
            timestamp=datetime.utcnow(),
            details={"connection": "active"}
        )
    except Exception as e:
        return HealthStatus(
            status="unhealthy",
            message=f"Database connection failed: {str(e)}",
            timestamp=datetime.utcnow(),
            details={"error": str(e)}
        )

# Made with Bob
