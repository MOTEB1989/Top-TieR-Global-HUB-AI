import os
import requests

# مفاتيح البيئة
token = os.environ["GITHUB_TOKEN"]
repo = os.environ["GITHUB_REPOSITORY"]
pr_number = os.environ.get("GITHUB_REF").split("/")[-1]

api_key = os.environ.get("API_KEY1") or os.environ.get("API_KEY2")

# نجيب تغييرات الـ PR
url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
headers = {"Authorization": f"token {token}"}
files = requests.get(url, headers=headers).json()

diffs = "\n\n".join(f["patch"] for f in files if "patch" in f)

# استدعاء موديل مفتوح المصدر عبر Hugging Face Inference API
# تقدر تغير model_id لأي موديل تحب مثل "mistralai/Mistral-7B-Instruct-v0.2"
model_id = "codellama/CodeLlama-7b-Instruct-hf"
hf_url = f"https://api-inference.huggingface.co/models/{model_id}"
hf_headers = {"Authorization": f"Bearer {api_key}"}

payload = {
    "inputs": f"راجع هذا الكود وأعطِ ملاحظات قصيرة:\n\n{diffs}",
    "parameters": {"max_new_tokens": 300}
}

response = requests.post(hf_url, headers=hf_headers, json=payload)

try:
    review_comment = response.json()[0]["generated_text"].strip()
except Exception:
    review_comment = "⚠️ لم أتمكن من توليد مراجعة تلقائية."

# نكتب تعليق على الـ PR
comment_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
requests.post(comment_url, headers=headers, json={"body": review_comment})
