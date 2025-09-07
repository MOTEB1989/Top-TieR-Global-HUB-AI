"""
GPT Client for Top-TieR Global HUB AI API
Provides OpenAI GPT integration with proper error handling.
"""

import os
from typing import Dict, Any, Optional
import openai


class GPTClient:
    """Client for OpenAI GPT API integration."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize GPT client with API key."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
        
    def is_configured(self) -> bool:
        """Check if GPT client is properly configured with API key."""
        return bool(self.api_key)
    
    async def generate_response(self, prompt: str, max_tokens: int = 150) -> Dict[str, Any]:
        """
        Generate a response using OpenAI GPT.
        
        Args:
            prompt: The input prompt for GPT
            max_tokens: Maximum number of tokens in the response
            
        Returns:
            Dictionary containing the response or error information
        """
        if not self.is_configured():
            return {
                "error": "OpenAI API key not configured",
                "message": "Please set OPENAI_API_KEY environment variable"
            }
        
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=0.7,
                n=1,
                stop=None
            )
            
            return {
                "success": True,
                "response": response.choices[0].text.strip(),
                "usage": response.usage
            }
            
        except openai.error.AuthenticationError:
            return {
                "error": "Authentication failed",
                "message": "Invalid OpenAI API key"
            }
        except openai.error.RateLimitError:
            return {
                "error": "Rate limit exceeded",
                "message": "Please try again later"
            }
        except openai.error.APIError as e:
            return {
                "error": "OpenAI API error",
                "message": str(e)
            }
        except Exception as e:
            return {
                "error": "Unexpected error",
                "message": str(e)
            }


# Global GPT client instance
gpt_client = GPTClient()