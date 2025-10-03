import json

# قائمة سيناريوهات Canonical
CANONICAL_SCENARIOS = {
    "aml_intl_transfer_500k_no_kyc": {
        "description": "تحويل دولي يتجاوز 500,000 ريال دون توثيق مصدر الأموال.",
        "action": "إرسال بلاغ اشتباه إلى وحدة التحريات المالية (SAFIU)",
        "risk_level": "مرتفعة",
        "citations": [
            "لائحة مكافحة غسل الأموال – المادة 16",
            "تعليمات ساما AML/CFT",
            "FATF Recommendation 16"
        ]
    },
    "kyc_missing_new_account": {
        "description": "فتح حساب جديد بدون إتمام متطلبات KYC.",
        "action": "رفض فتح الحساب ورفع STR إذا توفرت شبهة",
        "risk_level": "متوسطة",
        "citations": [
            "قواعد CMA – KYC/CDD",
            "FATF Guidance on PEPs",
            "Basel III alignment"
        ]
    }
    # يمكن التوسعة لاحقًا
}

def run_compliance(input: dict) -> dict:
    """
    واجهة تنفيذ موحدة لتحليل سيناريو امتثال.
    المدخل: {"test_case": "aml_intl_transfer_500k_no_kyc"}
    الناتج: توصية تشغيلية موثقة.
    """
    test_case = input.get("test_case")
    
    if not test_case:
        return {
            "status": "error",
            "message": "يرجى إدخال test_case"
        }
    
    scenario = CANONICAL_SCENARIOS.get(test_case)
    
    if not scenario:
        return {
            "status": "not_found",
            "message": f"السيناريو '{test_case}' غير موجود في مكتبة Canonical.",
            "available_scenarios": list(CANONICAL_SCENARIOS.keys())
        }
    
    return {
        "status": "success",
        "test_case": test_case,
        "description": scenario["description"],
        "recommended_action": scenario["action"],
        "risk_level": scenario["risk_level"],
        "citations": scenario["citations"]
    }


# ✅ تنفيذ محلي لأغراض اختبار (اختياري)
if __name__ == "__main__":
    example_input = {"test_case": "aml_intl_transfer_500k_no_kyc"}
    result = run_compliance(example_input)
    print(json.dumps(result, ensure_ascii=False, indent=2))
