from typing import Optional

import httpx

from base_provider import BaseProvider


_DEFAULT_MODEL = "bigscience/bloom"


class HuggingFaceProvider(BaseProvider):
    """Inference provider backed by Hugging Face Inference Endpoints."""

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Hugging Face API key must be provided")
        self.api_key = api_key

    async def infer(self, prompt: str, model: Optional[str] = None) -> str:
        model_name = model or _DEFAULT_MODEL
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"inputs": prompt}
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"https://api-inference.huggingface.co/models/{model_name}",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        if isinstance(data, list):
            for item in data:
                generated = item.get("generated_text")
                if generated:
                    return generated
        elif isinstance(data, dict):
            generated = data.get("generated_text")
            if generated:
                return generated

        raise ValueError("Unexpected response format from Hugging Face API")
