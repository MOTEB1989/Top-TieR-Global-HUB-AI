"""Central dispatcher for unified review operations."""
from __future__ import annotations

import argparse
from typing import Any, Dict, Optional

from review_engine import code_review, document_review, security_review


class ReviewEngine:
    """Dispatch review requests to the appropriate specialization."""

    def __init__(self, default_provider: Optional[str] = None, default_model: Optional[str] = None) -> None:
        self.gateway = self._load_gateway()
        self.default_provider = default_provider or getattr(self.gateway, "provider", None)
        self.default_model = default_model or getattr(self.gateway, "model", None)

    def _load_gateway(self) -> Any:
        try:
            import gateway  # type: ignore

            return gateway.get_gateway()  # type: ignore[attr-defined]
        except Exception:
            return None

    def run(
        self,
        review_type: str,
        input_text: str,
        metadata: Optional[Dict[str, Any]] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        normalized_type = review_type.lower()
        provider_choice = provider or self.default_provider
        model_choice = model or self.default_model

        if normalized_type == "code":
            return code_review.review_code(input_text, provider=provider_choice, model=model_choice, metadata=metadata)
        if normalized_type == "security":
            return security_review.review_security(input_text, provider=provider_choice, model=model_choice, metadata=metadata)
        if normalized_type == "document":
            return document_review.review_document(input_text, provider=provider_choice, model=model_choice, metadata=metadata)

        raise ValueError(f"Unsupported review type: {review_type}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Unified Review Engine CLI")
    parser.add_argument("--type", required=True, choices=["code", "security", "document"], help="Type of review to run")
    parser.add_argument("--content", required=True, help="Input text or code to review")
    parser.add_argument("--provider", help="Gateway provider override")
    parser.add_argument("--model", help="Model override")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    engine = ReviewEngine()
    result = engine.run(args.type, args.content, provider=args.provider, model=args.model)
    import json

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
