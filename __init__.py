"""lexhub: وصلات بيانات ونماذج لبيئة LexCode."""

# يسمح هذا الاستيراد بالعمل حتى عند تنفيذ الوحدة كمسار مستقل (مثل بيئات الاختبار)
# حيث قد لا تكون الحزمة مثبتة بالكامل.
try:  # pragma: no cover - لا يختبر هنا
    from .providers import connect_ai, connect_dataset
except Exception:  # pragma: no cover - تظل الواجهة متاحة في البيئات المُثبَّتة
    connect_ai = None
    connect_dataset = None

__all__ = ["connect_ai", "connect_dataset"]
