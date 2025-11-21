from typing import Dict

from .config import DB_PATH
from .embed import get_embedding
from .store import get_top_k_similar, init_db
from gateway.router import simple_chat


def rag_answer(question: str, top_k: int = 5, provider: str | None = None, model: str | None = None) -> Dict:
    init_db(DB_PATH)
    q_emb = get_embedding(question)
    contexts = get_top_k_similar(q_emb, top_k=top_k)

    context_text = "\n\n".join(
        f"[{c['path']}#chunk-{c['chunk_index']} score={c['score']:.3f}]\n{c['content']}"
        for c in contexts
    )

    prompt = (
        "You are a retrieval-augmented assistant. Use ONLY the context below "
        "to answer the question. If the context is insufficient, say so explicitly.\n\n"
        f"CONTEXT:\n{context_text}\n\n"
        f"QUESTION:\n{question}\n\n"
        "Answer in Arabic when the question is Arabic; otherwise respond in the question language."
    )

    answer_text = simple_chat(prompt, provider=provider, model=model)
    return {
        "question": question,
        "answer": answer_text,
        "contexts": contexts,
        "provider": provider,
        "model": model,
    }
