#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
advanced.py

Advanced commands: /summarize, /continue, /regen, /share
أوامر متقدمة للتحكم في المحادثة.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def cmd_summarize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Summarize the current conversation."""
    user_id = update.effective_user.id
    bot_data = context.bot_data
    
    session_store = bot_data.get("session_store")
    current_session = context.user_data.get("current_session", "default")
    
    if not session_store:
        await update.message.reply_text("❌ مخزن الجلسات غير متاح")
        return
    
    # Get conversation history
    messages = session_store.get_messages(user_id, current_session)
    
    if len(messages) < 2:
        await update.message.reply_text(
            "ℹ️ لا توجد محادثة كافية للتلخيص.\n"
            "ابدأ محادثة أولاً باستخدام /chat أو بإرسال رسالة نصية."
        )
        return
    
    # Build conversation text
    conversation_text = "\n\n".join([
        f"{'المستخدم' if msg['role'] == 'user' else 'المساعد'}: {msg['content']}"
        for msg in messages[-20:]  # Last 20 messages
    ])
    
    # Get AI client
    provider = context.user_data.get("provider", "openai")
    model = context.user_data.get("model", "gpt-4o-mini")
    
    client_map = {
        "openai": bot_data.get("openai_client"),
        "anthropic": bot_data.get("anthropic_client"),
        "groq": bot_data.get("groq_client")
    }
    
    client = client_map.get(provider)
    
    if not client or not client.is_available():
        await update.message.reply_text(f"❌ الموفر '{provider}' غير مهيأ")
        return
    
    # Create summarization prompt
    summary_messages = [
        {
            "role": "system",
            "content": "أنت مساعد متخصص في تلخيص المحادثات. قدم ملخصاً واضحاً ومختصراً بالعربية."
        },
        {
            "role": "user",
            "content": f"لخص هذه المحادثة في 3-5 نقاط رئيسية:\n\n{conversation_text}"
        }
    ]
    
    try:
        await update.message.chat.send_action("typing")
        
        summary = client.chat_completion(
            messages=summary_messages,
            model=model,
            temperature=0.3,
            max_tokens=500
        )
        
        await update.message.reply_markdown(
            f"📝 **ملخص المحادثة:**\n\n{summary}"
        )
        
        logger.info(f"[bot] user={user_id} cmd=summarize session={current_session}")
        
    except Exception as e:
        await update.message.reply_text(f"❌ فشل التلخيص: {e}")
        logger.error(f"[bot] user={user_id} summarize_error: {e}")


async def cmd_continue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Continue the last assistant response."""
    user_id = update.effective_user.id
    bot_data = context.bot_data
    
    session_store = bot_data.get("session_store")
    current_session = context.user_data.get("current_session", "default")
    
    if not session_store:
        await update.message.reply_text("❌ مخزن الجلسات غير متاح")
        return
    
    # Get last messages
    messages = session_store.get_messages(user_id, current_session)
    
    if not messages or messages[-1]["role"] != "assistant":
        await update.message.reply_text(
            "ℹ️ لا يوجد رد من المساعد لإكماله.\n"
            "ابدأ محادثة أولاً."
        )
        return
    
    last_response = messages[-1]["content"]
    
    # Get AI client
    provider = context.user_data.get("provider", "openai")
    model = context.user_data.get("model", "gpt-4o-mini")
    
    client_map = {
        "openai": bot_data.get("openai_client"),
        "anthropic": bot_data.get("anthropic_client"),
        "groq": bot_data.get("groq_client")
    }
    
    client = client_map.get(provider)
    
    if not client or not client.is_available():
        await update.message.reply_text(f"❌ الموفر '{provider}' غير مهيأ")
        return
    
    # Create continuation prompt
    continue_messages = [
        {
            "role": "system",
            "content": "أكمل الرد السابق بمزيد من التفاصيل والشرح."
        },
        {
            "role": "user",
            "content": f"الرد السابق:\n{last_response}\n\nأكمل هذا الرد بمزيد من المعلومات:"
        }
    ]
    
    try:
        await update.message.chat.send_action("typing")
        
        continuation = client.chat_completion(
            messages=continue_messages,
            model=model,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Append continuation to last message
        updated_content = last_response + "\n\n" + continuation
        
        # Update in session
        session_data = session_store.get_session(user_id, current_session)
        if session_data and session_data["messages"]:
            session_data["messages"][-1]["content"] = updated_content
            session_store.save_session(user_id, current_session, session_data)
        
        await update.message.reply_text(f"➕ **استمرار:**\n\n{continuation}")
        
        logger.info(f"[bot] user={user_id} cmd=continue session={current_session}")
        
    except Exception as e:
        await update.message.reply_text(f"❌ فشل الاستمرار: {e}")
        logger.error(f"[bot] user={user_id} continue_error: {e}")


async def cmd_regen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Regenerate the last assistant response."""
    user_id = update.effective_user.id
    bot_data = context.bot_data
    
    session_store = bot_data.get("session_store")
    persona_manager = bot_data.get("persona_manager")
    response_builder = bot_data.get("response_builder")
    current_session = context.user_data.get("current_session", "default")
    
    if not session_store:
        await update.message.reply_text("❌ مخزن الجلسات غير متاح")
        return
    
    # Get session
    session_data = session_store.get_session(user_id, current_session)
    
    if not session_data or not session_data.get("messages"):
        await update.message.reply_text("ℹ️ لا توجد رسائل لإعادة توليدها")
        return
    
    # Find last assistant message
    messages = session_data["messages"]
    last_assistant_idx = None
    
    for i in range(len(messages) - 1, -1, -1):
        if messages[i]["role"] == "assistant":
            last_assistant_idx = i
            break
    
    if last_assistant_idx is None:
        await update.message.reply_text("ℹ️ لا يوجد رد من المساعد لإعادة توليده")
        return
    
    # Remove last assistant message
    messages.pop(last_assistant_idx)
    
    # Get AI client
    provider = context.user_data.get("provider", "openai")
    model = context.user_data.get("model", "gpt-4o-mini")
    persona = context.user_data.get("persona", "default")
    
    client_map = {
        "openai": bot_data.get("openai_client"),
        "anthropic": bot_data.get("anthropic_client"),
        "groq": bot_data.get("groq_client")
    }
    
    client = client_map.get(provider)
    
    if not client or not client.is_available():
        await update.message.reply_text(f"❌ الموفر '{provider}' غير مهيأ")
        return
    
    # Build API messages
    api_messages = []
    
    if persona_manager:
        system_prompt = persona_manager.get_system_prompt(persona)
        api_messages.append({"role": "system", "content": system_prompt})
    
    # Add remaining conversation
    for msg in messages:
        api_messages.append({"role": msg["role"], "content": msg["content"]})
    
    try:
        await update.message.chat.send_action("typing")
        
        new_response = client.chat_completion(
            messages=api_messages,
            model=model,
            temperature=0.8,  # Higher temperature for variety
            max_tokens=1000
        )
        
        # Add new response to session
        session_store.append_message(user_id, current_session, "assistant", new_response)
        
        # Add suggestions
        if response_builder:
            new_response = response_builder.add_suggestions(new_response)
            new_response = response_builder.truncate_if_needed(new_response)
        
        await update.message.reply_text(f"🔄 **رد جديد:**\n\n{new_response}")
        
        logger.info(f"[bot] user={user_id} cmd=regen session={current_session}")
        
    except Exception as e:
        # Restore the removed message on error
        session_data["messages"] = messages
        session_store.save_session(user_id, current_session, session_data)
        
        await update.message.reply_text(f"❌ فشل إعادة التوليد: {e}")
        logger.error(f"[bot] user={user_id} regen_error: {e}")


async def cmd_share(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate a shareable snippet of the conversation."""
    user_id = update.effective_user.id
    bot_data = context.bot_data
    
    session_store = bot_data.get("session_store")
    current_session = context.user_data.get("current_session", "default")
    
    if not session_store:
        await update.message.reply_text("❌ مخزن الجلسات غير متاح")
        return
    
    # Get recent messages
    messages = session_store.get_messages(user_id, current_session)
    
    if len(messages) < 2:
        await update.message.reply_text("ℹ️ لا توجد محادثة كافية للمشاركة")
        return
    
    # Take last 6 messages (3 exchanges)
    recent = messages[-6:]
    
    # Build shareable text
    lines = [
        "💬 **مقتطف من المحادثة:**",
        f"📅 الجلسة: `{current_session}`",
        "",
    ]
    
    for msg in recent:
        role_emoji = "👤" if msg["role"] == "user" else "🤖"
        role_label = "المستخدم" if msg["role"] == "user" else "المساعد"
        
        # Truncate long messages
        content = msg["content"]
        if len(content) > 300:
            content = content[:300] + "..."
        
        lines.append(f"{role_emoji} **{role_label}:**")
        lines.append(content)
        lines.append("")
    
    lines.append("---")
    lines.append("_تم الإنشاء بواسطة بوت Top-TieR-Global-HUB-AI_")
    
    share_text = "\n".join(lines)
    
    await update.message.reply_markdown(share_text)
    
    logger.info(f"[bot] user={user_id} cmd=share session={current_session}")
