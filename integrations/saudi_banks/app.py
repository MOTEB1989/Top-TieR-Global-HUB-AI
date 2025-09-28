from flask import Flask, request, jsonify
import sqlite3, json
from datetime import datetime

# ===============================
# إعداد التطبيق
# ===============================
app = Flask(__name__)
DB_PATH = "saudi_banks.db"
LOG_FILE = "ai_training.log"
_suggested_rules = []


# ===============================
# أدوات مساعدة
# ===============================
def log_event(message: str):
    """تسجيل الأحداث في ملف log"""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{{datetime.now()}}] {{message}}\n")


# ===============================
# Health Check
# ===============================
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "running", "message": "Saudi Banks API is live ✅"}), 200


# ===============================
# Customer KYC
# ===============================
@app.route('/customer/<customer_id>', methods=['GET'])
def get_customer_kyc(customer_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT source_of_funds FROM kyc_data WHERE customer_id = ?", (customer_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify({
            "customer_id": customer_id,
            "kyc": {"source_of_funds": bool(row[0])}
        })
    else:
        return jsonify({"error": "Customer not found"}), 404


# ===============================
# Decision Rules
# ===============================
@app.route('/decision-rule', methods=['POST'])
def add_decision_rule():
    rule = request.json
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO decision_rules (rule_id, description, conditions, action, metadata)
    VALUES (?, ?, ?, ?, ?)
    """, (
        rule["rule_id"],
        rule["description"],
        json.dumps(rule["conditions"], ensure_ascii=False),
        json.dumps(rule["action"], ensure_ascii=False),
        json.dumps(rule["metadata"], ensure_ascii=False)
    ))
    conn.commit()
    conn.close()
    return jsonify({"message": "Rule added successfully ✅"})


# ===============================
# Transaction Evaluation
# ===============================
@app.route('/transaction', methods=['POST'])
def evaluate_transaction():
    txn = request.json
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT rule_id, conditions, action FROM decision_rules")
    rules = cursor.fetchall()
    alerts = []

    for rule_id, cond_str, act_str in rules:
        conditions = json.loads(cond_str)
        action = json.loads(act_str)

        match = True
        for key, value in conditions.items():
            keys = key.split(".")
            v = txn
            for k in keys:
                if isinstance(v, dict):
                    v = v.get(k, None)
                else:
                    v = None
                if v is None:
                    break

            if isinstance(value, str) and value.startswith(">") and isinstance(v, (int, float)):
                threshold = float(value[1:])
                if not v > threshold:
                    match = False
            elif value is False and v is not False:
                match = False
            elif value is True and v is not True:
                match = False
            elif v != value:
                match = False

        if match:
            cursor.execute("""
            INSERT INTO alerts_log (rule_id, notes, urgency, target)
            VALUES (?, ?, ?, ?)
            """, (
                rule_id,
                action.get("notes", ""),
                action.get("urgency", "medium"),
                action.get("target", "compliance")
            ))
            alerts.append(rule_id)

    conn.commit()
    conn.close()
    return jsonify({"matched_rules": alerts})


# ===============================
# Alerts
# ===============================
@app.route('/alerts', methods=['GET'])
def get_alerts():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM alerts_log ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    alerts = [{
        "id": r[0], "rule_id": r[1], "timestamp": r[2],
        "notes": r[3], "urgency": r[4], "target": r[5]
    } for r in rows]
    return jsonify(alerts)


# ===============================
# AI: Analyze Transactions
# ===============================
@app.route('/ai/analyze', methods=['POST'])
def ai_analyze():
    data = request.json
    transactions = data.get("transactions", [])
    if not transactions:
        return jsonify({"status": "error", "message": "No transactions provided"}), 400

    amounts = [t.get("transaction", {}).get("amount", 0) for t in transactions]

    anomalies_detected = False
    suggested_rule = None

    try:
        # Isolation Forest (يتطلب scikit-learn مثبتة)
        from sklearn.ensemble import IsolationForest
        import numpy as np
        X = np.array(amounts).reshape(-1, 1)
        model = IsolationForest(contamination=0.1, random_state=42)
        preds = model.fit_predict(X)
        if -1 in preds:
            anomalies_detected = True
            suggested_rule = {
                "rule_id": "anomaly_cash_001",
                "description": "اكتشاف نمط شاذ في المعاملات",
                "conditions": {"transaction.amount": ">100000"},
                "action": {"type": "report", "target": "compliance", "urgency": "high"}
            }
            _suggested_rules.append(suggested_rule)
    except Exception:
        # fallback: threshold-based
        if any(a > 100000 for a in amounts):
            anomalies_detected = True
            suggested_rule = {
                "rule_id": "threshold_cash_001",
                "description": "مبلغ كبير غير عادي",
                "conditions": {"transaction.amount": ">100000"},
                "action": {"type": "report", "target": "compliance", "urgency": "medium"}
            }
            _suggested_rules.append(suggested_rule)

    log_event(f"Analyzed {{len(transactions)}} transactions | anomalies={{anomalies_detected}}")
    return jsonify({
        "status": "ok",
        "anomalies_detected": anomalies_detected,
        "suggested_rule": suggested_rule
    })


# ===============================
# AI: Suggest Rules
# ===============================
@app.route('/ai/suggest-rules', methods=['GET'])
def ai_suggest_rules():
    return jsonify(_suggested_rules)


# ===============================
# تشغيل التطبيق
# ===============================
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5005)
