#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
meta.py

Meta commands: /help, /status, /model, /provider, /persona
أوامر التحكم والمساعدة.
"""

import logging
import textwrap
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


HELP_TEXT = textwrap.dedent("""
🤖 **بوت ChatGPT المتقدم - Top-TieR-Global-HUB-AI**

━━━━━━━━━━━━━━━━━━━━
📋 **الأوامر الأساسية**
━━━━━━━━━━━━━━━━━━━━

/start - رسالة ترحيب
/help - عرض هذه المساعدة
/status - حالة النظام والتكوين
/whoami - معرف Telegram الخاص بك

━━━━━━━━━━━━━━━━━━━━
💬 **إدارة الجلسات**
━━━━━━━━━━━━━━━━━━━━

/sessions - عرض كل الجلسات
/new <اسم> - إنشاء جلسة جديدة
/switch <اسم> - التبديل إلى جلسة
/clear - مسح الجلسة الحالية
/export <md|json> - تصدير الجلسة

━━━━━━━━━━━━━━━━━━━━
🎯 **الدردشة والأوامر المتقدمة**
━━━━━━━━━━━━━━━━━━━━

/chat <نص> - دردشة مع الذكاء الاصطناعي
أو ببساطة أرسل رسالة نصية مباشرة!

/summarize - تلخيص المحادثة الحالية
/continue - إكمال آخر رد من المساعد
/regen - إعادة توليد آخر رد
/share - إنشاء مقتطف قابل للمشاركة

━━━━━━━━━━━━━━━━━━━━
⚙️ **التكوين**
━━━━━━━━━━━━━━━━━━━━

/model list - عرض النماذج المتاحة
/model <اسم> - اختيار نموذج معين

/provider list - عرض الموفرين المتاحين
/provider <openai|anthropic|groq> - اختيار موفر

/persona list - عرض الشخصيات المتاحة
/persona <اسم> - اختيار شخصية

━━━━━━━━━━━━━━━━━━━━
✨ **ميزات خاصة**
━━━━━━━━━━━━━━━━━━━━

• ذاكرة محادثة ذكية لكل جلسة
• اقتراحات متابعة تلقائية
• فلتر أمان للمحتوى الحساس
• دعم عدة موفرين ونماذج
• شخصيات متخصصة (مهندس، أمان، توثيق)

