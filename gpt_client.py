import os
from typing import Optional, Dict, Any

import openai
from pydantic import BaseModel


class GPTRequest(BaseModel):
    """Request model for GPT endpoint"""
    prompt: str
    max_tokens: Optional[int] = 150
    temperature: Optional[float] = 0.7
    model: Optional[str] = "gpt-3.5-turbo"


class GPTResponse(BaseModel):
    """Response model for GPT endpoint"""
    response: str
    usage: Dict[str, Any]
    model: str


class GPTClient:
    """OpenAI GPT client for the Top-TieR Global HUB AI API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize GPT client with API key"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
        
    def is_available(self) -> bool:
        """Check if GPT client is available (has API key)"""
        return bool(self.api_key)
    
    async def generate_response(self, request: GPTRequest) -> GPTResponse:
        """Generate response using OpenAI GPT"""
        if not self.is_available():
            raise ValueError("OpenAI API key not configured")
        
        try:
            # Use the older openai v0.27.10 API format
            response = openai.Completion.create(
                engine=request.model if request.model != "gpt-3.5-turbo" else "text-davinci-003",
                prompt=request.prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )
            
            return GPTResponse(
                response=response.choices[0].text.strip(),
                usage=response.usage,
                model=response.model
            )
            
        except Exception as e:
            raise RuntimeError(f"GPT API error: {str(e)}")


# Global client instance
gpt_client = GPTClient()


def main():
    """Health check main function for OpenAI API availability"""
    print("🔍 Running OpenAI Health Check...")
    
    client = GPTClient()
    if not client.is_available():
        print("❌ OpenAI API key not configured")
        exit(1)
    
    try:
        # Simple test to verify API connectivity
        import asyncio
        from gpt_client import GPTRequest
        
        async def test_connection():
            request = GPTRequest(
                prompt="Say 'OK' if you can hear me",
                max_tokens=5,
                temperature=0.1
            )
            response = await client.generate_response(request)
            return response
        
        response = asyncio.run(test_connection())
        print(f"✅ OpenAI API connection successful: {response.response}")
        exit(0)
        
    except Exception as e:
        print(f"❌ OpenAI API health check failed: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()