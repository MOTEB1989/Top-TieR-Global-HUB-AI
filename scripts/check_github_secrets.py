#!/usr/bin/env python3
"""
GitHub Secrets Validator
التحقق من أسرار GitHub في المستودع
"""

import os
import sys
import requests
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

# Load .env
def load_env():
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, _, value = line.partition('=')
                    if key and value:
                        os.environ[key.strip()] = value.strip()

load_env()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "MOTEB1989/Top-TieR-Global-HUB-AI")

def check_github_token() -> Tuple[bool, str]:
    """التحقق من صلاحية GitHub Token"""
    if not GITHUB_TOKEN or GITHUB_TOKEN.startswith("${{"):
        return False, "❌ GITHUB_TOKEN غير مُعدّ في .env"
    
    try:
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            return True, f"✅ مُصادق كـ: {user_data.get('login')}"
        elif response.status_code == 401:
            return False, "❌ التوكن غير صالح أو منتهي الصلاحية"
        else:
            return False, f"⚠️ خطأ: {response.status_code}"
    
    except Exception as e:
        return False, f"❌ خطأ في الاتصال: {str(e)}"

def get_repo_secrets() -> Tuple[bool, List[str], str]:
    """الحصول على قائمة الأسرار في المستودع"""
    if not GITHUB_TOKEN:
        return False, [], "GitHub Token غير موجود"
    
    try:
        owner, repo = GITHUB_REPO.split("/")
        url = f"https://api.github.com/repos/{owner}/{repo}/actions/secrets"
        
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            secrets = [secret["name"] for secret in data.get("secrets", [])]
            return True, secrets, f"تم العثور على {len(secrets)} سر"
        elif response.status_code == 404:
            return False, [], "المستودع غير موجود أو لا توجد صلاحيات"
        else:
            return False, [], f"خطأ: {response.status_code}"
    
    except Exception as e:
        return False, [], f"خطأ: {str(e)}"

def check_required_secrets() -> Dict[str, str]:
    """التحقق من الأسرار المطلوبة"""
    required_secrets = {
        "OPENAI_API_KEY": "مطلوب لـ GPT/AI",
        "GITHUB_ACCESS_TOKEN": "مطلوب للبوت والأتمتة",
        "TELEGRAM_BOT_TOKEN": "مطلوب لبوت Telegram"
    }
    
    success, secrets_list, msg = get_repo_secrets()
    
    if not success:
        return {"error": msg}
    
    results = {}
    for secret_name, description in required_secrets.items():
        if secret_name in secrets_list:
            results[secret_name] = f"✅ موجود - {description}"
        else:
            results[secret_name] = f"❌ مفقود - {description}"
    
    # إضافة أي أسرار إضافية موجودة
    extra_secrets = [s for s in secrets_list if s not in required_secrets]
    if extra_secrets:
        results["_extra"] = f"ℹ️ أسرار إضافية: {', '.join(extra_secrets)}"
    
    return results

def test_secret_usage() -> Dict[str, str]:
    """اختبار استخدام الأسرار في Workflows"""
    workflow_files = [
        ".github/workflows/ci.yml",
        ".github/workflows/cd.yml",
        ".github/workflows/telegram-bot.yml"
    ]
    
    results = {}
    
    for workflow in workflow_files:
        path = Path(workflow)
        if path.exists():
            with open(path) as f:
                content = f.read()
                
            # البحث عن استخدام الأسرار
            secrets_used = []
            if "${{ secrets." in content:
                import re
                matches = re.findall(r'\$\{\{\s*secrets\.(\w+)\s*\}\}', content)
                secrets_used = list(set(matches))
            
            if secrets_used:
                results[workflow] = f"✅ يستخدم: {', '.join(secrets_used)}"
            else:
                results[workflow] = "⚠️ لا يستخدم أسرار"
        else:
            results[workflow] = "❌ غير موجود"
    
    return results

def check_local_vs_github() -> Dict[str, str]:
    """مقارنة المفاتيح المحلية مع أسرار GitHub"""
    local_keys = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN"),
        "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN")
    }
    
    success, github_secrets, _ = get_repo_secrets()
    
    results = {}
    
    for key, value in local_keys.items():
        local_status = "✅ موجود محلياً" if value and not value.startswith("${{") else "❌ مفقود محلياً"
        
        # تحويل GITHUB_TOKEN إلى GITHUB_ACCESS_TOKEN للمقارنة
        github_key = "GITHUB_ACCESS_TOKEN" if key == "GITHUB_TOKEN" else key
        github_status = "✅ موجود في GitHub" if success and github_key in github_secrets else "❌ مفقود في GitHub"
        
        results[key] = f"{local_status} | {github_status}"
    
    return results

def main():
    """الدالة الرئيسية"""
    print("\n" + "="*70)
    print("🔐 فحص أسرار GitHub (Secrets)")
    print("="*70 + "\n")
    
    # 1. التحقق من GitHub Token
    print("1️⃣ التحقق من GitHub Token:")
    print("-" * 70)
    is_valid, msg = check_github_token()
    print(f"   {msg}\n")
    
    if not is_valid:
        print("💡 للإصلاح:")
        print("   - أضف GITHUB_TOKEN صالح في ملف .env")
        print("   - احصل على توكن من: https://github.com/settings/tokens")
        print("   - الصلاحيات المطلوبة: repo, workflow\n")
        return 1
    
    # 2. قائمة الأسرار في المستودع
    print("2️⃣ الأسرار في المستودع:")
    print("-" * 70)
    success, secrets, msg = get_repo_secrets()
    if success:
        if secrets:
            for secret in secrets:
                print(f"   ✅ {secret}")
        else:
            print("   ⚠️ لا توجد أسرار مُعرّفة")
    else:
        print(f"   {msg}")
    print()
    
    # 3. التحقق من الأسرار المطلوبة
    print("3️⃣ الأسرار المطلوبة:")
    print("-" * 70)
    required = check_required_secrets()
    if "error" in required:
        print(f"   ❌ {required['error']}")
    else:
        for secret, status in required.items():
            if not secret.startswith("_"):
                print(f"   {status}")
        if "_extra" in required:
            print(f"   {required['_extra']}")
    print()
    
    # 4. استخدام الأسرار في Workflows
    print("4️⃣ استخدام الأسرار في Workflows:")
    print("-" * 70)
    workflows = test_secret_usage()
    for workflow, status in workflows.items():
        print(f"   {status} ({workflow})")
    print()
    
    # 5. مقارنة محلي vs GitHub
    print("5️⃣ مقارنة المفاتيح المحلية مع GitHub:")
    print("-" * 70)
    comparison = check_local_vs_github()
    for key, status in comparison.items():
        print(f"   {key}:")
        print(f"      {status}")
    print()
    
    # الملخص النهائي
    print("="*70)
    print("📊 الملخص:")
    print("="*70)
    
    if success and secrets:
        missing = [k for k, v in check_required_secrets().items() 
                  if not k.startswith("_") and "❌" in v]
        
        if not missing:
            print("✅ جميع الأسرار المطلوبة موجودة!")
            print("✅ النظام جاهز للعمل على GitHub Actions")
        else:
            print(f"⚠️ {len(missing)} سر مفقود:")
            for m in missing:
                print(f"   - {m}")
            print("\n💡 لإضافة سر جديد:")
            print(f"   https://github.com/{GITHUB_REPO}/settings/secrets/actions/new")
    else:
        print("⚠️ لم يتم العثور على أسرار")
        print("💡 أضف الأسرار المطلوبة في إعدادات المستودع")
    
    print("="*70 + "\n")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ تم إيقاف الفحص")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
