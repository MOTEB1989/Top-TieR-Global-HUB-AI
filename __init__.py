"""lexhub: وصلات بيانات ونماذج لبيئة LexCode."""

try:  # pragma: no cover - import shim
    from .providers import connect_ai, connect_dataset
except Exception:  # pragma: no cover - fallback when package context missing
    from providers import connect_ai, connect_dataset

__all__ = ["connect_ai", "connect_dataset"]
