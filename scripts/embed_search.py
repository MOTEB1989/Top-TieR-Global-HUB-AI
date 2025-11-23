#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
embed_search.py

CLI utility to query the embeddings index for a given text prompt.
Computes embedding for the query, performs cosine similarity search,
and prints top-k JSON results.

Usage:
    python scripts/embed_search.py "your search query here"

Environment Variables:
- OPENAI_API_KEY (required): OpenAI API key
- EMBEDDING_MODEL (optional): Embedding model name, default: text-embedding-3-small
- EMBEDDING_INDEX_PATH (optional): Path to index, default: analysis/embeddings/index.json
- VECTOR_TOP_K (optional): Number of top results, default: 6
"""

import os
import sys
import json
import math
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple

import requests
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("embed_search")

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_INDEX_PATH = os.getenv("EMBEDDING_INDEX_PATH", "analysis/embeddings/index.json")
VECTOR_TOP_K = int(os.getenv("VECTOR_TOP_K", "6"))


def create_embedding(text: str) -> List[float]:
    """
    Create embedding for a single text using OpenAI API.
    Returns embedding vector.
    """
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is required")
    
    url = f"{OPENAI_BASE_URL.rstrip('/')}/embeddings"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": EMBEDDING_MODEL,
        "input": [text],
    }
    
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        
        return data["data"][0]["embedding"]
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to create embedding: {e}")
        raise


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    """
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)


def load_index(index_path: Path) -> List[Dict[str, Any]]:
    """Load embeddings index from JSON file."""
    if not index_path.exists():
        logger.error(f"Index file not found: {index_path}")
        return []
    
    try:
        with index_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load index: {e}")
        return []


def search_index(query: str, index: List[Dict[str, Any]], top_k: int = 6) -> List[Tuple[Dict[str, Any], float]]:
    """
    Search index for query and return top-k results with scores.
    Returns list of (chunk, score) tuples sorted by score descending.
    """
    if not index:
        logger.warning("Index is empty")
        return []
    
    # Create query embedding
    logger.info(f"Creating embedding for query: {query[:100]}...")
    query_embedding = create_embedding(query)
    
    # Calculate similarities
    results = []
    for chunk in index:
        if "embedding" not in chunk:
            continue
        
        similarity = cosine_similarity(query_embedding, chunk["embedding"])
        results.append((chunk, similarity))
    
    # Sort by similarity (highest first) and take top-k
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_k]


def format_result(chunk: Dict[str, Any], score: float, rank: int) -> Dict[str, Any]:
    """Format a search result for output."""
    return {
        "rank": rank,
        "score": round(score, 4),
        "path": chunk.get("path", "unknown"),
        "start": chunk.get("start", 0),
        "end": chunk.get("end", 0),
        "content_preview": chunk.get("content", "")[:200] + "..." if len(chunk.get("content", "")) > 200 else chunk.get("content", ""),
    }


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/embed_search.py \"your search query\"")
        print("\nEnvironment Variables:")
        print("  OPENAI_API_KEY       - Required: OpenAI API key")
        print("  EMBEDDING_MODEL      - Optional: Embedding model (default: text-embedding-3-small)")
        print("  EMBEDDING_INDEX_PATH - Optional: Index path (default: analysis/embeddings/index.json)")
        print("  VECTOR_TOP_K         - Optional: Number of results (default: 6)")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    
    logger.info("Starting vector search...")
    logger.info(f"Query: {query}")
    logger.info(f"Embedding model: {EMBEDDING_MODEL}")
    logger.info(f"Top K: {VECTOR_TOP_K}")
    
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY is not set")
        sys.exit(1)
    
    # Load index
    repo_root = Path(__file__).parent.parent
    index_path = Path(EMBEDDING_INDEX_PATH)
    if not index_path.is_absolute():
        index_path = repo_root / index_path
    
    logger.info(f"Loading index from: {index_path}")
    index = load_index(index_path)
    
    if not index:
        logger.error("No index loaded. Run embed_index.py first.")
        sys.exit(1)
    
    logger.info(f"Loaded {len(index)} chunks from index")
    
    # Search
    try:
        results = search_index(query, index, VECTOR_TOP_K)
        
        if not results:
            print("No results found.")
            sys.exit(0)
        
        # Format and print results
        output = {
            "query": query,
            "model": EMBEDDING_MODEL,
            "top_k": VECTOR_TOP_K,
            "results": [format_result(chunk, score, i + 1) for i, (chunk, score) in enumerate(results)]
        }
        
        print(json.dumps(output, ensure_ascii=False, indent=2))
        
        logger.info(f"✅ Found {len(results)} results")
    
    except Exception as e:
        logger.error(f"Search failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
