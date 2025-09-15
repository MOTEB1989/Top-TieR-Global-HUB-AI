# Safety Belt: Post-merge Validation (Readonly)

هدف الملف `.github/workflows/post-merge-validation.yml`:
- تشغيل فحوص قراءة فقط بعد كل دمج إلى `main`.
- التأكد من صحة الأسرار واتصال OpenAI ونجاح `scripts/safe_smoke.sh`.
- بدون أي كتابة على قواعد البيانات أو الخدمات (dry-run/SAFE_MODE).

## متطلبات
- إعداد Secrets:
  - `OPENAI_API_KEY`
  - `NEO4J_USER`, `NEO4J_PASS`
  - (اختياري) `SLACK_WEBHOOK_URL`
- وجود `scripts/safe_smoke.sh` (مضاف ضمن حزام الأمان).

## تفعيل حماية الفرع (Branch Protection)
1) Settings → Branches → Branch protection rules → `main`.
2) فعّل:
   - Require status checks to pass before merging.
3) اختر كحد أدنى:
   - `Safe Readonly Check`
   - `Post-merge Validation (Readonly)`
   - (إن وجد) `CI`, `CodeQL`.

> ملاحظة: تفعيل الحماية يتم من واجهة GitHub فقط (ليس عبر PR).

## تشغيل يدويًا
من تبويب Actions:
- شغّل `Post-merge Validation (Readonly)` يدويًا عبر `workflow_dispatch`.
- راجع `post-merge-smoke` artifact في حال الفشل لمعرفة السبب.

## نشر PDB (اختياري)
```
kubectl apply -f k8s/pdb.yaml
```

## تشغيل فحص محلي
```
CORE_URL=http://localhost:8080 \
OSINT_URL=http://localhost:8081 \
NEO4J_HTTP=http://localhost:7474 \
NEO4J_USER=neo4j NEO4J_PASS=test1234 \
./scripts/safe_smoke.sh
```