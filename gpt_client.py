"""
Backward compatibility shim for gpt_client module.
This file provides the same interface as before, but imports from the new search_hub structure.
"""

# Import everything from the new location
from search_hub.gpt.client import (
    GPTClient,
    GPTRequest, 
    GPTResponse,
    gpt_client
)

# Export all the same symbols for backward compatibility
__all__ = ['GPTClient', 'GPTRequest', 'GPTResponse', 'gpt_client']