#!/usr/bin/env python3
"""
diagnose_telegram_bot.py

سكربت تشخيصي شامل لفحص جميع متطلبات تشغيل بوت Telegram:
- فحص المتغيرات البيئية المطلوبة
- اختبار الاتصال بـ OpenAI API
- اختبار الاتصال بـ Telegram Bot API
- التحقق من ملفات المستودع الحرجة
- عرض تقرير شامل بحالة النظام

الاستخدام:
    export TELEGRAM_BOT_TOKEN=your_token
    export OPENAI_API_KEY=your_key
    export OPENAI_MODEL=gpt-4o-mini
    python3 scripts/diagnose_telegram_bot.py
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime

# Try to import required libraries
try:
    import requests
except ImportError:
    print("❌ مكتبة requests غير مثبتة. قم بتثبيتها: pip install requests")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  مكتبة python-dotenv غير مثبتة. سيتم تجاهل ملف .env")


# ============================================================================
# Constants and Configuration
# ============================================================================

REQUIRED_ENV_VARS = [
    "TELEGRAM_BOT_TOKEN",
    "OPENAI_API_KEY",
    "OPENAI_MODEL",
    "GITHUB_REPO",
]

OPTIONAL_ENV_VARS = [
    "TELEGRAM_ALLOWLIST",
    "OPENAI_BASE_URL",
]

CRITICAL_FILES = [
    "scripts/telegram_chatgpt_mode.py",
    "scripts/verify_env.py",
    "requirements.txt",
    ".env.example",
]

# ============================================================================
# Color Output (for better terminal display)
# ============================================================================

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text: str) -> None:
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}\n")


def print_success(text: str) -> None:
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_error(text: str) -> None:
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_warning(text: str) -> None:
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def print_info(text: str) -> None:
    """Print info message"""
    print(f"ℹ️  {text}")


# ============================================================================
# Diagnostic Functions
# ============================================================================

def mask_value(value: str, key: str) -> str:
    """Mask sensitive values for safe display"""
    if key.endswith("_TOKEN") or key.endswith("_KEY"):
        if len(value) > 10:
            return f"{value[:6]}...{value[-4:]}"
        return "***MASKED***"
    return value


def check_environment_variables() -> Tuple[bool, Dict[str, Any]]:
    """
    Check if all required environment variables are set
    
    Returns:
        Tuple of (all_ok: bool, report: dict)
    """
    print_header("فحص المتغيرات البيئية")
    
    report = {
        "required": {},
        "optional": {},
        "missing": [],
        "empty": [],
    }
    
    all_ok = True
    
    # Check required variables
    for var in REQUIRED_ENV_VARS:
        value = os.getenv(var)
        if value is None:
            print_error(f"{var}: غير موجود")
            report["missing"].append(var)
            all_ok = False
        elif value.strip() == "":
            print_error(f"{var}: فارغ")
            report["empty"].append(var)
            all_ok = False
        else:
            masked = mask_value(value, var)
            print_success(f"{var}: {masked}")
            report["required"][var] = masked
    
    # Check optional variables
    print()
    for var in OPTIONAL_ENV_VARS:
        value = os.getenv(var)
        if value and value.strip():
            masked = mask_value(value, var)
            print_info(f"{var}: {masked}")
            report["optional"][var] = masked
        else:
            print_warning(f"{var}: غير مضبوط (اختياري)")
            report["optional"][var] = None
    
    return all_ok, report


def check_openai_connection() -> Tuple[bool, Dict[str, Any]]:
    """
    Test connection to OpenAI API
    
    Returns:
        Tuple of (success: bool, report: dict)
    """
    print_header("اختبار الاتصال بـ OpenAI API")
    
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    report = {
        "status": "unknown",
        "model": model,
        "base_url": base_url,
        "error": None,
    }
    
    if not api_key:
        print_error("OPENAI_API_KEY غير موجود")
        report["status"] = "missing_key"
        return False, report
    
    try:
        # Test with a simple API call
        url = f"{base_url.rstrip('/')}/models"
        headers = {
            "Authorization": f"Bearer {api_key}",
        }
        
        print_info(f"جاري الاتصال بـ: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            models = data.get("data", [])
            model_ids = [m.get("id") for m in models[:5]]
            
            print_success(f"الاتصال ناجح! عدد النماذج المتاحة: {len(models)}")
            print_info(f"بعض النماذج المتاحة: {', '.join(model_ids)}")
            
            # Check if the specified model exists
            if any(model == m.get("id") for m in models):
                print_success(f"النموذج المطلوب '{model}' متاح ✓")
            else:
                print_warning(f"النموذج المطلوب '{model}' غير موجود في القائمة")
            
            report["status"] = "success"
            report["available_models"] = model_ids
            return True, report
        else:
            print_error(f"فشل الاتصال - رمز الحالة: {response.status_code}")
            print_error(f"الرسالة: {response.text[:200]}")
            report["status"] = "failed"
            report["error"] = f"HTTP {response.status_code}: {response.text[:200]}"
            return False, report
            
    except requests.exceptions.Timeout:
        print_error("انتهت مهلة الاتصال (timeout)")
        report["status"] = "timeout"
        report["error"] = "Connection timeout"
        return False, report
    except requests.exceptions.RequestException as e:
        print_error(f"خطأ في الاتصال: {str(e)}")
        report["status"] = "error"
        report["error"] = str(e)
        return False, report
    except Exception as e:
        print_error(f"خطأ غير متوقع: {str(e)}")
        report["status"] = "error"
        report["error"] = str(e)
        return False, report


def check_telegram_connection() -> Tuple[bool, Dict[str, Any]]:
    """
    Test connection to Telegram Bot API
    
    Returns:
        Tuple of (success: bool, report: dict)
    """
    print_header("اختبار الاتصال بـ Telegram Bot API")
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    report = {
        "status": "unknown",
        "bot_info": None,
        "error": None,
    }
    
    if not bot_token:
        print_error("TELEGRAM_BOT_TOKEN غير موجود")
        report["status"] = "missing_token"
        return False, report
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        
        print_info(f"جاري الاتصال بـ Telegram Bot API...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("ok"):
                bot_info = data.get("result", {})
                bot_username = bot_info.get("username", "N/A")
                bot_name = bot_info.get("first_name", "N/A")
                bot_id = bot_info.get("id", "N/A")
                
                print_success(f"الاتصال ناجح!")
                print_info(f"اسم البوت: {bot_name}")
                print_info(f"معرف البوت: @{bot_username}")
                print_info(f"Bot ID: {bot_id}")
                
                report["status"] = "success"
                report["bot_info"] = {
                    "username": bot_username,
                    "name": bot_name,
                    "id": bot_id,
                }
                return True, report
            else:
                print_error(f"فشل الاتصال: {data.get('description', 'Unknown error')}")
                report["status"] = "failed"
                report["error"] = data.get("description", "Unknown error")
                return False, report
        else:
            print_error(f"فشل الاتصال - رمز الحالة: {response.status_code}")
            report["status"] = "failed"
            report["error"] = f"HTTP {response.status_code}"
            return False, report
            
    except requests.exceptions.Timeout:
        print_error("انتهت مهلة الاتصال (timeout)")
        report["status"] = "timeout"
        report["error"] = "Connection timeout"
        return False, report
    except requests.exceptions.RequestException as e:
        print_error(f"خطأ في الاتصال: {str(e)}")
        report["status"] = "error"
        report["error"] = str(e)
        return False, report
    except Exception as e:
        print_error(f"خطأ غير متوقع: {str(e)}")
        report["status"] = "error"
        report["error"] = str(e)
        return False, report


def check_critical_files() -> Tuple[bool, Dict[str, Any]]:
    """
    Check if critical repository files exist
    
    Returns:
        Tuple of (all_exist: bool, report: dict)
    """
    print_header("فحص الملفات الحرجة")
    
    report = {
        "existing": [],
        "missing": [],
    }
    
    all_exist = True
    
    for file_path in CRITICAL_FILES:
        path = Path(file_path)
        if path.exists():
            print_success(f"{file_path}")
            report["existing"].append(file_path)
        else:
            print_error(f"{file_path} - غير موجود")
            report["missing"].append(file_path)
            all_exist = False
    
    return all_exist, report


def check_python_dependencies() -> Tuple[bool, Dict[str, Any]]:
    """
    Check if critical Python packages are installed
    
    Returns:
        Tuple of (all_installed: bool, report: dict)
    """
    print_header("فحص المكتبات المطلوبة")
    
    required_packages = [
        ("requests", "requests"),
        ("telegram", "python-telegram-bot"),
        ("dotenv", "python-dotenv"),
    ]
    
    report = {
        "installed": [],
        "missing": [],
    }
    
    all_installed = True
    
    for module_name, package_name in required_packages:
        try:
            __import__(module_name)
            print_success(f"{package_name}")
            report["installed"].append(package_name)
        except ImportError:
            print_error(f"{package_name} - غير مثبت")
            report["missing"].append(package_name)
            all_installed = False
    
    if not all_installed:
        print()
        print_warning("لتثبيت المكتبات المفقودة، قم بتشغيل:")
        print_info("pip install -r requirements.txt")
    
    return all_installed, report


# ============================================================================
# Main Diagnostic Report
# ============================================================================

def generate_summary_report(results: Dict[str, Any]) -> str:
    """Generate a summary report of all diagnostic checks"""
    
    report_lines = [
        "",
        "=" * 70,
        "التقرير النهائي - Telegram Bot Diagnostic Report".center(70),
        "=" * 70,
        "",
        f"⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"📁 المستودع: {os.getenv('GITHUB_REPO', 'N/A')}",
        "",
        "نتائج الفحص:",
        "-" * 70,
    ]
    
    # Overall status
    all_passed = all(results.values())
    
    for check_name, passed in results.items():
        status = "✅ نجح" if passed else "❌ فشل"
        report_lines.append(f"{status}  {check_name}")
    
    report_lines.extend([
        "-" * 70,
        "",
    ])
    
    if all_passed:
        report_lines.extend([
            f"{Colors.GREEN}{Colors.BOLD}",
            "🎉 جميع الفحوصات نجحت!",
            "البوت جاهز للتشغيل على Railway.",
            f"{Colors.END}",
        ])
    else:
        report_lines.extend([
            f"{Colors.RED}{Colors.BOLD}",
            "⚠️  بعض الفحوصات فشلت!",
            "الرجاء مراجعة الأخطاء أعلاه وإصلاحها قبل النشر.",
            f"{Colors.END}",
        ])
    
    report_lines.extend([
        "",
        "=" * 70,
        "",
    ])
    
    return "\n".join(report_lines)


def save_json_report(data: Dict[str, Any], filename: str = "diagnostic_report.json") -> None:
    """Save diagnostic report as JSON file"""
    try:
        report_dir = Path("analysis")
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = report_dir / filename
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print_success(f"تم حفظ التقرير في: {report_path}")
    except Exception as e:
        print_error(f"فشل حفظ التقرير: {str(e)}")


def main() -> int:
    """Main diagnostic function"""
    
    print(f"\n{Colors.BOLD}{'=' * 70}")
    print(f"🔍 Telegram Bot Diagnostic Tool - أداة تشخيص بوت Telegram".center(70))
    print(f"{'=' * 70}{Colors.END}\n")
    
    # Run all diagnostic checks
    results = {}
    full_report = {
        "timestamp": datetime.now().isoformat(),
        "repository": os.getenv("GITHUB_REPO", "N/A"),
        "checks": {},
    }
    
    # 1. Environment Variables
    env_ok, env_report = check_environment_variables()
    results["المتغيرات البيئية"] = env_ok
    full_report["checks"]["environment_variables"] = {
        "passed": env_ok,
        "details": env_report,
    }
    
    # 2. Critical Files
    files_ok, files_report = check_critical_files()
    results["الملفات الحرجة"] = files_ok
    full_report["checks"]["critical_files"] = {
        "passed": files_ok,
        "details": files_report,
    }
    
    # 3. Python Dependencies
    deps_ok, deps_report = check_python_dependencies()
    results["المكتبات المطلوبة"] = deps_ok
    full_report["checks"]["python_dependencies"] = {
        "passed": deps_ok,
        "details": deps_report,
    }
    
    # 4. OpenAI Connection (only if env vars are OK)
    if env_ok and deps_ok:
        openai_ok, openai_report = check_openai_connection()
        results["اتصال OpenAI"] = openai_ok
        full_report["checks"]["openai_connection"] = {
            "passed": openai_ok,
            "details": openai_report,
        }
    else:
        print_header("اختبار الاتصال بـ OpenAI API")
        print_warning("تم تخطي الفحص بسبب فشل فحوصات سابقة")
        results["اتصال OpenAI"] = False
        full_report["checks"]["openai_connection"] = {
            "passed": False,
            "details": {"status": "skipped"},
        }
    
    # 5. Telegram Connection (only if env vars are OK)
    if env_ok and deps_ok:
        telegram_ok, telegram_report = check_telegram_connection()
        results["اتصال Telegram"] = telegram_ok
        full_report["checks"]["telegram_connection"] = {
            "passed": telegram_ok,
            "details": telegram_report,
        }
    else:
        print_header("اختبار الاتصال بـ Telegram Bot API")
        print_warning("تم تخطي الفحص بسبب فشل فحوصات سابقة")
        results["اتصال Telegram"] = False
        full_report["checks"]["telegram_connection"] = {
            "passed": False,
            "details": {"status": "skipped"},
        }
    
    # Generate and display summary
    summary = generate_summary_report(results)
    print(summary)
    
    # Save JSON report
    full_report["overall_status"] = "passed" if all(results.values()) else "failed"
    save_json_report(full_report)
    
    # Return exit code (0 = success, 1 = failure)
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  تم إيقاف الفحص بواسطة المستخدم{Colors.END}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}❌ خطأ فادح: {str(e)}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
