import json
import os

import requests
from sentence_transformers import SentenceTransformer


def openai_chat(messages, model):
    import openai

    openai.api_key = os.getenv("LEXCODE_OPENAI_KEY")
    resp = openai.ChatCompletion.create(model=model, messages=messages, temperature=0.2)
    return resp["choices"][0]["message"]["content"]


def handle_process(config, data):
    model = config.get("model", "")
    op = config.get("operation", "chat")
    prompt = config.get("prompt", "")

    if model.startswith("gpt-"):
        content = openai_chat(
            messages=[
                {
                    "role": "system",
                    "content": prompt
                    or "Process the input and respond in structured JSON if applicable.",
                },
                {"role": "user", "content": json.dumps(data, ensure_ascii=False)},
            ],
            model=model,
        )
        print("🤖 OpenAI processed data")
        return content

    if model.startswith("huggingface/") and op == "embeddings":
        hf_model = model.split("/", 1)[-1]
        st_model = SentenceTransformer(hf_model)
        texts = data if isinstance(data, list) else [str(data)]
        emb = st_model.encode(texts, normalize_embeddings=True).tolist()
        print(f"🔡 HF embeddings generated for {len(texts)} texts")
        return emb

    print(f"⚠️ Unknown or unsupported processor (model={model}, operation={op})")
    return data
