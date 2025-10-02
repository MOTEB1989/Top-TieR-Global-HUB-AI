import os

import openai
from sentence_transformers import SentenceTransformer


def handle_process(config, data):
    model = config.get("model", "")

    if model.startswith("gpt"):
        openai.api_key = os.getenv("LEXCODE_OPENAI_KEY")
        prompt = config.get("prompt", "")
        resp = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": str(data)},
            ],
        )
        result = resp["choices"][0]["message"]["content"]
        print("🤖 GPT processed data")
        return result

    if model.startswith("huggingface"):
        operation = config.get("operation", "embeddings")
        if operation == "embeddings":
            hf_model = model.split("/", 1)[-1]
            embedding_model = SentenceTransformer(hf_model)
            embeddings = embedding_model.encode([str(data)])
            print("🔡 Generated embeddings with HF")
            return embeddings

    print(f"⚠️ Unknown model: {model}")
    return data
