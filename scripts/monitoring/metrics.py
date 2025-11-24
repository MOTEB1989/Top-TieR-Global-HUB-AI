"""
Metrics Collection Module
Provides Prometheus-compatible metrics collection and exposition.
"""

import time
from collections import defaultdict
from typing import Dict, List, Optional


class MetricsCollector:
    """
    Collects and manages application metrics.
    
    Supports:
    - Counters (monotonically increasing)
    - Gauges (can increase or decrease)
    - Histograms (distributions)
    - Summaries (percentiles)
    """

    def __init__(self, namespace: str = "telegram_bot"):
        """
        Initialize metrics collector.
        
        Args:
            namespace: Metric namespace prefix
        """
        self.namespace = namespace
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.start_time = time.time()

    def increment_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None):
        """
        Increment a counter metric.
        
        Args:
            name: Metric name
            value: Increment value
            labels: Optional metric labels
        """
        metric_key = self._build_key(name, labels)
        self.counters[metric_key] += value

    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """
        Set a gauge metric value.
        
        Args:
            name: Metric name
            value: Gauge value
            labels: Optional metric labels
        """
        metric_key = self._build_key(name, labels)
        self.gauges[metric_key] = value

    def observe_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """
        Record a histogram observation.
        
        Args:
            name: Metric name
            value: Observed value
            labels: Optional metric labels
        """
        metric_key = self._build_key(name, labels)
        self.histograms[metric_key].append(value)

    def _build_key(self, name: str, labels: Optional[Dict[str, str]] = None) -> str:
        """
        Build metric key with labels.
        
        Args:
            name: Metric name
            labels: Optional labels
            
        Returns:
            Formatted metric key
        """
        full_name = f"{self.namespace}_{name}"
        if labels:
            label_str = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
            return f"{full_name}{{{label_str}}}"
        return full_name

    def get_metrics(self) -> Dict[str, any]:
        """
        Get all collected metrics.
        
        Returns:
            Dictionary of all metrics
        """
        return {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "histograms": {
                name: {
                    "count": len(values),
                    "sum": sum(values),
                    "min": min(values) if values else 0,
                    "max": max(values) if values else 0,
                    "avg": sum(values) / len(values) if values else 0,
                }
                for name, values in self.histograms.items()
            },
        }

    def reset(self):
        """Reset all metrics."""
        self.counters.clear()
        self.gauges.clear()
        self.histograms.clear()


class PrometheusMetrics:
    """
    Prometheus-compatible metrics exporter.
    """

    def __init__(self, collector: MetricsCollector):
        """
        Initialize Prometheus metrics exporter.
        
        Args:
            collector: MetricsCollector instance
        """
        self.collector = collector

    def export(self) -> str:
        """
        Export metrics in Prometheus text format.
        
        Returns:
            Prometheus-formatted metrics string
        """
        lines = []
        
        # Export counters
        for name, value in self.collector.counters.items():
            lines.append(f"# TYPE {name} counter")
            lines.append(f"{name} {value}")
        
        # Export gauges
        for name, value in self.collector.gauges.items():
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {value}")
        
        # Export histograms
        for name, values in self.collector.histograms.items():
            if values:
                lines.append(f"# TYPE {name} histogram")
                lines.append(f"{name}_count {len(values)}")
                lines.append(f"{name}_sum {sum(values)}")
                
                # Calculate buckets
                buckets = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]
                for bucket in buckets:
                    count = sum(1 for v in values if v <= bucket)
                    lines.append(f'{name}_bucket{{le="{bucket}"}} {count}')
                lines.append(f'{name}_bucket{{le="+Inf"}} {len(values)}')
        
        # Add uptime
        uptime = time.time() - self.collector.start_time
        lines.append(f"# TYPE {self.collector.namespace}_uptime_seconds gauge")
        lines.append(f"{self.collector.namespace}_uptime_seconds {uptime}")
        
        return "\n".join(lines) + "\n"


# Global metrics instance
_metrics_instance: Optional[MetricsCollector] = None


def get_metrics(namespace: str = "telegram_bot") -> MetricsCollector:
    """
    Get or create global metrics collector.
    
    Args:
        namespace: Metric namespace
        
    Returns:
        MetricsCollector instance
    """
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = MetricsCollector(namespace)
    return _metrics_instance


# Example usage
if __name__ == "__main__":
    # Create metrics collector
    metrics = get_metrics("telegram_bot")
    
    # Record some metrics
    metrics.increment_counter("requests_total", labels={"method": "POST", "endpoint": "/chat"})
    metrics.increment_counter("requests_total", labels={"method": "GET", "endpoint": "/status"})
    metrics.increment_counter("requests_total", 5, labels={"method": "POST", "endpoint": "/chat"})
    
    metrics.set_gauge("active_users", 42)
    metrics.set_gauge("queue_size", 15)
    
    # Simulate response times
    for _ in range(10):
        metrics.observe_histogram("request_duration_seconds", 0.123)
        metrics.observe_histogram("request_duration_seconds", 0.456)
        metrics.observe_histogram("request_duration_seconds", 0.789)
    
    # Get metrics summary
    print("=== Metrics Summary ===\n")
    summary = metrics.get_metrics()
    
    print("Counters:")
    for name, value in summary["counters"].items():
        print(f"  {name}: {value}")
    
    print("\nGauges:")
    for name, value in summary["gauges"].items():
        print(f"  {name}: {value}")
    
    print("\nHistograms:")
    for name, stats in summary["histograms"].items():
        print(f"  {name}:")
        print(f"    Count: {stats['count']}")
        print(f"    Sum: {stats['sum']:.3f}")
        print(f"    Min: {stats['min']:.3f}")
        print(f"    Max: {stats['max']:.3f}")
        print(f"    Avg: {stats['avg']:.3f}")
    
    # Export in Prometheus format
    print("\n=== Prometheus Export ===\n")
    prometheus = PrometheusMetrics(metrics)
    print(prometheus.export())
