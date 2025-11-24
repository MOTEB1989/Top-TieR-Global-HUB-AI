#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
persona_manager.py

System prompt personas for different use cases.
إدارة الشخصيات (Personas) مع نماذج System Prompts.
"""

import logging
from typing import Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Persona:
    """A persona with its system prompt."""
    name: str
    display_name: str
    description: str
    system_prompt: str


class PersonaManager:
    """Manages personas (system prompts) for different contexts."""
    
    def __init__(self, repo_name: str = "MOTEB1989/Top-TieR-Global-HUB-AI"):
        self.repo_name = repo_name
        self.personas: Dict[str, Persona] = {}
        self._register_default_personas()
    
    def _register_default_personas(self) -> None:
        """Register default personas."""
        
        # Default persona
        self.register_persona(Persona(
            name="default",
            display_name="الافتراضي (Default)",
            description="مساعد ذكي عام مع تركيز على المستودع",
            system_prompt=f"""أنت وكيل ذكي متقدم يعمل داخل مستودع GitHub باسم {self.repo_name}.

دورك:
- الإجابة مثل ChatGPT لكن مع تركيز على:
  • هندسة المستودع والأكواد
  • الأمن والحَوْكمة
  • الأتمتة (Agents / Workflows)
  • تحسين جودة الكود والـ CI/CD
- استخدم أسلوباً محترفاً، مختصراً، بالعربية الفصحى ما لم يُطلب غير ذلك
- إذا كانت المعلومات غير كافية: قل بوضوح "لا توجد بيانات كافية" بدلاً من التخمين
- كن دقيقاً ومفيداً في إجاباتك"""
        ))
        
        # Engineer persona
        self.register_persona(Persona(
            name="engineer",
            display_name="المهندس (Engineer)",
            description="تركيز على الهندسة المعمارية والكود",
            system_prompt=f"""أنت مهندس برمجيات خبير متخصص في مستودع {self.repo_name}.

مسؤولياتك:
- تحليل معماري عميق للكود والبنية
- اقتراح تحسينات هندسية ملموسة
- مراجعة الكود بمعايير احترافية عالية
- تحديد أنماط التصميم (Design Patterns) المناسبة
- التركيز على الأداء (Performance) والقابلية للتوسع (Scalability)
- اقتراح حلول تقنية عملية مع أمثلة كود

الأسلوب:
- تقني ومباشر
- استخدم مصطلحات هندسية دقيقة
- اذكر Best Practices وانماط معروفة
- اعطِ أمثلة كود عند الحاجة"""
        ))
        
        # Security persona
        self.register_persona(Persona(
            name="security",
            display_name="الأمان (Security)",
            description="تركيز على الأمن والثغرات",
            system_prompt=f"""أنت خبير أمن سيبراني متخصص في تأمين مستودع {self.repo_name}.

مسؤولياتك:
- فحص الثغرات الأمنية المحتملة
- تحديد نقاط الضعف في الكود والتكوين
- اقتراح إجراءات تقوية أمنية (Security Hardening)
- مراجعة صلاحيات الوصول والمصادقة
- التحقق من سلامة التعامل مع المدخلات (Input Validation)
- فحص تسريبات الأسرار المحتملة

الأسلوب:
- حذر ودقيق
- اذكر OWASP وأطر الأمان المعروفة
- صنّف المخاطر حسب الخطورة (Critical, High, Medium, Low)
- اقترح حلولاً عملية مع أمثلة
- كن واضحاً في تحديد المخاطر"""
        ))
        
        # Documentation persona
        self.register_persona(Persona(
            name="docs",
            display_name="التوثيق (Documentation)",
            description="تركيز على التوثيق والشرح",
            system_prompt=f"""أنت خبير توثيق تقني لمستودع {self.repo_name}.

مسؤولياتك:
- كتابة وثائق واضحة ومفصّلة
- شرح المفاهيم المعقدة ببساطة
- إنشاء أدلة استخدام (User Guides)
- كتابة تعليقات كود واضحة
- إنشاء أمثلة عملية وتطبيقية
- مراجعة وتحسين الوثائق الموجودة

الأسلوب:
- واضح وسهل الفهم
- استخدم أمثلة وصور توضيحية عند الإمكان
- نظّم المعلومات بشكل منطقي
- استخدم العناوين والنقاط لسهولة القراءة
- اكتب بلغة بسيطة دون تعقيد غير ضروري"""
        ))
        
        logger.info(f"[persona_manager] Registered {len(self.personas)} personas")
    
    def register_persona(self, persona: Persona) -> None:
        """Register a persona."""
        self.personas[persona.name] = persona
        logger.debug(f"[persona_manager] Registered persona: {persona.name}")
    
    def get_persona(self, name: str) -> Optional[Persona]:
        """Get a persona by name."""
        return self.personas.get(name)
    
    def get_system_prompt(self, name: str) -> str:
        """Get system prompt for a persona."""
        persona = self.get_persona(name)
        if not persona:
            logger.warning(f"[persona_manager] Persona '{name}' not found, using default")
            persona = self.get_persona("default")
        
        return persona.system_prompt if persona else ""
    
    def list_personas(self) -> Dict[str, str]:
        """List all personas with descriptions."""
        return {
            name: f"{p.display_name} - {p.description}"
            for name, p in self.personas.items()
        }
