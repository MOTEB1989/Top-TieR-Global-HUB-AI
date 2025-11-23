#!/usr/bin/env python3
"""
TopTire AI Agent - Smart Health Validator & Confirmation System
يتولى مهمة التحقق الذكي من جميع المفاتيح وتنفيذ الإجراءات اللازمة
"""

import os
import sys
import asyncio
import requests
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ServiceStatus(Enum):
    """حالات الخدمة"""
    HEALTHY = "✅ صحيح"
    DEGRADED = "⚠️ جزئي"
    FAILED = "❌ فشل"
    MISSING = "🔑 مفقود المفتاح"

@dataclass
class ServiceReport:
    """تقرير فحص الخدمة"""
    name: str
    status: ServiceStatus
    message: str
    details: Optional[Dict] = None
    action_taken: Optional[str] = None

class SmartAgentValidator:
    """وكيل ذكي للتحقق والتشخيص"""
    
    def __init__(self, auto_fix: bool = True):
        self.reports: List[ServiceReport] = []
        self.auto_fix = auto_fix
        self.api_endpoints = {
            "WHO": "https://ghoapi.azureedge.net/api/Indicator?$top=3",
            "WorldBank": "https://api.worldbank.org/v2/country/SA/indicator/SP.POP.TOTL?format=json&date=2021",
            "Wikidata": "https://www.wikidata.org/wiki/Special:EntityData/Q30.json",
            "GitHubAPI": "https://api.github.com/repos/MOTEB1989/Top-TieR-Global-HUB-AI"
        }
    
    async def check_openai(self) -> ServiceReport:
        """التحقق الذكي من OpenAI"""
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key or api_key.startswith("sk-...") or len(api_key) < 20:
            return ServiceReport(
                name="OpenAI GPT",
                status=ServiceStatus.MISSING,
                message="المفتاح غير مضبوط أو غير صالح",
                action_taken="تخطي الاختبار - يرجى إعداد OPENAI_API_KEY"
            )
        
        try:
            # اختبار الموديلات المتوفرة
            import openai
            openai.api_key = api_key
            
            # نموذج اختبار خفيف
            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5
            )
            
            return ServiceReport(
                name="OpenAI GPT",
                status=ServiceStatus.HEALTHY,
                message="الاتصال ناجح",
                details={"model": "gpt-3.5-turbo", "usage": response.usage}
            )
            
        except Exception as e:
            return ServiceReport(
                name="OpenAI GPT",
                status=ServiceStatus.FAILED,
                message=f"خطأ: {str(e)[:100]}",
                action_taken="تحقق من صلاحية المفتاح والشبكة"
            )
    
    async def check_database(self, db_type: str, url_env: str) -> ServiceReport:
        """التحقق من قواعد البيانات"""
        url = os.getenv(url_env)
        
        if not url or "example" in url or "placeholder" in url:
            return ServiceReport(
                name=f"Database ({db_type})",
                status=ServiceStatus.MISSING,
                message=f"عنوان {url_env} غير مضبوط",
                action_taken=f"يرجى إعداد {url_env} في ملف .env"
            )
        
        try:
            # اختبار الاتصال الأساسي
            if "postgresql" in url:
                import psycopg2
                conn = psycopg2.connect(url, connect_timeout=3)
                conn.close()
            elif "redis" in url:
                import redis
                r = redis.from_url(url)
                r.ping()
            
            return ServiceReport(
                name=f"Database ({db_type})",
                status=ServiceStatus.HEALTHY,
                message="اتصال ناجح",
                details={"url": url.split("@")[-1] if "@" in url else url}
            )
            
        except Exception as e:
            return ServiceReport(
                name=f"Database ({db_type})",
                status=ServiceStatus.FAILED,
                message=f"خطأ اتصال: {str(e)[:80]}",
                action_taken="تحقق من تشغيل الخدمة وبيانات الاعتماد"
            )
    
    async def check_external_apis(self) -> List[ServiceReport]:
        """التحقق من واجهات API الخارجية"""
        reports = []
        
        for name, url in self.api_endpoints.items():
            try:
                response = await asyncio.to_thread(
                    requests.get, url, timeout=10,
                    headers={"User-Agent": "TopTire-Agent/1.0"}
                )
                
                if response.status_code == 200:
                    reports.append(ServiceReport(
                        name=f"API {name}",
                        status=ServiceStatus.HEALTHY,
                        message=f"استجابة سريعة ({response.elapsed.total_seconds():.2f}s)",
                        details={"status": response.status_code}
                    ))
                else:
                    reports.append(ServiceReport(
                        name=f"API {name}",
                        status=ServiceStatus.DEGRADED,
                        message=f"رد غير متوقع: {response.status_code}",
                        action_taken="تحقق من حدود معدل الطلبات"
                    ))
                    
            except Exception as e:
                reports.append(ServiceReport(
                    name=f"API {name}",
                    status=ServiceStatus.FAILED,
                    message=f"فشل الاتصال: {str(e)[:50]}",
                    action_taken="تحقق من جدار الحماية والشبكة"
                ))
        
        return reports
    
    async def validate_all(self) -> Dict[str, Any]:
        """التحقق الذكي الشامل"""
        print("🚀 بدء عملية التحقق الذكية...\n")
        
        # تشغيل جميع الفحوصات بالتوازي
        tasks = [
            self.check_openai(),
            self.check_database("PostgreSQL", "DB_URL"),
            self.check_database("Redis", "REDIS_URL"),
            self.check_external_apis()
        ]
        
        results = await asyncio.gather(*tasks)
        
        # تسطيح النتائج
        for result in results:
            if isinstance(result, list):
                self.reports.extend(result)
            elif isinstance(result, ServiceReport):
                self.reports.append(result)
        
        return self.generate_confirmation()
    
    def generate_confirmation(self) -> Dict[str, Any]:
        """توليد تأكيد نهائي والتوصيات"""
        summary = {
            "total": len(self.reports),
            "healthy": sum(1 for r in self.reports if r.status == ServiceStatus.HEALTHY),
            "failed": sum(1 for r in self.reports if r.status == ServiceStatus.FAILED),
            "missing": sum(1 for r in self.reports if r.status == ServiceStatus.MISSING),
        }
        
        # تحليل الذكاء الاصطناعي للمشكلات
        recommendations = []
        
        if summary["missing"] > 0:
            recommendations.append("🔑 إعداد المفاتيح المفقودة في ملف .env")
        
        if summary["failed"] > 0:
            recommendations.append("🔧 تشغيل الخدمات المتوقفة والتحقق من الشبكة")
        
        if summary["healthy"] == summary["total"]:
            recommendations.append("✅ جميع الخدمات تعمل بشكل مثالي - جاهز للإنتاج")
        
        import time
        return {
            "status": "SUCCESS" if summary["failed"] == 0 else "NEEDS_ATTENTION",
            "summary": summary,
            "reports": [
                {
                    "name": r.name,
                    "status": r.status.value,
                    "message": r.message,
                    "details": r.details,
                    "action_taken": r.action_taken
                }
                for r in self.reports
            ],
            "recommendations": recommendations,
            "timestamp": time.time()
        }