━━━━━━━━━━━━━━━━━━━━
""").strip()


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display help message."""
    await update.message.reply_markdown(HELP_TEXT)
    logger.info(f"[bot] user={update.effective_user.id} cmd=help")


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command - welcome message."""
    welcome = textwrap.dedent("""
    🤖 **مرحباً بك في بوت ChatGPT المتقدم!**
    
    أنا مساعدك الذكي المتطور لمستودع Top-TieR-Global-HUB-AI.
    
    **المميزات:**
    ✅ جلسات متعددة للمحادثات
    ✅ دعم عدة نماذج وموفرين AI
    ✅ شخصيات متخصصة (مهندس، أمان، توثيق)
    ✅ أوامر متقدمة (تلخيص، مشاركة، استمرار)
    ✅ فلتر أمان ذكي
    
    استخدم /help لعرض جميع الأوامر المتاحة.
    """).strip()
    
    await update.message.reply_markdown(welcome)
    logger.info(f"[bot] user={update.effective_user.id} cmd=start")


async def cmd_whoami(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display user's Telegram ID."""
    user_id = update.effective_user.id
    username = update.effective_user.username or "N/A"
    first_name = update.effective_user.first_name or ""
    
    info = textwrap.dedent(f"""
    🆔 **معلوماتك:**
    
    **معرف Telegram:** `{user_id}`
    **اسم المستخدم:** @{username}
    **الاسم:** {first_name}
    
    لإضافة معرفك إلى القائمة المسموح بها:
    ```
    TELEGRAM_ALLOWLIST={user_id}
    ```
    """).strip()
    
    await update.message.reply_markdown(info)
    logger.info(f"[bot] user={user_id} cmd=whoami")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display bot status and configuration."""
    user_id = update.effective_user.id
    
    # Get current session info
    current_session = context.user_data.get("current_session", "default")
    current_provider = context.user_data.get("provider", "openai")
    current_model = context.user_data.get("model", "gpt-4o-mini")
    current_persona = context.user_data.get("persona", "default")
    
    # Get bot components from context
    bot_data = context.bot_data
    openai_client = bot_data.get("openai_client")
    anthropic_client = bot_data.get("anthropic_client")
    groq_client = bot_data.get("groq_client")
    rate_limiter = bot_data.get("rate_limiter")
    
    # Build status message
    status_lines = [
        "📊 **حالة البوت:**",
        "",
        f"**الجلسة الحالية:** `{current_session}`",
        f"**الموفر:** `{current_provider}`",
        f"**النموذج:** `{current_model}`",
        f"**الشخصية:** `{current_persona}`",
        "",
        "**الموفرون المتاحون:**",
    ]
    
    # Check provider availability
    if openai_client and openai_client.is_available():
        status_lines.append("✅ OpenAI - متاح")
    else:
        status_lines.append("❌ OpenAI - غير مهيأ")
    
    if anthropic_client and anthropic_client.is_available():
        status_lines.append("✅ Anthropic - متاح")
    else:
        status_lines.append("❌ Anthropic - غير مهيأ")
    
    if groq_client and groq_client.is_available():
        status_lines.append("✅ Groq - متاح")
    else:
        status_lines.append("❌ Groq - غير مهيأ")
    
    # Rate limit info
    if rate_limiter:
        remaining = rate_limiter.get_remaining(user_id)
        max_msgs = rate_limiter.max_messages
        window = rate_limiter.window_seconds // 60  # Convert to minutes
        status_lines.append("")
        status_lines.append(f"**حد الرسائل:** {remaining}/{max_msgs} متبقي ({window} دقيقة)")
    
    await update.message.reply_markdown("\n".join(status_lines))
    logger.info(f"[bot] user={user_id} cmd=status")


async def cmd_model(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /model command - list or set model."""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text(
            "❌ الرجاء تحديد 'list' لعرض النماذج أو اسم نموذج للاختيار.\n"
            "مثال:\n"
            "/model list\n"
            "/model gpt-4o-mini"
        )
        return
    
    action = context.args[0].lower()
    
    if action == "list":
        # List available models
        model_registry = context.bot_data.get("model_registry")
        if not model_registry:
            await update.message.reply_text("❌ سجل النماذج غير متاح")
            return
        
        provider = context.user_data.get("provider", "openai")
        models = model_registry.list_models(provider)
        
        lines = [f"**النماذج المتاحة ({provider}):**\n"]
        for model in models:
            lines.append(f"• `{model.name}`")
            lines.append(f"  {model.display_name} - {model.description}\n")
        
        await update.message.reply_markdown("\n".join(lines))
    else:
        # Set model
        model_name = action
        model_registry = context.bot_data.get("model_registry")
        provider = context.user_data.get("provider", "openai")
        
        if model_registry and model_registry.validate_model(model_name, provider):
            context.user_data["model"] = model_name
            
            # Update session metadata
            session_store = context.bot_data.get("session_store")
            current_session = context.user_data.get("current_session", "default")
            if session_store:
                session_store.update_metadata(user_id, current_session, "model", model_name)
            
            await update.message.reply_text(f"✅ تم تعيين النموذج إلى: `{model_name}`")
            logger.info(f"[bot] user={user_id} cmd=model action=set model={model_name}")
        else:
            await update.message.reply_text(
                f"❌ النموذج '{model_name}' غير متاح للموفر '{provider}'\n"
                "استخدم /model list لعرض النماذج المتاحة"
            )
    
    logger.info(f"[bot] user={user_id} cmd=model")


