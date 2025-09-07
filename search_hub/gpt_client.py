import os
import openai

# المفتاح من Secrets/البيئة
openai.api_key = os.getenv("OPENAI_API_KEY")

def query_gpt(prompt: str, model: str = "gpt-4", max_tokens: int = 200, temperature: float = 0.3) -> str:
    """
    يرسل prompt إلى GPT ويعيد الاستجابة كنص.
    يستخدم واجهة ChatCompletion المستقرة لإصدار openai 0.27.x.
    """
    try:
        resp = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        text = resp["choices"][0]["message"]["content"]
        return text[:2000]  # قص دفاعي
    except Exception as e:
        return f"Error: {e}"