"""
Test bot_diagnostics module for Telegram bot diagnostic commands.
"""
from pathlib import Path


def test_bot_diagnostics_module_exists():
    """Test that the bot_diagnostics.py file exists."""
    diagnostics_path = Path("scripts/bot_diagnostics.py")
    assert diagnostics_path.exists(), "❌ ملف bot_diagnostics.py غير موجود"


def test_bot_diagnostics_imports():
    """Test that bot_diagnostics module can be imported."""
    import sys
    from pathlib import Path
    
    # Add parent directory to sys.path
    parent_dir = Path(__file__).parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    
    try:
        from scripts.bot_diagnostics import register_diag_handlers
        assert callable(register_diag_handlers), "❌ register_diag_handlers ليس دالة"
        print("✅ bot_diagnostics.py يمكن استيراده بنجاح")
    except ImportError as e:
        raise AssertionError(f"❌ فشل استيراد bot_diagnostics: {e}") from e


def test_verify_env_script_exists():
    """Test that verify_env.py script exists."""
    verify_env_path = Path("scripts/verify_env.py")
    assert verify_env_path.exists(), "❌ ملف verify_env.py غير موجود"


def test_check_connections_script_exists():
    """Test that check_connections.sh script exists."""
    check_connections_path = Path("scripts/check_connections.sh")
    assert check_connections_path.exists(), "❌ ملف check_connections.sh غير موجود"


def test_reports_directory_exists():
    """Test that reports directory exists."""
    reports_dir = Path("reports")
    assert reports_dir.exists(), "❌ مجلد reports غير موجود"


def test_telegram_chatgpt_mode_updated():
    """Test that telegram_chatgpt_mode.py includes the diagnostic handlers."""
    telegram_bot_path = Path("scripts/telegram_chatgpt_mode.py")
    assert telegram_bot_path.exists(), "❌ ملف telegram_chatgpt_mode.py غير موجود"
    
    content = telegram_bot_path.read_text(encoding="utf-8")
    
    # Check for import statement
    assert "from scripts.bot_diagnostics import register_diag_handlers" in content, \
        "❌ لم يتم استيراد register_diag_handlers في telegram_chatgpt_mode.py"
    
    # Check for registration call
    assert "register_diag_handlers(app)" in content, \
        "❌ لم يتم استدعاء register_diag_handlers في telegram_chatgpt_mode.py"
    
    # Check for help text updates
    assert "/verifyenv" in content, "❌ لم يتم إضافة /verifyenv إلى النص التعليمي"
    assert "/preflight" in content, "❌ لم يتم إضافة /preflight إلى النص التعليمي"
    assert "/report" in content, "❌ لم يتم إضافة /report إلى النص التعليمي"
    assert "أوامر التشخيص" in content, "❌ لم يتم إضافة قسم أوامر التشخيص"
    
    print("✅ telegram_chatgpt_mode.py تم تحديثه بشكل صحيح")


if __name__ == "__main__":
    test_bot_diagnostics_module_exists()
    test_bot_diagnostics_imports()
    test_verify_env_script_exists()
    test_check_connections_script_exists()
    test_reports_directory_exists()
    test_telegram_chatgpt_mode_updated()
    print("\n✅ جميع الاختبارات نجحت!")