async def cmd_provider(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /provider command - list or set provider."""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text(
            "❌ الرجاء تحديد 'list' لعرض الموفرين أو اسم موفر للاختيار.\n"
            "مثال:\n"
            "/provider list\n"
            "/provider openai"
        )
        return
    
    action = context.args[0].lower()
    
    if action == "list":
        # List available providers
        bot_data = context.bot_data
        
        lines = ["**الموفرون المتاحون:**\n"]
        
        if bot_data.get("openai_client", {}).is_available():
            lines.append("✅ `openai` - OpenAI (GPT models)")
        else:
            lines.append("❌ `openai` - غير مهيأ")
        
        if bot_data.get("anthropic_client", {}).is_available():
            lines.append("✅ `anthropic` - Anthropic (Claude models)")
        else:
            lines.append("❌ `anthropic` - غير مهيأ")
        
        if bot_data.get("groq_client", {}).is_available():
            lines.append("✅ `groq` - Groq (Fast inference)")
        else:
            lines.append("❌ `groq` - غير مهيأ")
        
        await update.message.reply_markdown("\n".join(lines))
    else:
        # Set provider
        provider_name = action
        bot_data = context.bot_data
        
        # Check if provider is available
        client_map = {
            "openai": bot_data.get("openai_client"),
            "anthropic": bot_data.get("anthropic_client"),
            "groq": bot_data.get("groq_client")
        }
        
        if provider_name not in client_map:
            await update.message.reply_text(
                f"❌ موفر غير معروف: '{provider_name}'\n"
                "استخدم /provider list لعرض الموفرين المتاحين"
            )
            return
        
        client = client_map[provider_name]
        
        if not client or not client.is_available():
            await update.message.reply_text(
                f"⚠️ مفتاح المزود '{provider_name}' غير مُهيّأ.\n"
                f"سيتم الرجوع إلى الموفر الحالي.\n\n"
                f"لتفعيل {provider_name}، أضف المفتاح في المتغيرات البيئية."
            )
            logger.warning(f"[bot] user={user_id} attempted to use unavailable provider={provider_name}")
            return
        
        # Set provider
        context.user_data["provider"] = provider_name
        
        # Set default model for this provider
        model_registry = bot_data.get("model_registry")
        if model_registry:
            default_model = model_registry.get_default_model(provider_name)
            context.user_data["model"] = default_model
        
        # Update session metadata
        session_store = bot_data.get("session_store")
        current_session = context.user_data.get("current_session", "default")
        if session_store:
            session_store.update_metadata(user_id, current_session, "provider", provider_name)
            session_store.update_metadata(user_id, current_session, "model", context.user_data["model"])
        
        await update.message.reply_text(
            f"✅ تم تعيين الموفر إلى: `{provider_name}`\n"
            f"النموذج الافتراضي: `{context.user_data['model']}`"
        )
        logger.info(f"[bot] user={user_id} cmd=provider action=set provider={provider_name}")
    
    logger.info(f"[bot] user={user_id} cmd=provider")


async def cmd_persona(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /persona command - list or set persona."""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text(
            "❌ الرجاء تحديد 'list' لعرض الشخصيات أو اسم شخصية للاختيار.\n"
            "مثال:\n"
            "/persona list\n"
            "/persona engineer"
        )
        return
    
    action = context.args[0].lower()
    persona_manager = context.bot_data.get("persona_manager")
    
    if not persona_manager:
        await update.message.reply_text("❌ مدير الشخصيات غير متاح")
        return
    
    if action == "list":
        # List available personas
        personas = persona_manager.list_personas()
        
        lines = ["**الشخصيات المتاحة:**\n"]
        for name, desc in personas.items():
            lines.append(f"• `{name}` - {desc}")
        
        await update.message.reply_markdown("\n".join(lines))
    else:
        # Set persona
        persona_name = action
        
        if persona_manager.get_persona(persona_name):
            context.user_data["persona"] = persona_name
            
            # Update session metadata
            session_store = context.bot_data.get("session_store")
            current_session = context.user_data.get("current_session", "default")
            if session_store:
                session_store.update_metadata(user_id, current_session, "persona", persona_name)
            
            persona = persona_manager.get_persona(persona_name)
            await update.message.reply_markdown(
                f"✅ تم تعيين الشخصية إلى: `{persona_name}`\n\n"
                f"**{persona.display_name}**\n{persona.description}"
            )
            logger.info(f"[bot] user={user_id} cmd=persona action=set persona={persona_name}")
        else:
            await update.message.reply_text(
                f"❌ الشخصية '{persona_name}' غير موجودة\n"
                "استخدم /persona list لعرض الشخصيات المتاحة"
            )
    
    logger.info(f"[bot] user={user_id} cmd=persona")