def print_confirmation(conf: Dict[str, Any]):
    """طباعة التأكيد النهائي"""
    print("\n" + "="*60)
    print("📋 تقرير التحقق النهائي - TopTire AI Agent")
    print("="*60)
    
    summary = conf["summary"]
    print(f"\n📊 الملخص: {summary['healthy']}/{summary['total']} خدمة صحيحة")
    
    if summary["missing"] > 0:
        print(f"🔑 مفاتيح مفقودة: {summary['missing']}")
    if summary["failed"] > 0:
        print(f"❌ خدمات متوقفة: {summary['failed']}")
    
    print("\n🔍 التفاصيل:")
    for report in conf["reports"]:
        print(f"  {report['status']} {report['name']}: {report['message']}")
        if report['action_taken']:
            print(f"     💡 إجراء: {report['action_taken']}")
    
    print("\n🎯 التوصيات:")
    for rec in conf["recommendations"]:
        print(f"  {rec}")
    
    print("\n" + "="*60)
    status_emoji = "✅" if conf["status"] == "SUCCESS" else "⚠️"
    print(f"{status_emoji} الحالة النهائية: {conf['status']}")
    print("="*60 + "\n")

async def main():
    """الدالة الرئيسية"""
    # تهيئة الوكيل
    agent = SmartAgentValidator(auto_fix=True)
    
    # التحقق الشامل
    confirmation = await agent.validate_all()
    
    # طباعة التأكيد
    print_confirmation(confirmation)
    
    # حفظ تقرير JSON
    with open("agent_health_report.json", "w") as f:
        json.dump(confirmation, f, indent=2, default=str)
    
    print("💾 تم حفظ التقرير في: agent_health_report.json")
    
    # خروج بناءً على الحالة
    sys.exit(0 if confirmation["status"] == "SUCCESS" else 1)

if __name__ == "__main__":
    asyncio.run(main())
