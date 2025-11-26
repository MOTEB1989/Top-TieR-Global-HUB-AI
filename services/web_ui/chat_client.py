"""Lightweight client for sending chat history to the LLM gateway.

This module keeps external dependencies minimal and intentionally avoids
framework-specific code to keep the Streamlit app small and focused.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import requests


class ChatClient:
    """HTTP client used by the Streamlit chat UI to talk to the gateway.

    The gateway URL can be overridden with the ``GATEWAY_URL`` environment
    variable. We append ``/v1/ai/infer`` to this base to build the final
    endpoint. The expected payload matches the OpenAI Chat Completions style
    where ``messages`` is a list of ``{"role": "user"|"assistant", "content": str}``.
    """

    def __init__(self, gateway_url: Optional[str] = None) -> None:
        base_url = gateway_url or os.getenv("GATEWAY_URL", "http://gateway:3000")
        self.gateway_url = base_url.rstrip("/")
        self.infer_endpoint = f"{self.gateway_url}/v1/ai/infer"

    def send_messages(
        self, messages: List[Dict[str, str]], mode: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send the full conversation to the LLM gateway.

        Args:
            messages: Chat history in OpenAI-like format.
            mode: Optional persona/mode hint. Left as a simple string while
                backend support is clarified (see TODO in ``app.py``).

        Returns:
            A dictionary with keys ``content`` (assistant text) and optional
            ``context``/``sources`` passed through from the backend. On error
            a friendly message is returned instead of raising.
        """

        payload: Dict[str, Any] = {"messages": messages}
        if mode:
            # TODO: Wire the persona/mode into the gateway once the contract is defined.
            payload["mode"] = mode

        try:
            response = requests.post(self.infer_endpoint, json=payload, timeout=30)
            response.raise_for_status()
            data: Dict[str, Any] = response.json()
        except requests.RequestException as exc:  # network or HTTP errors
            return {
                "content": (
                    "Sorry, I couldn't reach the AI gateway right now. "
                    "Please check the GATEWAY_URL setting and try again."
                ),
                "error": str(exc),
            }
        except ValueError as exc:  # invalid JSON
            return {
                "content": "The gateway returned an unexpected response format.",
                "error": str(exc),
            }

        assistant_text = self._extract_content(data)
        context = data.get("context") or data.get("sources")
        return {"content": assistant_text, "context": context, "raw": data}

    @staticmethod
    def _extract_content(data: Dict[str, Any]) -> str:
        """Best-effort extraction of assistant text from various response shapes."""

        # Common OpenAI-compatible shape: {"choices": [{"message": {"content": "..."}}]}
        choices = data.get("choices")
        if isinstance(choices, list) and choices:
            first = choices[0]
            message = first.get("message") if isinstance(first, dict) else None
            if isinstance(message, dict) and "content" in message:
                return str(message.get("content", ""))

        for key in ("assistant", "message", "content", "reply", "text"):
            if key in data and isinstance(data[key], str):
                return data[key]

        # As a last resort, return a readable fallback.
        return "(No content received from gateway)"
