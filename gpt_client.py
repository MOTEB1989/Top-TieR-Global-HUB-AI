import os
from typing import Optional, Dict, Any

import openai
from pydantic import BaseModel


class GPTRequest(BaseModel):
    prompt: str
    model: str = "text-davinci-003"
    max_tokens: int = 100
    temperature: float = 0.7


class GPTResponse(BaseModel):
    text: str
    usage: Optional[Dict[str, Any]] = None
    model: str


class GPTClient:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize GPT client with API key from environment or parameter"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        openai.api_key = self.api_key
    
    async def generate_text(self, request: GPTRequest) -> GPTResponse:
        """Generate text using OpenAI GPT model"""
        try:
            response = openai.Completion.create(
                engine=request.model,
                prompt=request.prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
            )
            
            text = response.choices[0].text.strip()
            usage = response.get("usage", {})
            
            return GPTResponse(
                text=text,
                usage=usage,
                model=request.model
            )
            
        except Exception as e:
            raise Exception(f"GPT API error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if the client is properly configured"""
        return bool(self.api_key)