from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def generate_local_phi(prompt: str, model_path: str | None = None, max_tokens: int = 512, **kwargs: Any) -> str:
    """Stubbed Phi-3 runner that can be swapped with llama.cpp bindings.

    For production, replace the placeholder implementation with a call to a
    compiled llama.cpp binary. This function is intentionally lightweight to
    keep CI fast.
    """

    # Placeholder echo-style generation
    return f"[phi-3 mock] {prompt[:200]}..."


def main(argv: list[str] | None = None) -> None:  # pragma: no cover - CLI
    parser = argparse.ArgumentParser(description="Run local Phi-3 generation")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--model-path", type=Path, default=Path("./models/phi-3-mini-4k-q4.gguf"))
    parser.add_argument("--max-tokens", type=int, default=512)
    args = parser.parse_args(argv)

    output = generate_local_phi(args.prompt, model_path=str(args.model_path), max_tokens=args.max_tokens)
    print(json.dumps({"output": output}, ensure_ascii=False))


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
