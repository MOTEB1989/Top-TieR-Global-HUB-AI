#!/usr/bin/env python3
"""Index repository content into a Chroma vector store."""

import argparse
import json
from pathlib import Path
from typing import Iterable, List

import chromadb
from sentence_transformers import SentenceTransformer
from tqdm import tqdm


def iter_files(repo_root: Path, include_hidden: bool = False) -> Iterable[Path]:
    for path in repo_root.rglob('*'):
        if path.is_dir():
            continue
        if not include_hidden and any(part.startswith('.') for part in path.relative_to(repo_root).parts):
            continue
        if path.name == 'codex_status.txt':
            continue
        yield path


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        return path.read_text(encoding='utf-8', errors='ignore')


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    chunks: List[str] = []
    start = 0
    text_length = len(text)
    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - chunk_overlap
        if start < 0:
            start = 0
        if start == end:
            start += chunk_size
    return chunks


def build_collection(repo_root: Path, output_dir: Path, chunk_size: int, chunk_overlap: int, model_name: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(output_dir))
    collection = client.get_or_create_collection(name='lexcode-repo', metadata={'hnsw:space': 'cosine'})

    model = SentenceTransformer(model_name)

    all_documents: List[str] = []
    all_metadatas: List[dict] = []
    all_ids: List[str] = []

    files = list(iter_files(repo_root))

    progress = tqdm(files, desc='Indexing files', unit='file')
    for file_index, file_path in enumerate(progress):
        text = read_text(file_path)
        chunks = chunk_text(text, chunk_size, chunk_overlap)
        for chunk_index, chunk in enumerate(chunks):
            chunk_id = f"{file_index}-{chunk_index}"
            all_ids.append(chunk_id)
            all_documents.append(chunk)
            all_metadatas.append({
                'path': str(file_path.relative_to(repo_root)),
                'chunk_index': chunk_index,
            })

    if not all_documents:
        print('No textual content discovered; nothing to index.')
        return

    embeddings = model.encode(all_documents, show_progress_bar=True, convert_to_numpy=True)

    collection.upsert(ids=all_ids, documents=all_documents, embeddings=embeddings.tolist(), metadatas=all_metadatas)

    manifest = {
        'repo_root': str(repo_root),
        'output_dir': str(output_dir),
        'total_files': len(files),
        'total_chunks': len(all_documents),
        'model_name': model_name,
        'chunk_size': chunk_size,
        'chunk_overlap': chunk_overlap,
    }

    manifest_path = output_dir / 'manifest.json'
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"Indexed {len(all_documents)} chunks from {len(files)} files. Manifest saved to {manifest_path}.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, default=Path('.'), help='Path to the repository root')
    parser.add_argument('--output-dir', type=Path, default=Path('.kb_store'), help='Directory to store the Chroma DB')
    parser.add_argument('--chunk-size', type=int, default=800, help='Number of characters per chunk')
    parser.add_argument('--chunk-overlap', type=int, default=200, help='Number of overlapping characters between chunks')
    parser.add_argument('--model-name', type=str, default='sentence-transformers/all-MiniLM-L6-v2', help='SentenceTransformer model')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_collection(args.repo_root.resolve(), args.output_dir.resolve(), args.chunk_size, args.chunk_overlap, args.model_name)


if __name__ == '__main__':
    main()
