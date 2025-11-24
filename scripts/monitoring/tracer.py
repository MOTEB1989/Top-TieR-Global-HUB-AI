"""
Distributed Tracing Module
Provides request tracing and correlation for distributed systems.
"""

import time
import uuid
from contextvars import ContextVar
from typing import Any, Dict, Optional


# Context variable for trace ID (thread-safe)
trace_id_var: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)


class RequestTracer:
    """
    Manages distributed request tracing.
    
    Features:
    - Unique trace IDs for request correlation
    - Span tracking for operation timing
    - Context propagation
    - Performance measurement
    """

    def __init__(self, service_name: str = "telegram-bot"):
        """
        Initialize request tracer.
        
        Args:
            service_name: Service identifier
        """
        self.service_name = service_name
        self.traces: Dict[str, Dict[str, Any]] = {}

    def start_trace(self, trace_id: Optional[str] = None, operation: str = "request") -> str:
        """
        Start a new trace or continue existing one.
        
        Args:
            trace_id: Existing trace ID or None to create new
            operation: Operation name
            
        Returns:
            Trace ID
        """
        if trace_id is None:
            trace_id = self._generate_trace_id()
        
        trace_id_var.set(trace_id)
        
        self.traces[trace_id] = {
            "trace_id": trace_id,
            "service": self.service_name,
            "operation": operation,
            "start_time": time.time(),
            "spans": [],
            "metadata": {},
        }
        
        return trace_id

    def start_span(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Start a new span within current trace.
        
        Args:
            name: Span name
            metadata: Optional span metadata
            
        Returns:
            Span ID
        """
        trace_id = trace_id_var.get()
        if not trace_id or trace_id not in self.traces:
            # Start new trace if none exists
            trace_id = self.start_trace()
        
        span_id = self._generate_span_id()
        span = {
            "span_id": span_id,
            "name": name,
            "start_time": time.time(),
            "metadata": metadata or {},
        }
        
        self.traces[trace_id]["spans"].append(span)
        return span_id

    def end_span(self, span_id: str, status: str = "success", error: Optional[str] = None):
        """
        End a span and record its duration.
        
        Args:
            span_id: Span ID to end
            status: Span status (success, error, etc.)
            error: Optional error message
        """
        trace_id = trace_id_var.get()
        if not trace_id or trace_id not in self.traces:
            return
        
        for span in self.traces[trace_id]["spans"]:
            if span["span_id"] == span_id and "end_time" not in span:
                span["end_time"] = time.time()
                span["duration_ms"] = round((span["end_time"] - span["start_time"]) * 1000, 2)
                span["status"] = status
                if error:
                    span["error"] = error
                break

    def end_trace(self, status: str = "success", metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        End current trace and return trace data.
        
        Args:
            status: Trace status
            metadata: Optional trace metadata
            
        Returns:
            Complete trace data
        """
        trace_id = trace_id_var.get()
        if not trace_id or trace_id not in self.traces:
            return {}
        
        trace = self.traces[trace_id]
        trace["end_time"] = time.time()
        trace["duration_ms"] = round((trace["end_time"] - trace["start_time"]) * 1000, 2)
        trace["status"] = status
        
        if metadata:
            trace["metadata"].update(metadata)
        
        # Clear context
        trace_id_var.set(None)
        
        return trace

    def get_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """
        Get trace data by ID.
        
        Args:
            trace_id: Trace identifier
            
        Returns:
            Trace data or None if not found
        """
        return self.traces.get(trace_id)

    def get_current_trace_id(self) -> Optional[str]:
        """
        Get current trace ID from context.
        
        Returns:
            Current trace ID or None
        """
        return trace_id_var.get()

    def add_metadata(self, key: str, value: Any):
        """
        Add metadata to current trace.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        trace_id = trace_id_var.get()
        if trace_id and trace_id in self.traces:
            self.traces[trace_id]["metadata"][key] = value

    @staticmethod
    def _generate_trace_id() -> str:
        """
        Generate unique trace ID.
        
        Returns:
            Trace ID string
        """
        return str(uuid.uuid4())

    @staticmethod
    def _generate_span_id() -> str:
        """
        Generate unique span ID.
        
        Returns:
            Span ID string
        """
        return str(uuid.uuid4())[:8]

    def cleanup_old_traces(self, max_age_seconds: int = 3600):
        """
        Remove traces older than specified age.
        
        Args:
            max_age_seconds: Maximum trace age in seconds
        """
        current_time = time.time()
        traces_to_remove = []
        
        for trace_id, trace in self.traces.items():
            if "end_time" in trace:
                age = current_time - trace["end_time"]
                if age > max_age_seconds:
                    traces_to_remove.append(trace_id)
        
        for trace_id in traces_to_remove:
            del self.traces[trace_id]

    def get_trace_summary(self) -> Dict[str, Any]:
        """
        Get summary of all traces.
        
        Returns:
            Trace statistics
        """
        total_traces = len(self.traces)
        active_traces = sum(1 for t in self.traces.values() if "end_time" not in t)
        completed_traces = total_traces - active_traces
        
        durations = [
            t["duration_ms"] for t in self.traces.values() if "duration_ms" in t
        ]
        
        return {
            "total_traces": total_traces,
            "active_traces": active_traces,
            "completed_traces": completed_traces,
            "avg_duration_ms": sum(durations) / len(durations) if durations else 0,
            "min_duration_ms": min(durations) if durations else 0,
            "max_duration_ms": max(durations) if durations else 0,
        }


# Global tracer instance
_tracer_instance: Optional[RequestTracer] = None


def get_tracer(service_name: str = "telegram-bot") -> RequestTracer:
    """
    Get or create global tracer instance.
    
    Args:
        service_name: Service identifier
        
    Returns:
        RequestTracer instance
    """
    global _tracer_instance
    if _tracer_instance is None:
        _tracer_instance = RequestTracer(service_name)
    return _tracer_instance


# Context manager for easy span tracking
class TracedSpan:
    """Context manager for automatic span tracking."""

    def __init__(self, tracer: RequestTracer, name: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize traced span context manager.
        
        Args:
            tracer: RequestTracer instance
            name: Span name
            metadata: Optional metadata
        """
        self.tracer = tracer
        self.name = name
        self.metadata = metadata
        self.span_id = None

    def __enter__(self):
        """Start span on context entry."""
        self.span_id = self.tracer.start_span(self.name, self.metadata)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End span on context exit."""
        if self.span_id:
            if exc_type:
                self.tracer.end_span(self.span_id, status="error", error=str(exc_val))
            else:
                self.tracer.end_span(self.span_id, status="success")


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def example_operation():
        """Example traced operation."""
        tracer = get_tracer("example-service")
        
        # Start trace
        trace_id = tracer.start_trace(operation="process_request")
        print(f"Started trace: {trace_id}\n")
        
        # Add metadata
        tracer.add_metadata("user_id", 123456)
        tracer.add_metadata("endpoint", "/api/chat")
        
        # Span 1: Database query
        with TracedSpan(tracer, "database_query", {"table": "users"}):
            await asyncio.sleep(0.1)  # Simulate DB query
            print("✓ Database query completed")
        
        # Span 2: API call
        with TracedSpan(tracer, "openai_api_call", {"model": "gpt-4"}):
            await asyncio.sleep(0.2)  # Simulate API call
            print("✓ OpenAI API call completed")
        
        # Span 3: Cache update
        with TracedSpan(tracer, "cache_update", {"cache": "redis"}):
            await asyncio.sleep(0.05)  # Simulate cache update
            print("✓ Cache update completed")
        
        # End trace
        trace_data = tracer.end_trace(
            status="success",
            metadata={"response_size": 1024, "cached": False},
        )
        
        print(f"\n=== Trace Complete ===")
        print(f"Trace ID: {trace_data['trace_id']}")
        print(f"Total Duration: {trace_data['duration_ms']:.2f}ms")
        print(f"Status: {trace_data['status']}")
        print(f"\nSpans ({len(trace_data['spans'])}):")
        for span in trace_data["spans"]:
            print(f"  • {span['name']}: {span['duration_ms']:.2f}ms ({span['status']})")
        
        # Summary
        print(f"\n=== Trace Summary ===")
        summary = tracer.get_trace_summary()
        for key, value in summary.items():
            print(f"  {key}: {value}")
    
    asyncio.run(example_operation())
