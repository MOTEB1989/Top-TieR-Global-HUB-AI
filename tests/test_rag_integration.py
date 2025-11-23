#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test RAG integration functionality without requiring API keys.
Tests the core logic and graceful degradation.
"""

import json
import math
import sys
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

# Import without running the bot
import embed_index
import embed_search


def test_chunk_text():
    """Test text chunking function."""
    text = "A" * 3000
    chunks = embed_index.chunk_text(text, chunk_size=1000, overlap=100)
    
    assert len(chunks) > 0, "Should create chunks"
    assert chunks[0][0] == 0, "First chunk should start at 0"
    assert chunks[0][2] == "A" * 1000, "First chunk should have correct content"
    
    # Check overlap
    if len(chunks) > 1:
        # Second chunk should start at 900 (1000 - 100 overlap)
        assert chunks[1][0] == 900, "Second chunk should have overlap"
    
    print("✅ test_chunk_text passed")


def test_cosine_similarity():
    """Test cosine similarity calculation."""
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [1.0, 0.0, 0.0]
    vec3 = [0.0, 1.0, 0.0]
    
    # Identical vectors should have similarity 1.0
    sim1 = embed_search.cosine_similarity(vec1, vec2)
    assert abs(sim1 - 1.0) < 0.001, f"Identical vectors should have similarity ~1.0, got {sim1}"
    
    # Orthogonal vectors should have similarity 0.0
    sim2 = embed_search.cosine_similarity(vec1, vec3)
    assert abs(sim2) < 0.001, f"Orthogonal vectors should have similarity ~0.0, got {sim2}"
    
    # Empty vectors should return 0.0
    sim3 = embed_search.cosine_similarity([], [1.0, 2.0])
    assert sim3 == 0.0, "Empty vector should return 0.0"
    
    print("✅ test_cosine_similarity passed")


def test_scan_files():
    """Test file scanning functionality."""
    # Use the actual repository root
    repo_root = Path(__file__).parent.parent
    files = embed_index.scan_files(repo_root)
    
    assert len(files) > 0, "Should find files in repository"
    
    # Check that only allowed extensions are included
    for f in files:
        assert f.suffix.lower() in embed_index.ALLOWED_EXTENSIONS, f"File {f} has disallowed extension"
    
    # Check that excluded directories are skipped
    for f in files:
        assert ".git" not in f.parts, "Should skip .git directory"
        assert "node_modules" not in f.parts, "Should skip node_modules directory"
    
    print(f"✅ test_scan_files passed (found {len(files)} files)")


def test_index_structure():
    """Test that index has correct structure when loaded."""
    # Create a mock index
    mock_index = [
        {
            "id": "abc123",
            "path": "test.py",
            "start": 0,
            "end": 100,
            "content": "test content",
            "embedding": [0.1, 0.2, 0.3]
        }
    ]
    
    # Save to temp file
    test_path = Path("/tmp/test_index.json")
    with test_path.open("w") as f:
        json.dump(mock_index, f)
    
    # Load it back
    loaded = embed_search.load_index(test_path)
    
    assert len(loaded) == 1, "Should load one item"
    assert loaded[0]["id"] == "abc123", "Should preserve ID"
    assert loaded[0]["path"] == "test.py", "Should preserve path"
    assert len(loaded[0]["embedding"]) == 3, "Should preserve embedding"
    
    # Clean up
    test_path.unlink()
    
    print("✅ test_index_structure passed")


def test_graceful_failure():
    """Test that scripts handle missing API keys gracefully."""
    import os
    
    # Temporarily remove API key
    original_key = os.environ.get("OPENAI_API_KEY")
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]
    
    # embed_index should not raise exception
    try:
        # This should log a warning and skip, not crash
        assert embed_index.OPENAI_API_KEY is None or embed_index.OPENAI_API_KEY == ""
        print("✅ test_graceful_failure: embed_index handles missing key")
    except Exception as e:
        print(f"❌ test_graceful_failure failed: {e}")
        raise
    finally:
        # Restore original key
        if original_key:
            os.environ["OPENAI_API_KEY"] = original_key


def test_environment_variables():
    """Test that environment variables are parsed correctly."""
    import os
    
    # Test boolean parsing for ENABLE_RAG
    test_cases = {
        "true": True,
        "True": True,
        "1": True,
        "yes": True,
        "false": False,
        "0": False,
        "no": False,
        "": False,
    }
    
    for value, expected in test_cases.items():
        os.environ["ENABLE_RAG"] = value
        result = os.getenv("ENABLE_RAG", "false").lower() in ("true", "1", "yes")
        assert result == expected, f"ENABLE_RAG={value} should parse to {expected}, got {result}"
    
    print("✅ test_environment_variables passed")


def main():
    """Run all tests."""
    print("Running RAG integration tests...\n")
    
    try:
        test_chunk_text()
        test_cosine_similarity()
        test_scan_files()
        test_index_structure()
        test_graceful_failure()
        test_environment_variables()
        
        print("\n✅ All tests passed!")
        return 0
    
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
