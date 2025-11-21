import os
import sys
from typing import List, Tuple
from gateway.router import get_gateway

PROVIDERS: List[Tuple[str, str, str]] = [
    ("openai", "OPENAI_API_KEY", os.getenv("OPENAI_MODEL", "gpt-4.1")),
    ("groq", "GROQ_API_KEY", os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")),
]

def main() -> int:
    had_failure = False
    for provider, key_env, model in PROVIDERS:
        api_key = os.getenv(key_env)
        if not api_key:
            print(f"[SKIP] Provider={provider}: missing {key_env}, skipping validation.")
            continue
        try:
            print(f"[INFO] Validating provider={provider}, model={model}...")
            client = get_gateway(provider=provider, model=model)
            result = client.generate("ping")
            text = str(result.get("text", ""))[:80]
            print(f"[OK] {provider} responded with: {text!r}")
        except Exception as exc:  # noqa: BLE001
            had_failure = True
            print(f"[ERROR] Validation failed for provider={provider}: {exc!r}")
    if had_failure:
        print("[FAIL] One or more providers failed validation.")
        return 1
    print("[DONE] Gateway validation finished.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
