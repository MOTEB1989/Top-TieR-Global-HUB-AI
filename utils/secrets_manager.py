"""Centralized secrets manager abstraction for the Top-TieR platform."""
from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class SecretRecord:
    """Represents a cached secret value."""

    value: Any
    fetched_at: float


class SecretManager:
    """Simple secrets manager supporting environment and Vault backends."""

    def __init__(self, cache_ttl: int = 300) -> None:
        self._backend = os.getenv("SECRETS_BACKEND", "env").lower()
        self._cache_ttl = cache_ttl
        self._cache: Dict[str, SecretRecord] = {}
        self._vault_client = None
        if self._backend == "vault":
            self._configure_vault()
        elif self._backend != "env":
            logger.warning("Unknown secrets backend '%s'; falling back to environment variables.", self._backend)
            self._backend = "env"

    # ------------------------------------------------------------------
    # Vault helpers
    # ------------------------------------------------------------------
    def _configure_vault(self) -> None:
        vault_addr = os.getenv("VAULT_ADDR")
        vault_token = os.getenv("VAULT_TOKEN")
        if not vault_addr or not vault_token:
            logger.warning("Vault backend selected but VAULT_ADDR/VAULT_TOKEN missing. Falling back to env backend.")
            self._backend = "env"
            return
        try:
            import hvac  # type: ignore
        except Exception as exc:  # pragma: no cover - defensive branch
            logger.error("hvac package required for Vault backend: %s", exc)
            self._backend = "env"
            return

        self._vault_client = hvac.Client(url=vault_addr, token=vault_token)
        if not self._vault_client.is_authenticated():  # pragma: no cover - network call
            raise RuntimeError("Failed to authenticate with Vault. Check token and policies.")
        logger.info("Vault backend initialised at %s", vault_addr)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get_secret(self, identifier: str, key: Optional[str] = None, default: Any | None = None) -> Any:
        """Retrieve a secret value.

        Parameters
        ----------
        identifier:
            Environment variable name or Vault secret path depending on backend.
        key:
            Optional key when retrieving nested Vault secrets.
        default:
            Default value if the secret is not present.
        """

        cache_key = f"{identifier}:{key or ''}"
        cached = self._cache.get(cache_key)
        if cached and (time.time() - cached.fetched_at) < self._cache_ttl:
            return cached.value

        value: Any = default
        if self._backend == "vault" and self._vault_client is not None:
            value = self._read_from_vault(identifier, key, default)
        else:
            env_name = identifier if identifier.isupper() else identifier.upper()
            value = os.getenv(env_name, default)

        self._cache[cache_key] = SecretRecord(value=value, fetched_at=time.time())
        return value

    def _read_from_vault(self, path: str, key: Optional[str], default: Any | None) -> Any:
        try:
            assert self._vault_client is not None
            response = self._vault_client.secrets.kv.v2.read_secret_version(path=path)  # type: ignore[attr-defined]
            data = response.get("data", {}).get("data", {})
            if key is None:
                return data or default
            return data.get(key, default)
        except Exception as exc:  # pragma: no cover - network call
            logger.error("Failed to read secret '%s' from Vault: %s", path, exc)
            return default

    def flush_cache(self) -> None:
        """Clear the in-memory cache."""

        self._cache.clear()

    # Convenience helpers -------------------------------------------------
    def get_json(self, identifier: str, key: Optional[str] = None, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Return a parsed JSON secret."""

        raw = self.get_secret(identifier, key=key, default=None)
        if raw is None:
            return default or {}
        if isinstance(raw, dict):
            return raw
        try:
            return json.loads(str(raw))
        except json.JSONDecodeError:
            logger.warning("Secret '%s' is not valid JSON; returning default", identifier)
            return default or {}


__all__ = ["SecretManager"]
