import os
import openai

# مفتاح API من البيئة
openai.api_key = os.getenv("OPENAI_API_KEY")

def query_gpt(prompt: str, model: str = "gpt-4", max_tokens: int = 800, temperature: float = 0.7) -> str:
    """
    يرسل prompt إلى GPT ويعيد الاستجابة كنص.
    يعتمد واجهة ChatCompletion المستقرة لإصدار openai 0.27.x.
    """
    try:
        resp = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return resp["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {e}"