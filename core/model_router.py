"""
Model Router for Top-TieR Global HUB AI
Determines appropriate model based on task type and input size for cost optimization
"""
import logging
import re
from enum import Enum
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Enumeration of task types for model routing"""
    EXTRACTION = "extraction"
    CLASSIFICATION = "classification"
    NORMALIZATION = "normalization"
    SUMMARY = "summary"
    REPORT = "report"
    OSINT_QUERY = "osint_query"
    CONVERSATION = "conversation"


class ModelSize(Enum):
    """Model size categories for cost optimization"""
    SMALL = "small"   # < 2k tokens, fast and cheap
    MEDIUM = "medium" # 2k-6k tokens, balanced
    LARGE = "large"   # > 6k tokens or complex tasks


class ModelRouter:
    """Intelligent model routing for cost optimization and performance"""
    
    def __init__(self):
        """Initialize model router with predefined mappings"""
        # Model mappings by size category
        self.models = {
            ModelSize.SMALL: {
                "primary": "gpt-3.5-turbo",
                "alternatives": ["gpt-3.5-turbo-16k"],
                "max_tokens": 2000,
                "cost_per_1k": 0.0015  # Approximate cost
            },
            ModelSize.MEDIUM: {
                "primary": "gpt-3.5-turbo-16k", 
                "alternatives": ["gpt-4", "gpt-3.5-turbo"],
                "max_tokens": 6000,
                "cost_per_1k": 0.003
            },
            ModelSize.LARGE: {
                "primary": "gpt-4",
                "alternatives": ["gpt-4-32k", "gpt-3.5-turbo-16k"],
                "max_tokens": 16000,
                "cost_per_1k": 0.03
            }
        }
        
        # Task type to model size mapping
        self.task_routing = {
            TaskType.EXTRACTION: ModelSize.SMALL,
            TaskType.CLASSIFICATION: ModelSize.SMALL,
            TaskType.NORMALIZATION: ModelSize.SMALL,
            TaskType.SUMMARY: ModelSize.MEDIUM,
            TaskType.REPORT: ModelSize.LARGE,
            TaskType.OSINT_QUERY: ModelSize.MEDIUM,
            TaskType.CONVERSATION: ModelSize.SMALL
        }
        
        # Keywords for task type detection
        self.task_keywords = {
            TaskType.EXTRACTION: ["extract", "find", "identify", "locate", "parse"],
            TaskType.CLASSIFICATION: ["classify", "categorize", "type", "kind", "category"],
            TaskType.NORMALIZATION: ["normalize", "clean", "format", "standardize"],
            TaskType.SUMMARY: ["summarize", "summary", "overview", "brief", "digest"],
            TaskType.REPORT: ["report", "analysis", "detailed", "comprehensive", "full"],
            TaskType.OSINT_QUERY: ["osint", "investigate", "research", "intelligence"],
            TaskType.CONVERSATION: ["chat", "talk", "discuss", "conversation"]
        }
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation)"""
        # Rough estimation: ~4 characters per token for English text
        return len(text) // 4 + len(text.split()) // 2
    
    def detect_task_type(self, query: str, scope: Optional[List[str]] = None) -> TaskType:
        """Detect task type from query text and scope"""
        query_lower = query.lower()
        
        # Check scope first
        if scope:
            scope_str = " ".join(scope).lower()
            if "osint" in scope_str:
                return TaskType.OSINT_QUERY
        
        # Count keyword matches for each task type
        task_scores = {}
        for task_type, keywords in self.task_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                task_scores[task_type] = score
        
        # Return task type with highest score, default to conversation
        if task_scores:
            return max(task_scores.items(), key=lambda x: x[1])[0]
        
        return TaskType.CONVERSATION
    
    def select_model_size(self, query: str, task_type: TaskType, force_size: Optional[ModelSize] = None) -> ModelSize:
        """Select model size based on query complexity and task type"""
        if force_size:
            return force_size
        
        token_count = self.estimate_tokens(query)
        
        # Token-based size selection with task type consideration
        if token_count < 500:
            base_size = ModelSize.SMALL
        elif token_count < 2000:
            base_size = ModelSize.SMALL if task_type in [TaskType.EXTRACTION, TaskType.CLASSIFICATION] else ModelSize.MEDIUM
        elif token_count < 6000:
            base_size = ModelSize.MEDIUM
        else:
            base_size = ModelSize.LARGE
        
        # Task type override
        task_preferred_size = self.task_routing.get(task_type, ModelSize.SMALL)
        
        # Use larger of token-based and task-based size
        size_order = [ModelSize.SMALL, ModelSize.MEDIUM, ModelSize.LARGE]
        base_idx = size_order.index(base_size)
        task_idx = size_order.index(task_preferred_size)
        
        return size_order[max(base_idx, task_idx)]
    
    def route_model(
        self, 
        query: str, 
        scope: Optional[List[str]] = None,
        preferred_model: Optional[str] = None,
        cost_limit: Optional[float] = None
    ) -> Dict[str, any]:
        """
        Route to appropriate model based on query analysis
        
        Args:
            query: The input query text
            scope: Optional scope list (e.g., ["osint"])
            preferred_model: Optional specific model preference
            cost_limit: Optional cost ceiling for downgrading
            
        Returns:
            Dict with model selection details
        """
        # Detect task type
        task_type = self.detect_task_type(query, scope)
        logger.info(f"Detected task type: {task_type.value}")
        
        # Select model size
        model_size = self.select_model_size(query, task_type)
        logger.info(f"Selected model size: {model_size.value}")
        
        # Get model configuration
        model_config = self.models[model_size]
        selected_model = preferred_model or model_config["primary"]
        
        # Cost-based downgrading
        estimated_tokens = self.estimate_tokens(query)
        estimated_cost = (estimated_tokens / 1000) * model_config["cost_per_1k"]
        
        if cost_limit and estimated_cost > cost_limit:
            logger.warning(f"Cost limit exceeded ({estimated_cost:.4f} > {cost_limit:.4f}), downgrading")
            # Downgrade to smaller model
            if model_size == ModelSize.LARGE:
                model_size = ModelSize.MEDIUM
            elif model_size == ModelSize.MEDIUM:
                model_size = ModelSize.SMALL
            
            model_config = self.models[model_size]
            selected_model = model_config["primary"]
            estimated_cost = (estimated_tokens / 1000) * model_config["cost_per_1k"]
        
        # Check if we need map-reduce for large inputs
        needs_map_reduce = estimated_tokens > 6000 and task_type == TaskType.SUMMARY
        
        return {
            "model": selected_model,
            "model_size": model_size.value,
            "task_type": task_type.value,
            "estimated_tokens": estimated_tokens,
            "estimated_cost": estimated_cost,
            "max_tokens": model_config["max_tokens"],
            "needs_map_reduce": needs_map_reduce,
            "alternatives": model_config["alternatives"],
            "routing_reason": f"Task: {task_type.value}, Size: {model_size.value}, Tokens: {estimated_tokens}"
        }
    
    def should_enable_streaming(self, task_type: TaskType, estimated_tokens: int) -> bool:
        """Determine if streaming should be enabled for this request"""
        # Enable streaming for longer responses or conversation tasks
        return (
            task_type in [TaskType.CONVERSATION, TaskType.REPORT, TaskType.SUMMARY] or
            estimated_tokens > 1000
        )
    
    def get_model_stats(self) -> Dict[str, any]:
        """Get model routing statistics"""
        return {
            "available_models": {
                size.value: config for size, config in self.models.items()
            },
            "task_mappings": {
                task.value: size.value for task, size in self.task_routing.items()
            },
            "supported_tasks": [task.value for task in TaskType]
        }


# Global router instance
model_router = ModelRouter()