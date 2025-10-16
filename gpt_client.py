import os
import openai
from pydantic import BaseModel


class GPTRequest(BaseModel):
    prompt: str
    max_tokens: int = 150
    temperature: float = 0.7
    model: str = "gpt-3.5-turbo"
    user: str = "system"


class GPTResponse(BaseModel):
    response: str
    usage: dict
    model: str


class GPTClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key

    def is_available(self):
        return self.api_key is not None

    def send(self, request: GPTRequest) -> GPTResponse:
        try:
            response = openai.ChatCompletion.create(
                model=request.model,
                messages=[{"role": "user", "content": request.prompt}],
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                user=request.user
            )
            result = response["choices"][0]["message"]["content"]
            return GPTResponse(
                response=result,
                usage=response["usage"],
                model=response["model"]
            )
        except Exception as e:
            raise RuntimeError(f"GPT API error: {str(e)}") from e


# للتجربة المحلية
if __name__ == "__main__":
    client = GPTClient()
    if not client.is_available():
        print("❌ OpenAI API key not configured")
        exit(1)
    prompt = "Say hello from Codex!"
    response = client.send(GPTRequest(prompt=prompt))
    print(response.response)
