-- ==========================
-- إنشاء الجداول
-- ==========================
CREATE TABLE IF NOT EXISTS circulars (
    id TEXT PRIMARY KEY,
    title TEXT,
    language TEXT,
    status TEXT,
    scope TEXT,
    regulator TEXT,
    jurisdiction TEXT,
    source_url TEXT,
    ingested_at TEXT
);

CREATE TABLE IF NOT EXISTS decision_rules (
    rule_id TEXT PRIMARY KEY,
    description TEXT,
    conditions TEXT,
    action TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS alerts_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    urgency TEXT,
    target TEXT
);

CREATE TABLE IF NOT EXISTS kyc_data (
    customer_id TEXT PRIMARY KEY,
    source_of_funds BOOLEAN
);

-- ==========================
-- بيانات اختبارية
-- ==========================

-- تعميم من ساما (مثال)
INSERT OR IGNORE INTO circulars (
    id, title, language, status, scope, regulator, jurisdiction, source_url, ingested_at
) VALUES (
    '8b9ea0863b891bd5ff71588dfffcdefb892a0333',
    'تعليمات البنوك ذات الأهمية النظامية المحلية (D-SIBs) 2024',
    'ar', 'In-Force', 'Banking Sector',
    'SAMA', 'KSA',
    'https://www.sama.gov.sa/sites/InternalResources/CircularsRepository/GDBC-450565080000-024H.pdf',
    '2025-09-19T12:53:07Z'
);

-- قاعدة قرار AML (تحويل دولي أكبر من 500k بدون توثيق مصدر الأموال)
INSERT OR IGNORE INTO decision_rules (
    rule_id, description, conditions, action, metadata
) VALUES (
    'aml_intl_transfer_500k_no_kyc',
    'تحويل دولي يتجاوز 500,000 ريال دون توثيق مصدر الأموال في KYC',
    '{"transaction.type": "international_transfer", "transaction.amount": ">500000", "kyc.source_of_funds": false}',
    '{"type": "report", "target": "SAFIU", "urgency": "immediate", "notes": "إرسال بلاغ اشتباه إلى وحدة التحريات المالية وفق لائحة مكافحة غسل الأموال – المادة 16 وتعليمات ساما."}',
    '{"source": "لائحة مكافحة غسل الأموال – المادة 16", "jurisdiction": "KSA", "regulator": "SAMA", "last_update": "2021-07-15", "compliance_domain": "AML/CFT"}'
);

-- عميل للاختبار
INSERT OR IGNORE INTO kyc_data (
    customer_id, source_of_funds
) VALUES (
    'cust123', 0
);
