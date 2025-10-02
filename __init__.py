"""lexhub: وصلات بيانات ونماذج لبيئة LexCode."""

try:  # pragma: no cover - import helper for namespace/standalone usage
    from .providers import connect_ai, connect_dataset  # type: ignore
except ImportError:  # pragma: no cover
    from providers import connect_ai, connect_dataset  # type: ignore

__all__ = ["connect_ai", "connect_dataset"]
