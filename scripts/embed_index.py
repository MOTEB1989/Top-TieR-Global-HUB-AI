#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
embed_index.py

Build an embeddings index of repository source/content files.
Scans allowed file extensions, chunks them, creates embeddings via OpenAI API,
and saves the index as JSON.

Environment Variables:
- OPENAI_API_KEY (required): OpenAI API key
- EMBEDDING_MODEL (optional): Embedding model name, default: text-embedding-3-small
- EMBEDDING_INDEX_PATH (optional): Path to save index, default: analysis/embeddings/index.json
- EMBEDDING_CHUNK_SIZE (optional): Characters per chunk, default: 1200
- EMBEDDING_CHUNK_OVERLAP (optional): Overlap characters, default: 150
- FILE_EXT_ALLOWLIST (optional): Comma-separated file extensions, default: .py,.ts,.md,.sh,.yaml,.yml,.txt,.json
- EMBEDDING_MAX_FILES (optional): Max files to process (0=unlimited), default: 0
"""

import os
import json
import logging
import hashlib
from pathlib import Path
from typing import List, Dict, Any

import requests
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("embed_index")

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_INDEX_PATH = os.getenv("EMBEDDING_INDEX_PATH", "analysis/embeddings/index.json")
EMBEDDING_CHUNK_SIZE = int(os.getenv("EMBEDDING_CHUNK_SIZE", "1200"))
EMBEDDING_CHUNK_OVERLAP = int(os.getenv("EMBEDDING_CHUNK_OVERLAP", "150"))
FILE_EXT_ALLOWLIST = os.getenv("FILE_EXT_ALLOWLIST", ".py,.ts,.md,.sh,.yaml,.yml,.txt,.json")
EMBEDDING_MAX_FILES = int(os.getenv("EMBEDDING_MAX_FILES", "0"))

# Parse allowlist
ALLOWED_EXTENSIONS = set(ext.strip() for ext in FILE_EXT_ALLOWLIST.split(",") if ext.strip())


def chunk_text(text: str, chunk_size: int, overlap: int) -> List[tuple]:
    """
    Split text into overlapping chunks.
    Returns list of (start_pos, end_pos, chunk_text).
    """
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append((start, min(end, text_len), chunk))
        
        # Move forward with overlap
        start += chunk_size - overlap
        if start >= text_len:
            break
    
    return chunks


def create_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Create embeddings for a batch of texts using OpenAI API.
    Returns list of embedding vectors.
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
        "input": texts,
    }
    
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        
        # Extract embeddings in order
        embeddings = []
        for item in data["data"]:
            embeddings.append(item["embedding"])
        
        return embeddings
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to create embeddings: {e}")
        return []


def scan_files(root_path: Path) -> List[Path]:
    """
    Scan repository for files matching allowed extensions.
    Skips common directories to exclude (.git, node_modules, etc.).
    """
    skip_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".pytest_cache"}
    files = []
    
    for item in root_path.rglob("*"):
        if item.is_file():
            # Skip if in excluded directory
            if any(skip_dir in item.parts for skip_dir in skip_dirs):
                continue
            
            # Check extension
            if item.suffix.lower() in ALLOWED_EXTENSIONS:
                files.append(item)
    
    return files


def build_index(root_path: Path) -> List[Dict[str, Any]]:
    """
    Build embeddings index from repository files.
    Returns list of chunk dictionaries with embeddings.
    """
    logger.info("Scanning repository for files...")
    files = scan_files(root_path)
    
    # Limit files if specified
    if EMBEDDING_MAX_FILES > 0:
        files = files[:EMBEDDING_MAX_FILES]
    
    logger.info(f"Found {len(files)} files to process")
    
    index = []
    batch_texts = []
    batch_metadata = []
    batch_size = 50  # Process in batches of 50
    
    for file_path in files:
        try:
            # Read file content
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            
            # Skip empty files
            if not content.strip():
                continue
            
            # Chunk the content
            chunks = chunk_text(content, EMBEDDING_CHUNK_SIZE, EMBEDDING_CHUNK_OVERLAP)
            
            for start, end, chunk_text in chunks:
                # Create unique chunk ID
                chunk_id = hashlib.md5(
                    f"{file_path}:{start}:{end}".encode()
                ).hexdigest()[:16]
                
                batch_texts.append(chunk_text)
                batch_metadata.append({
                    "id": chunk_id,
                    "path": str(file_path.relative_to(root_path)),
                    "start": start,
                    "end": end,
                    "content": chunk_text,
                })
                
                # Process batch when full
                if len(batch_texts) >= batch_size:
                    logger.info(f"Processing batch of {len(batch_texts)} chunks...")
                    embeddings = create_embeddings_batch(batch_texts)
                    
                    if embeddings:
                        for meta, emb in zip(batch_metadata, embeddings):
                            meta["embedding"] = emb
                            index.append(meta)
                    
                    batch_texts = []
                    batch_metadata = []
        
        except Exception as e:
            logger.warning(f"Skipping file {file_path}: {e}")
            continue
    
    # Process remaining batch
    if batch_texts:
        logger.info(f"Processing final batch of {len(batch_texts)} chunks...")
        embeddings = create_embeddings_batch(batch_texts)
        
        if embeddings:
            for meta, emb in zip(batch_metadata, embeddings):
                meta["embedding"] = emb
                index.append(meta)
    
    logger.info(f"Built index with {len(index)} chunks")
    return index


def save_index(index: List[Dict[str, Any]], output_path: Path) -> None:
    """Save index to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Saved index to {output_path}")


def main():
    """Main entry point."""
    logger.info("Starting embeddings index build...")
    logger.info(f"Embedding model: {EMBEDDING_MODEL}")
    logger.info(f"Chunk size: {EMBEDDING_CHUNK_SIZE}, Overlap: {EMBEDDING_CHUNK_OVERLAP}")
    logger.info(f"Allowed extensions: {ALLOWED_EXTENSIONS}")
    logger.info(f"Output path: {EMBEDDING_INDEX_PATH}")
    
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY is not set. Cannot build embeddings index.")
        logger.info("Skipping embeddings index build (RAG will be disabled).")
        return
    
    # Get repository root (parent of scripts directory)
    repo_root = Path(__file__).parent.parent
    
    try:
        index = build_index(repo_root)
        
        if not index:
            logger.warning("No chunks were indexed. Index will be empty.")
        
        output_path = Path(EMBEDDING_INDEX_PATH)
        if not output_path.is_absolute():
            output_path = repo_root / output_path
        
        save_index(index, output_path)
        logger.info("✅ Embeddings index build completed successfully")
    
    except Exception as e:
        logger.error(f"Failed to build embeddings index: {e}")
        logger.info("Creating empty index as fallback...")
        
        # Create empty index to avoid errors in bot
        output_path = Path(EMBEDDING_INDEX_PATH)
        if not output_path.is_absolute():
            output_path = repo_root / output_path
        
        save_index([], output_path)


if __name__ == "__main__":
    main()
