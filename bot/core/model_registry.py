#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
model_registry.py

Unified model/provider selection and registry.
سجل موحد للنماذج والموفرين.
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ModelInfo:
    """Information about a model."""
    name: str
    provider: str
    display_name: str
    description: str
    context_window: int
    supports_streaming: bool = False


class ModelRegistry:
    """Registry for available models and providers."""
    
    def __init__(self):
        self.models: Dict[str, ModelInfo] = {}
        self._register_default_models()
    
    def _register_default_models(self) -> None:
        """Register default models."""
        # OpenAI models
        self.register_model(ModelInfo(
            name="gpt-4o-mini",
            provider="openai",
            display_name="GPT-4o Mini",
            description="Fast and efficient OpenAI model",
            context_window=128000,
            supports_streaming=True
        ))
        
        self.register_model(ModelInfo(
            name="gpt-4o",
            provider="openai",
            display_name="GPT-4o",
            description="Most capable OpenAI model",
            context_window=128000,
            supports_streaming=True
        ))
        
        self.register_model(ModelInfo(
            name="gpt-4-turbo",
            provider="openai",
            display_name="GPT-4 Turbo",
            description="High performance GPT-4 variant",
            context_window=128000,
            supports_streaming=True
        ))
        
        # Anthropic models
        self.register_model(ModelInfo(
            name="claude-3-5-sonnet-20241022",
            provider="anthropic",
            display_name="Claude 3.5 Sonnet",
            description="Most intelligent Claude model",
            context_window=200000,
            supports_streaming=True
        ))
        
        self.register_model(ModelInfo(
            name="claude-3-haiku-20240307",
            provider="anthropic",
            display_name="Claude 3 Haiku",
            description="Fast and compact Claude model",
            context_window=200000,
            supports_streaming=True
        ))
        
        # Groq models
        self.register_model(ModelInfo(
            name="llama-3.1-70b-versatile",
            provider="groq",
            display_name="Llama 3.1 70B",
            description="Fast Llama inference via Groq",
            context_window=32000,
            supports_streaming=True
        ))
        
        self.register_model(ModelInfo(
            name="mixtral-8x7b-32768",
            provider="groq",
            display_name="Mixtral 8x7B",
            description="Mixture of experts model via Groq",
            context_window=32768,
            supports_streaming=True
        ))
        
        logger.info(f"[model_registry] Registered {len(self.models)} models")
    
    def register_model(self, model: ModelInfo) -> None:
        """Register a model."""
        self.models[model.name] = model
        logger.debug(f"[model_registry] Registered model: {model.name} ({model.provider})")
    
    def get_model(self, name: str) -> Optional[ModelInfo]:
        """Get model information."""
        return self.models.get(name)
    
    def list_models(self, provider: Optional[str] = None) -> List[ModelInfo]:
        """List all models, optionally filtered by provider."""
        if provider:
            return [m for m in self.models.values() if m.provider == provider]
        return list(self.models.values())
    
    def list_providers(self) -> List[str]:
        """List all unique providers."""
        return sorted(set(m.provider for m in self.models.values()))
    
    def get_default_model(self, provider: str = "openai") -> str:
        """Get default model for a provider."""
        defaults = {
            "openai": "gpt-4o-mini",
            "anthropic": "claude-3-5-sonnet-20241022",
            "groq": "llama-3.1-70b-versatile"
        }
        return defaults.get(provider, "gpt-4o-mini")
    
    def validate_model(self, model_name: str, provider: str) -> bool:
        """Validate if a model belongs to the specified provider."""
        model = self.get_model(model_name)
        if not model:
            return False
        return model.provider == provider
