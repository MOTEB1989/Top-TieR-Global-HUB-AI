# LexCode – المساعد البرمجي الذكي

⚡ مشروع مفتوح المصدر يهدف إلى أن يكون شبيهًا بـ **Codex**:  
يسحب الملفات من مستودعات GitHub، يحللها، ويولّد مخرجات (شرح، إصلاح، توليد اختبارات) بشكل آلي.

---

## 🎯 الهدف
- مساعدة المطورين على **قراءة الكود** و**فهمه** بسهولة.  
- تقديم **شروح واختبارات** أوتوماتيكية.  
- **مراجعة Pull Requests** واقتراح تحسينات.  
- تتبّع استدعاءات الـ APIs داخل المشروع.

---

## ⚙️ كيفية العمل
1. **يسحب الملفات** من المستودع باستخدام GitHub API.  
2. **يفك التشفير** ويقرأ المحتوى.  
3. يرسلها إلى نموذج ذكي (GPT, LLaMA, Mistral …) للتحليل.  
4. **يرجع النتيجة** على شكل تعليق أو Issue أو تقرير.

---

## 🔑 الإعداد

### 1. أنشئ Personal Access Token من GitHub:
- ادخل إلى [Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens).  
- أنشئ Token جديد مع الصلاحيات:
  - `repo` (للوصول للملفات).  
  - `workflow` (لتشغيل Actions).

### 2. خزّن التوكن كمتحول بيئة:
```bash
export GITHUB_TOKEN="ضع_التوكن_هنا"
```

### 3. شغّل الكود الأولي لسحب ملف:
```python
import requests, base64

GITHUB_TOKEN = "ضع_التوكن_هنا"
REPO_OWNER = "اسم_الحساب"
REPO_NAME = "اسم_المستودع"
FILE_PATH = "المسار/الى/الملف.py"

url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
headers = {"Authorization": f"token {GITHUB_TOKEN}"}

response = requests.get(url, headers=headers)
if response.status_code == 200:
    content = response.json()
    file_content = base64.b64decode(content["content"]).decode("utf-8")
    print("📂 محتوى الملف:\n", file_content)
else:
    print("❌ فشل جلب الملف:", response.json())
```

---

## 🚀 التوسع القادم
- GitHub Actions Bot: يعلّق على كل Pull Request.  
- Code Review Module: يقترح تحسينات مع تعليمات واضحة.  
- Test Generator: يولّد Unit Tests تلقائيًا.  
- Trace Analyzer: يتبع استدعاءات APIs ويربطها بالملفات.
