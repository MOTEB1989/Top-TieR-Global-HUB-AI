"""Simple i18n module for Telegram bot."""
from typing import Dict

# Translation dictionary
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "start": {
        "ar": "مرحباً! أنا بوت Top-TieR Global HUB AI 🤖\n\nاستخدم /help لعرض الأوامر المتاحة.",
        "en": "Welcome! I'm the Top-TieR Global HUB AI bot 🤖\n\nUse /help to see available commands."
    },
    "help": {
        "ar": "📋 الأوامر المتاحة:\n\n/start - بدء المحادثة\n/help - عرض هذه الرسالة\n/health - التحقق من حالة البوت",
        "en": "📋 Available commands:\n\n/start - Start the conversation\n/help - Show this message\n/health - Check bot health"
    },
    "health": {
        "ar": "✅ البوت يعمل بشكل صحيح!",
        "en": "✅ Bot is healthy and running!"
    },
    "unknown_command": {
        "ar": "❌ أمر غير معروف. استخدم /help لعرض الأوامر المتاحة.",
        "en": "❌ Unknown command. Use /help to see available commands."
    }
}


def get_translation(key: str, locale: str = "en") -> str:
    """
    Get translation for a key in the specified locale.
    
    Args:
        key: Translation key
        locale: Locale code (ar or en), defaults to en
        
    Returns:
        Translated string, or the key itself if not found
    """
    if key not in TRANSLATIONS:
        return key
    
    translations = TRANSLATIONS[key]
    return translations.get(locale, translations.get("en", key))


def t(key: str, locale: str = "en") -> str:
    """Alias for get_translation for shorter syntax."""
    return get_translation(key, locale)
