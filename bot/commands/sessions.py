#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sessions.py

Session management commands: /sessions, /new, /switch, /clear, /export
أوامر إدارة الجلسات.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def cmd_sessions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all sessions for the user."""
    user_id = update.effective_user.id
    session_store = context.bot_data.get("session_store")
    
    if not session_store:
        await update.message.reply_text("❌ مخزن الجلسات غير متاح")
        return
    
    sessions = session_store.list_sessions(user_id)
    
    if not sessions:
        await update.message.reply_text(
            "📋 لا توجد جلسات بعد.\n"
            "استخدم /new <اسم> لإنشاء جلسة جديدة."
        )
        return
    
    current_session = context.user_data.get("current_session", "default")
    
    lines = ["📋 **جلساتك:**\n"]
    for session in sessions:
        marker = "👉 " if session["name"] == current_session else "   "
        lines.append(
            f"{marker}**{session['name']}**\n"
            f"   • الرسائل: {session['message_count']}\n"
            f"   • النموذج: `{session['model']}`\n"
            f"   • آخر تحديث: {session['updated_at'][:19]}\n"
        )
    
    lines.append("\n💡 استخدم `/switch <اسم>` للتبديل بين الجلسات")
    
    await update.message.reply_markdown("\n".join(lines))
    logger.info(f"[bot] user={user_id} cmd=sessions count={len(sessions)}")


async def cmd_new(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Create a new session."""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text(
            "❌ الرجاء تحديد اسم الجلسة.\n"
            "مثال:\n"
            "/new مشروعي\n"
            "/new project_alpha"
        )
        return
    
    session_name = " ".join(context.args).strip()
    
    # Validate session name
    if len(session_name) > 50:
        await update.message.reply_text("❌ اسم الجلسة طويل جداً (الحد الأقصى 50 حرف)")
        return
    
    # Clean session name for filesystem
    safe_name = "".join(c for c in session_name if c.isalnum() or c in (" ", "_", "-"))
    if not safe_name:
        await update.message.reply_text("❌ اسم الجلسة غير صالح")
        return
    
    session_store = context.bot_data.get("session_store")
    if not session_store:
        await update.message.reply_text("❌ مخزن الجلسات غير متاح")
        return
    
    # Create session
    if session_store.create_session(user_id, safe_name):
        context.user_data["current_session"] = safe_name
        await update.message.reply_text(
            f"✅ تم إنشاء جلسة جديدة: `{safe_name}`\n"
            f"وتم التبديل إليها تلقائياً."
        )
        logger.info(f"[bot] user={user_id} cmd=new session={safe_name}")
    else:
        await update.message.reply_text(
            f"❌ الجلسة `{safe_name}` موجودة بالفعل.\n"
            f"استخدم /switch {safe_name} للتبديل إليها."
        )


async def cmd_switch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Switch to a different session."""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text(
            "❌ الرجاء تحديد اسم الجلسة.\n"
            "استخدم /sessions لعرض الجلسات المتاحة.\n"
            "مثال:\n"
            "/switch default"
        )
        return
    
    session_name = " ".join(context.args).strip()
    session_store = context.bot_data.get("session_store")
    
    if not session_store:
        await update.message.reply_text("❌ مخزن الجلسات غير متاح")
        return
    
    # Check if session exists
    session_data = session_store.get_session(user_id, session_name)
    
    if not session_data:
        await update.message.reply_text(
            f"❌ الجلسة `{session_name}` غير موجودة.\n"
            "استخدم /sessions لعرض الجلسات المتاحة."
        )
        return
    
    # Switch session
    context.user_data["current_session"] = session_name
    
    # Load session metadata into user context
    metadata = session_data.get("metadata", {})
    if "model" in metadata:
        context.user_data["model"] = metadata["model"]
    if "provider" in metadata:
        context.user_data["provider"] = metadata["provider"]
    if "persona" in metadata:
        context.user_data["persona"] = metadata["persona"]
    
    msg_count = len(session_data.get("messages", []))
    
    await update.message.reply_markdown(
        f"✅ تم التبديل إلى الجلسة: `{session_name}`\n\n"
        f"**الرسائل:** {msg_count}\n"
        f"**النموذج:** `{metadata.get('model', 'N/A')}`\n"
        f"**الموفر:** `{metadata.get('provider', 'N/A')}`\n"
        f"**الشخصية:** `{metadata.get('persona', 'N/A')}`"
    )
    logger.info(f"[bot] user={user_id} cmd=switch session={session_name}")


async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear current session messages."""
    user_id = update.effective_user.id
    current_session = context.user_data.get("current_session", "default")
    
    session_store = context.bot_data.get("session_store")
    if not session_store:
        await update.message.reply_text("❌ مخزن الجلسات غير متاح")
        return
    
    if session_store.clear_session(user_id, current_session):
        await update.message.reply_text(
            f"✅ تم مسح جميع الرسائل في الجلسة `{current_session}`\n"
            "يمكنك البدء بمحادثة جديدة الآن."
        )
        logger.info(f"[bot] user={user_id} cmd=clear session={current_session}")
    else:
        await update.message.reply_text("❌ فشل مسح الجلسة")


async def cmd_export(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Export current session."""
    user_id = update.effective_user.id
    current_session = context.user_data.get("current_session", "default")
    
    # Determine format
    format_type = "json"
    if context.args and context.args[0].lower() in ["md", "markdown"]:
        format_type = "md"
    
    session_store = context.bot_data.get("session_store")
    if not session_store:
        await update.message.reply_text("❌ مخزن الجلسات غير متاح")
        return
    
    exported = session_store.export_session(user_id, current_session, format_type)
    
    if not exported:
        await update.message.reply_text("❌ فشل تصدير الجلسة")
        return
    
    # Send as file if too long, otherwise as message
    if len(exported) > 4000:
        # Send as file
        filename = f"session_{current_session}.{format_type}"
        await update.message.reply_document(
            document=exported.encode('utf-8'),
            filename=filename,
            caption=f"📄 تصدير الجلسة: `{current_session}`"
        )
    else:
        # Send as message
        if format_type == "json":
            await update.message.reply_text(f"```json\n{exported}\n```", parse_mode="Markdown")
        else:
            await update.message.reply_markdown(exported)
    
    logger.info(f"[bot] user={user_id} cmd=export session={current_session} format={format_type}")
