#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
chat.py

Chat command and fallback text message handler.
معالج الدردشة والرسائل النصية.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def process_chat_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_message: str
) -> None:
    """
    Process a chat message through the AI pipeline.
    
    Args:
        update: Telegram update
        context: Bot context
        user_message: User's message text
    """
    user_id = update.effective_user.id
    
    # Get components from bot_data
    bot_data = context.bot_data
    session_store = bot_data.get("session_store")
    rate_limiter = bot_data.get("rate_limiter")
    safety_filter = bot_data.get("safety_filter")
    response_builder = bot_data.get("response_builder")
    persona_manager = bot_data.get("persona_manager")
    
    # Check rate limit
    if rate_limiter and not rate_limiter.check_limit(user_id):
        remaining_time = rate_limiter.get_reset_time(user_id)
        minutes = remaining_time // 60
        await update.message.reply_text(
            f"⏱️ **تم تجاوز حد الرسائل**\n\n"
            f"لقد وصلت إلى الحد الأقصى للرسائل ({rate_limiter.max_messages} رسالة كل {rate_limiter.window_seconds // 60} دقيقة).\n"
            f"الرجاء الانتظار {minutes} دقيقة تقريباً."
        )
        logger.warning(f"[bot] user={user_id} rate_limited")
        return
    
    # Safety check
    if safety_filter:
        is_safe, warning, detected = safety_filter.filter_input(user_message)
        if not is_safe:
            await update.message.reply_markdown(warning)
            logger.warning(f"[bot] user={user_id} unsafe_input detected={detected}")
            return
    
    # Get current session
    current_session = context.user_data.get("current_session", "default")
    
    # Get session metadata
    if session_store:
        provider = session_store.get_metadata(user_id, current_session, "provider", "openai")
        model = session_store.get_metadata(user_id, current_session, "model", "gpt-4o-mini")
        persona = session_store.get_metadata(user_id, current_session, "persona", "default")
    else:
        provider = context.user_data.get("provider", "openai")
        model = context.user_data.get("model", "gpt-4o-mini")
        persona = context.user_data.get("persona", "default")
    
    # Get AI client
    client_map = {
        "openai": bot_data.get("openai_client"),
        "anthropic": bot_data.get("anthropic_client"),
        "groq": bot_data.get("groq_client")
    }
    
    client = client_map.get(provider)
    
    if not client or not client.is_available():
        await update.message.reply_text(
            f"❌ الموفر '{provider}' غير مهيأ.\n"
            "استخدم /provider list لعرض الموفرين المتاحين."
        )
        logger.error(f"[bot] user={user_id} provider={provider} unavailable")
        return
    
    # Save user message to session
    if session_store:
        session_store.append_message(user_id, current_session, "user", user_message)
    
    # Build messages for API
    messages = []
    
    # Add system prompt
    if persona_manager:
        system_prompt = persona_manager.get_system_prompt(persona)
        messages.append({"role": "system", "content": system_prompt})
    
    # Add conversation history
    if session_store:
        history = session_store.get_messages(user_id, current_session)
        messages.extend(history)
    else:
        messages.append({"role": "user", "content": user_message})
    
    # Call AI
    try:
        # Send "typing" indicator
        await update.message.chat.send_action("typing")
        
        response = client.chat_completion(
            messages=messages,
            model=model,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Save assistant response
        if session_store:
            session_store.append_message(user_id, current_session, "assistant", response)
        
        # Add follow-up suggestions
        if response_builder:
            response = response_builder.add_suggestions(response)
        
        # Truncate if needed
        if response_builder:
            response = response_builder.truncate_if_needed(response, max_length=4000)
        
        # Record message for rate limiting
        if rate_limiter:
            rate_limiter.record_message(user_id)
        
        # Send response
        await update.message.reply_text(response)
        
        # Log with token approximation
        approx_tokens = len(user_message + response) // 4
        logger.info(
            f"[bot] user={user_id} cmd=chat session={current_session} "
            f"provider={provider} model={model} tokens_approx={approx_tokens}"
        )
        
    except Exception as e:
        error_msg = str(e)
        
        if response_builder:
            error_msg = response_builder.format_error(error_msg)
        
        await update.message.reply_text(error_msg)
        logger.error(f"[bot] user={user_id} chat_error: {e}")


async def cmd_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /chat command."""
    if not context.args:
        await update.message.reply_text(
            "❌ الرجاء كتابة رسالتك بعد الأمر.\n"
            "مثال:\n"
            "/chat ما هي أفضل الممارسات للأمان في API؟\n\n"
            "💡 يمكنك أيضاً إرسال رسالة نصية مباشرة بدون استخدام /chat"
        )
        return
    
    user_message = " ".join(context.args).strip()
    await process_chat_message(update, context, user_message)


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle plain text messages (fallback)."""
    text = update.message.text or ""
    
    if not text.strip():
        return
    
    # Process as chat message
    await process_chat_message(update, context, text.strip())
