import yaml
from pathlib import Path

def test_policy_load_and_domains():
    policy_path = Path("tests/policy/policy.yaml")
    assert policy_path.exists(), "❌ ملف policy.yaml غير موجود"
    
    with open(policy_path, "r", encoding="utf-8") as f:
        policy = yaml.safe_load(f)

    # تحقق من وجود المفاتيح الأساسية
    assert "global" in policy, "❌ لم يتم تعريف global في policy"
    assert "domains" in policy, "❌ لم يتم تعريف domains في policy"

    # تحقق من بعض التخصصات
    for domain in ["law", "medicine", "finance"]:
        assert domain in policy["domains"], f"❌ لا يوجد {domain} في policy"
        d = policy["domains"][domain]
        assert "allowed_sources" in d, f"❌ {domain} بدون allowed_sources"
        assert "banned_actions" in d, f"❌ {domain} بدون banned_actions"
        assert "domain_disclaimer_ar" in d, f"❌ {domain} بدون disclaimer"
    
    print("✅ policy.yaml محمّل بشكل صحيح ويحتوي جميع التخصصات الأساسية")
