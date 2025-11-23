#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo script showing RAG workflow without requiring API keys.
Demonstrates the core functionality using mock embeddings.
"""

import json
import math
from pathlib import Path
from typing import List, Dict, Any

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    if not vec1 or not vec2:
        return 0.0
    
    min_len = min(len(vec1), len(vec2))
    vec1 = vec1[:min_len]
    vec2 = vec2[:min_len]
    
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)


def create_mock_index():
    """Create a mock embeddings index for demonstration."""
    mock_index = [
        {
            "id": "chunk001",
            "path": "scripts/telegram_chatgpt_mode.py",
            "start": 0,
            "end": 500,
            "content": "Telegram bot with ChatGPT functionality. Includes authentication, chat history, and OpenAI integration.",
            "embedding": [0.8, 0.2, 0.1, 0.3, 0.5]
        },
        {
            "id": "chunk002",
            "path": "scripts/embed_index.py",
            "start": 0,
            "end": 600,
            "content": "Build embeddings index by scanning repository files, chunking them, and creating vector embeddings using OpenAI API.",
            "embedding": [0.7, 0.4, 0.3, 0.2, 0.1]
        },
        {
            "id": "chunk003",
            "path": "README.md",
            "start": 0,
            "end": 400,
            "content": "LexCode Hybrid Stack - Rust core, Node.js API gateway, Python adapters for AI and data connections.",
            "embedding": [0.1, 0.8, 0.5, 0.2, 0.4]
        },
        {
            "id": "chunk004",
            "path": "tests/test_rag_integration.py",
            "start": 0,
            "end": 550,
            "content": "Test RAG integration: chunking, embeddings, cosine similarity, file scanning, and graceful failure handling.",
            "embedding": [0.6, 0.3, 0.7, 0.5, 0.2]
        }
    ]
    return mock_index


def search_mock_index(query_text: str, query_embedding: List[float], index: List[Dict], top_k: int = 3):
    """Search mock index using query embedding."""
    results = []
    for chunk in index:
        similarity = cosine_similarity(query_embedding, chunk["embedding"])
        results.append((chunk, similarity))
    
    # Sort by similarity (highest first) and take top-k
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_k]


def main():
    """Demonstrate RAG workflow."""
    print("=" * 80)
    print("RAG Workflow Demonstration")
    print("=" * 80)
    
    # Step 1: Create mock index
    print("\n1. Creating mock embeddings index...")
    index = create_mock_index()
    print(f"   ✅ Created index with {len(index)} chunks")
    
    # Step 2: Simulate different queries
    queries = [
        {
            "text": "How does the Telegram bot work?",
            "embedding": [0.75, 0.25, 0.15, 0.3, 0.4]  # Similar to chunk001
        },
        {
            "text": "How to build embeddings?",
            "embedding": [0.65, 0.35, 0.25, 0.2, 0.15]  # Similar to chunk002
        },
        {
            "text": "Testing and validation",
            "embedding": [0.55, 0.3, 0.65, 0.45, 0.2]  # Similar to chunk004
        }
    ]
    
    print("\n2. Running vector similarity searches...")
    for i, query in enumerate(queries, 1):
        print(f"\n   Query {i}: '{query['text']}'")
        results = search_mock_index(query['text'], query['embedding'], index, top_k=2)
        
        for rank, (chunk, score) in enumerate(results, 1):
            print(f"   [{rank}] {chunk['path']} (score: {score:.3f})")
            print(f"       {chunk['content'][:80]}...")
    
    # Step 3: Show context injection simulation
    print("\n3. Simulating context injection for /chat...")
    chat_query = "Explain authentication in the bot"
    chat_embedding = [0.8, 0.2, 0.1, 0.3, 0.5]
    
    print(f"   User query: '{chat_query}'")
    print(f"   Retrieving top 2 relevant chunks...")
    
    context_chunks = search_mock_index(chat_query, chat_embedding, index, top_k=2)
    
    print("\n   📄 Retrieved context:")
    for rank, (chunk, score) in enumerate(context_chunks, 1):
        print(f"   [{rank}] {chunk['path']} (score: {score:.3f})")
        print(f"       {chunk['content']}")
    
    print("\n   This context would be injected into the chat message before sending to OpenAI.")
    
    # Step 4: Summary
    print("\n" + "=" * 80)
    print("✅ RAG Workflow Complete!")
    print("=" * 80)
    print("\nKey Features Demonstrated:")
    print("  • Embeddings index structure (chunks with metadata)")
    print("  • Vector similarity search using cosine similarity")
    print("  • Top-K retrieval for relevant chunks")
    print("  • Context injection for enhanced chat responses")
    print("\nIn production:")
    print("  • Real embeddings created via OpenAI API")
    print("  • Index built automatically on Railway deployment")
    print("  • /search command allows direct querying")
    print("  • /chat uses RAG when ENABLE_RAG=true")
    print()


if __name__ == "__main__":
    main()
