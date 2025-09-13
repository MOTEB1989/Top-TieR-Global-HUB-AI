"""
Tests for model router functionality
"""
import pytest
from core.model_router import ModelRouter, TaskType, ModelSize


def test_model_router_init():
    """Test model router initialization"""
    router = ModelRouter()
    assert len(router.models) == 3
    assert ModelSize.SMALL in router.models
    assert ModelSize.MEDIUM in router.models
    assert ModelSize.LARGE in router.models


def test_estimate_tokens():
    """Test token estimation"""
    router = ModelRouter()
    
    # Short text should estimate fewer tokens
    short_text = "Hello world"
    short_tokens = router.estimate_tokens(short_text)
    
    # Long text should estimate more tokens
    long_text = "This is a much longer text " * 50
    long_tokens = router.estimate_tokens(long_text)
    
    assert long_tokens > short_tokens
    assert short_tokens > 0


def test_detect_task_type():
    """Test task type detection"""
    router = ModelRouter()
    
    # Test OSINT scope detection
    assert router.detect_task_type("test query", ["osint"]) == TaskType.OSINT_QUERY
    
    # Test keyword-based detection
    assert router.detect_task_type("extract phone numbers") == TaskType.EXTRACTION
    assert router.detect_task_type("classify this document") == TaskType.CLASSIFICATION
    assert router.detect_task_type("summarize the report") == TaskType.SUMMARY
    
    # Test default case
    assert router.detect_task_type("random chat message") == TaskType.CONVERSATION


def test_select_model_size():
    """Test model size selection"""
    router = ModelRouter()
    
    # Short extraction task should use SMALL
    short_extraction = "extract email"
    size = router.select_model_size(short_extraction, TaskType.EXTRACTION)
    assert size == ModelSize.SMALL
    
    # Very long text should upgrade size
    long_text = "analyze this document " * 500  # Much longer text
    size = router.select_model_size(long_text, TaskType.EXTRACTION)
    assert size in [ModelSize.MEDIUM, ModelSize.LARGE]
    
    # Report task should prefer LARGE
    size = router.select_model_size("short report", TaskType.REPORT)
    assert size == ModelSize.LARGE


def test_route_model():
    """Test complete model routing"""
    router = ModelRouter()
    
    # Test simple extraction
    result = router.route_model("extract phone numbers from text")
    assert result["model"] in ["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4"]
    assert result["task_type"] == TaskType.EXTRACTION.value
    assert "estimated_tokens" in result
    assert "estimated_cost" in result
    
    # Test OSINT query
    result = router.route_model("investigate this number", ["osint"])
    assert result["task_type"] == TaskType.OSINT_QUERY.value
    
    # Test preferred model override
    result = router.route_model("test", preferred_model="gpt-4")
    assert result["model"] == "gpt-4"


def test_should_enable_streaming():
    """Test streaming decision logic"""
    router = ModelRouter()
    
    # Long conversation should enable streaming
    assert router.should_enable_streaming(TaskType.CONVERSATION, 2000) is True
    
    # Short extraction shouldn't need streaming
    assert router.should_enable_streaming(TaskType.EXTRACTION, 100) is False
    
    # Reports should enable streaming
    assert router.should_enable_streaming(TaskType.REPORT, 500) is True


def test_get_model_stats():
    """Test model statistics"""
    router = ModelRouter()
    stats = router.get_model_stats()
    
    assert "available_models" in stats
    assert "task_mappings" in stats
    assert "supported_tasks" in stats
    
    assert len(stats["available_models"]) == 3
    assert len(stats["supported_tasks"]) == len(TaskType)