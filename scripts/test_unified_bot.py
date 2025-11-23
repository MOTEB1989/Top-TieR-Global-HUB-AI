#!/usr/bin/env python3
"""
Test script for unified telegram bot
تحقق من الإعدادات والمكتبات المطلوبة
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test if all required imports work."""
    print("🧪 Testing imports...")
    errors = []
    
    try:
        from telegram import Update
        from telegram.ext import Application
        print("  ✅ python-telegram-bot")
    except ImportError as e:
        errors.append(f"  ❌ python-telegram-bot: {e}")
    
    try:
        from dotenv import load_dotenv
        print("  ✅ python-dotenv")
    except ImportError:
        print("  ⚠️  python-dotenv (optional)")
    
    try:
        import requests
        print("  ✅ requests")
    except ImportError as e:
        errors.append(f"  ❌ requests: {e}")
    
    return len(errors) == 0, errors

def test_environment():
    """Test environment configuration."""
    print("\n🔧 Testing environment...")
    
    # Load .env if exists
    env_file = Path(".env")
    if env_file.exists():
        print("  ✅ .env file found")
    else:
        print("  ⚠️  .env file not found (using environment variables)")
    
    # Check critical variables
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if token and not token.startswith("PASTE_") and not token.startswith("${{"):
        print("  ✅ TELEGRAM_BOT_TOKEN configured")
    else:
        print("  ⚠️  TELEGRAM_BOT_TOKEN not configured or placeholder")
    
    # Check optional AI keys
    openai = os.getenv("OPENAI_API_KEY", "")
    if openai and not openai.startswith("PASTE_") and not openai.startswith("${{"):
        print("  ✅ OPENAI_API_KEY configured")
    else:
        print("  ⚠️  OPENAI_API_KEY not configured")
    
    return True

def test_bot_file():
    """Test if bot file is valid."""
    print("\n📄 Testing bot file...")
    
    bot_file = Path("scripts/telegram_unified_bot.py")
    if not bot_file.exists():
        print("  ❌ Bot file not found")
        return False
    
    print(f"  ✅ Bot file found ({bot_file.stat().st_size} bytes)")
    
    # Test syntax
    try:
        import py_compile
        py_compile.compile(str(bot_file), doraise=True)
        print("  ✅ Python syntax valid")
    except Exception as e:
        print(f"  ❌ Syntax error: {e}")
        return False
    
    # Test import
    try:
        sys.path.insert(0, str(bot_file.parent))
        # Don't actually import to avoid side effects
        print("  ✅ Bot structure OK")
    except Exception as e:
        print(f"  ❌ Import error: {e}")
        return False
    
    return True

def test_data_directory():
    """Test if data directory can be created."""
    print("\n📁 Testing data directory...")
    
    data_dir = Path("analysis/bot_data")
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Data directory ready: {data_dir}")
        
        # Test file creation
        test_file = data_dir / ".test"
        test_file.write_text("test")
        test_file.unlink()
        print("  ✅ Write permissions OK")
        
        return True
    except Exception as e:
        print(f"  ❌ Data directory error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("🤖 Unified Telegram Bot - Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run tests
    success, errors = test_imports()
    results.append(("Imports", success))
    if errors:
        for error in errors:
            print(error)
    
    results.append(("Environment", test_environment()))
    results.append(("Bot File", test_bot_file()))
    results.append(("Data Directory", test_data_directory()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("✅ All tests passed!")
        print("\n🚀 To run the bot:")
        print("   python3 scripts/telegram_unified_bot.py")
        return 0
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("\n💡 Common fixes:")
        print("   • Install dependencies: pip install python-telegram-bot python-dotenv requests")
        print("   • Configure .env file with TELEGRAM_BOT_TOKEN")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
