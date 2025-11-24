#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
response_builder.py

Follow-up suggestions and response enhancement.
بناء الردود مع اقتراحات المتابعة.
"""

import logging
import random
from typing import List

logger = logging.getLogger(__name__)


class ResponseBuilder:
    """Builds enhanced responses with follow-up suggestions."""
    
    def __init__(self, silent_suggestions: bool = False):
        """
        Initialize response builder.
        
        Args:
            silent_suggestions: If True, don't append suggestions
        """
        self.silent_suggestions = silent_suggestions
        
        # Suggestion templates in Arabic
        self.suggestion_templates = [
            [
                "💡 هل تريد معرفة المزيد عن هذا الموضوع؟",
                "📊 يمكنني تقديم أمثلة عملية إن أردت",
                "🔍 لديّ تفاصيل إضافية متاحة"
            ],
            [
                "💡 هل تحتاج إلى توضيح أي نقطة معينة؟",
                "📝 يمكنني شرح الخطوات بالتفصيل",
                "🎯 هل تريد التعمق في جزء محدد؟"
            ],
            [
                "💡 لديّ معلومات إضافية حول هذا",
                "🔧 يمكنني مساعدتك في التطبيق العملي",
                "📚 هل تريد مراجع أو مصادر إضافية؟"
            ],
            [
                "💡 هل تريد أمثلة كود لهذا الموضوع؟",
                "🚀 يمكنني شرح أفضل الممارسات",
                "⚙️ هل تحتاج مساعدة في التنفيذ؟"
            ],
            [
                "💡 لديّ اقتراحات لتحسين هذا",
                "📈 يمكنني مقارنة بدائل مختلفة",
                "🔐 هل تريد مراجعة الجوانب الأمنية؟"
            ]
        ]
    
    def add_suggestions(self, response: str, context: str = "general") -> str:
        """
        Add follow-up suggestions to response.
        
        Args:
            response: Original response text
            context: Context hint for suggestions (unused for now)
            
        Returns:
            Response with suggestions appended
        """
        if self.silent_suggestions:
            return response
        
        # Select a random suggestion set
        suggestions = random.choice(self.suggestion_templates)
        
        # Pick 2-3 suggestions randomly
        num_suggestions = random.randint(2, 3)
        selected = random.sample(suggestions, min(num_suggestions, len(suggestions)))
        
        # Build suggestion section
        suggestion_text = "\n\n---\n**اقتراحات للمتابعة:**\n" + "\n".join(f"• {s}" for s in selected)
        
        return response + suggestion_text
    
    def format_list_response(self, items: List[str], title: str = "القائمة") -> str:
        """
        Format a list response.
        
        Args:
            items: List of items to format
            title: Title for the list
            
        Returns:
            Formatted list response
        """
        if not items:
            return f"**{title}:** لا توجد عناصر"
        
        lines = [f"**{title}:**\n"]
        for i, item in enumerate(items, 1):
            lines.append(f"{i}. {item}")
        
        return "\n".join(lines)
    
    def format_error(self, error_msg: str, friendly: bool = True) -> str:
        """
        Format an error message.
        
        Args:
            error_msg: Error message
            friendly: If True, add friendly wrapper
            
        Returns:
            Formatted error message
        """
        if friendly:
            return f"❌ **عذراً، حدث خطأ:**\n{error_msg}\n\nيمكنك المحاولة مرة أخرى أو استخدام /help للمساعدة."
        return f"❌ {error_msg}"
    
    def truncate_if_needed(self, text: str, max_length: int = 4000) -> str:
        """
        Truncate text if it exceeds max length.
        
        Args:
            text: Text to truncate
            max_length: Maximum length
            
        Returns:
            Truncated text if needed
        """
        if len(text) <= max_length:
            return text
        
        return text[:max_length] + "\n\n...\n[تم قطع الرد لطوله - الرجاء استخدام /export للحصول على النص الكامل]"
