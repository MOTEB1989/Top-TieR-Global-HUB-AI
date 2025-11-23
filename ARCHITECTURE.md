# Top-TieR Global HUB AI – System Architecture  
إصدار: 1.0  
آخر تحديث: 2025-11-23  

## نظرة عامة  
يمثل النظام منصة تحليل وتشغيل وكلاء ذكاء اصطناعي متعددة المصادر، تعتمد على تكامل دقيق بين:  
- Python Adapters  
- برامج الفحص والتشخيص  
- سكربتات Bash  
- Redis / Neo4j  
- تكامل مع Telegram  
- دعم للنماذج الخارجية (OpenAI, Groq, Anthropic)

## البنية الأساسية  

┌────────────────────────────┐
│      Smart Agent Core      │
│  Python (validator, logic) │
└──────────────┬─────────────┘
│
┌──────────────▼─────────────┐
│   Connectors & Adapters    │
│  WHO • WorldBank • GitHub  │
│  Redis • Neo4j • Wikidata  │
└──────────────┬─────────────┘
│
┌──────────────▼─────────────┐
│  External AI Models        │
│ OpenAI • Groq • Anthropic  │
└──────────────┬─────────────┘
│
┌──────────────▼─────────────┐
│     User Interaction        │
│ Telegram Bot • CLI • REST   │
└─────────────────────────────┘

## مكوّنات رئيسية
- **scripts/**  
  تشغيل – فحص – إعداد – صحة النظام.
- **connectors/**  
  ربط مصادر البيانات.
- **src/providers/**  
  طبقة التجريد abstraction للمصادر.
- **.env**  
  مفاتيح API والتكوين.

## مسار البيانات  
1. ينفّذ المستخدم العملية (CLI أو Telegram).  
2. يمر النظام عبر validate_check_connections.  
3. يتم تجهيز البيئة ورفع الوكلاء.  
4. الذكاء المركزي smart_agent_validator يتعامل مع الردود والمصادر.  
5. يتم إرجاع نتيجة محسّنة مدعومة بالمصادر.
