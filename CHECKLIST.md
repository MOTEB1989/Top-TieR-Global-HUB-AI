# ✅ OSINT System – Checklist للتأكد من التفعيل

## 1) الأساسيات (Core)
- [ ] Smart Query Engine: تحويل الاستعلامات إلى صيغ قانونية قابلة للتنفيذ.
- [ ] NLP Rewriter ثنائي اللغة (AR/EN) مفعل.
- [ ] Confidence Model (v0.1) مفعل بحسابات الوزن/الحداثة/العدد/الاتساق.

## 2) الموصلات (Connectors)
- [ ] Phones: Truecaller / NumLookup / EveryCaller تُرجع نتائج.
- [ ] Emails: HIBP / Hunter.io / Email Hippo تعمل.
- [ ] Usernames: Sherlock / WhatsMyName / Namechk تعمل.
- [ ] Images: Yandex / Bing Visual / Vision API تعمل.
- [ ] Leaks: IntelX / DeHashed مفعلتان بمفاتيح صحيحة.
- [ ] Domains/IP: WhoisXML / SecurityTrails / Shodan تعمل.
- [ ] Social: Twint / Telepathy (Telegram) تعمل بدون حظر.
- [ ] Dark Web: Ahmia / DarkSearch.io تُرجع نتائج.

## 3) قاعدة البيانات البيانية (Graph DB)
- [ ] Neo4j قيد التشغيل (bolt://localhost:7687 و http://localhost:7474).
- [ ] Schema (Person, Phone, Email, Username, Image, Domain, IP) مطبق.
- [ ] ETL/Upsert يحدّث الحقول: `first_seen`, `last_seen`, `confidence`.

## 4) التحليل المتقدم
- [ ] Temporal: حقول `valid_from`/`valid_to` تُملأ.
- [ ] Behavioral: stylometry + pHash للصور مفعلان.
- [ ] Entity Resolution: قواعد دمج + عتبات ضبط.
- [ ] Confidence Model: معاير، ويظهر في التقارير.

## 5) الواجهة (UI/UX)
- [ ] FastAPI/Django يرد على `GET /` (حالة 200).
- [ ] Graph Viz (Cytoscape.js/Bloom) يعمل.
- [ ] Timeline View يعمل على مجموعة بيانات مثال.
- [ ] Export PDF/CSV/GraphML مع تضمين Audit Trail.

## 6) الحوكمة والأمان
- [ ] policy.yaml مفعل ويظهر التنبيه القانوني قبل البحث.
- [ ] Audit Log يسجل (من/متى/ماذا/نتائج مختصرة).
- [ ] RBAC (مشرف/محقق/مشاهِد) مطبق.
- [ ] التشفير أثناء النقل (HTTPS) وأثناء التخزين مفعّل.
- [ ] Anti-blocking: VPN/Proxy/Tor مدمجة مع Health Checks.

---

### نتائج آخر فحص
> سيتم ملء هذا القسم تلقائيًا من `scripts/self_check.py`.

- تاريخ الفحص: _
- الحالة العامة: _
- الملخص: _