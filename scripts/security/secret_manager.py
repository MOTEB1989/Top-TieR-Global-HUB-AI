"""
Secret Management Module
Secure handling of API keys, tokens, and other secrets with key rotation support.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

from .encryption import DataEncryptor


class SecretManager:
    """
    Manages secrets securely with encryption and key rotation.
    
    Features:
    - Encrypted storage of secrets
    - Key rotation support
    - Expiration tracking
    - Environment variable integration
    """

    def __init__(
        self,
        encryption_key: Optional[str] = None,
        storage_path: Optional[str] = None
    ):
        """
        Initialize the secret manager.
        
        Args:
            encryption_key: Key for encrypting secrets (generated if not provided)
            storage_path: Path to store encrypted secrets file
        """
        # Initialize encryptor
        if encryption_key:
            self.encryptor = DataEncryptor(key=encryption_key.encode())
        else:
            # Try to get key from environment or generate new
            env_key = os.getenv("SECRET_ENCRYPTION_KEY")
            if env_key:
                self.encryptor = DataEncryptor(key=env_key.encode())
            else:
                self.encryptor = DataEncryptor()
        
        # Set storage path
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = Path.home() / ".top-tier-secrets" / "secrets.enc"
        
        # Ensure storage directory exists
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing secrets
        self.secrets: Dict[str, Dict[str, Any]] = self._load_secrets()

    def _load_secrets(self) -> Dict[str, Dict[str, Any]]:
        """
        Load secrets from encrypted storage.
        
        Returns:
            Dictionary of secrets with metadata
        """
        if not self.storage_path.exists():
            return {}
        
        try:
            with open(self.storage_path, "rb") as f:
                encrypted_data = f.read()
            
            decrypted_json = self.encryptor.decrypt(encrypted_data)
            return json.loads(decrypted_json)
        except Exception as e:
            print(f"Warning: Failed to load secrets: {e}")
            return {}

    def _save_secrets(self) -> None:
        """Save secrets to encrypted storage."""
        try:
            json_data = json.dumps(self.secrets, indent=2)
            encrypted_data = self.encryptor.encrypt(json_data)
            
            with open(self.storage_path, "wb") as f:
                f.write(encrypted_data)
        except Exception as e:
            print(f"Error: Failed to save secrets: {e}")

    def set_secret(
        self,
        key: str,
        value: str,
        expires_in_days: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Store a secret with optional expiration and metadata.
        
        Args:
            key: Secret identifier
            value: Secret value
            expires_in_days: Days until expiration (None for no expiration)
            metadata: Additional metadata to store
        """
        secret_data = {
            "value": value,
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        if expires_in_days:
            expiry_date = datetime.now() + timedelta(days=expires_in_days)
            secret_data["expires_at"] = expiry_date.isoformat()
        
        self.secrets[key] = secret_data
        self._save_secrets()

    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Retrieve a secret value.
        
        Args:
            key: Secret identifier
            default: Default value if secret not found
            
        Returns:
            Secret value or default
        """
        # First check environment variables (highest priority)
        env_value = os.getenv(key)
        if env_value:
            return env_value
        
        # Then check stored secrets
        secret_data = self.secrets.get(key)
        if not secret_data:
            return default
        
        # Check expiration
        if self._is_expired(secret_data):
            print(f"Warning: Secret '{key}' has expired")
            return default
        
        return secret_data["value"]

    def _is_expired(self, secret_data: Dict[str, Any]) -> bool:
        """
        Check if a secret has expired.
        
        Args:
            secret_data: Secret data dictionary
            
        Returns:
            True if expired, False otherwise
        """
        expires_at = secret_data.get("expires_at")
        if not expires_at:
            return False
        
        expiry_date = datetime.fromisoformat(expires_at)
        return datetime.now() > expiry_date

    def delete_secret(self, key: str) -> bool:
        """
        Delete a secret.
        
        Args:
            key: Secret identifier
            
        Returns:
            True if deleted, False if not found
        """
        if key in self.secrets:
            del self.secrets[key]
            self._save_secrets()
            return True
        return False

    def rotate_secret(self, key: str, new_value: str) -> None:
        """
        Rotate a secret (update with new value while preserving metadata).
        
        Args:
            key: Secret identifier
            new_value: New secret value
        """
        if key in self.secrets:
            metadata = self.secrets[key].get("metadata", {})
            metadata["rotated_at"] = datetime.now().isoformat()
            metadata["rotation_count"] = metadata.get("rotation_count", 0) + 1
            
            # Preserve expiration if it exists
            expires_in_days = None
            if "expires_at" in self.secrets[key]:
                expiry_date = datetime.fromisoformat(self.secrets[key]["expires_at"])
                days_remaining = (expiry_date - datetime.now()).days
                if days_remaining > 0:
                    expires_in_days = days_remaining
            
            self.set_secret(key, new_value, expires_in_days, metadata)
        else:
            self.set_secret(key, new_value)

    def list_secrets(self, include_values: bool = False) -> Dict[str, Any]:
        """
        List all secrets with metadata.
        
        Args:
            include_values: Whether to include secret values
            
        Returns:
            Dictionary of secrets with metadata
        """
        result = {}
        for key, data in self.secrets.items():
            secret_info = {
                "created_at": data.get("created_at"),
                "expires_at": data.get("expires_at"),
                "expired": self._is_expired(data),
                "metadata": data.get("metadata", {})
            }
            
            if include_values:
                secret_info["value"] = data.get("value")
            
            result[key] = secret_info
        
        return result

    def get_encryption_key(self) -> str:
        """
        Get the encryption key (for backup/sharing).
        
        Returns:
            Base64 encoded encryption key
        """
        return self.encryptor.get_key()

    def import_from_env(self, keys: list[str]) -> None:
        """
        Import secrets from environment variables.
        
        Args:
            keys: List of environment variable names to import
        """
        for key in keys:
            value = os.getenv(key)
            if value:
                self.set_secret(
                    key,
                    value,
                    metadata={"source": "environment", "imported_at": datetime.now().isoformat()}
                )

    def export_to_env_file(self, output_path: str, keys: Optional[list[str]] = None) -> None:
        """
        Export secrets to .env file format.
        
        Args:
            output_path: Path to output .env file
            keys: List of keys to export (exports all if None)
        """
        keys_to_export = keys if keys else list(self.secrets.keys())
        
        with open(output_path, "w") as f:
            f.write("# Generated by SecretManager\n")
            f.write(f"# Date: {datetime.now().isoformat()}\n\n")
            
            for key in keys_to_export:
                value = self.get_secret(key)
                if value:
                    f.write(f"{key}={value}\n")

    def cleanup_expired(self) -> int:
        """
        Remove all expired secrets.
        
        Returns:
            Number of secrets removed
        """
        expired_keys = [
            key for key, data in self.secrets.items()
            if self._is_expired(data)
        ]
        
        for key in expired_keys:
            del self.secrets[key]
        
        if expired_keys:
            self._save_secrets()
        
        return len(expired_keys)


# Example usage
if __name__ == "__main__":
    # Initialize secret manager
    manager = SecretManager()
    
    # Store some secrets
    manager.set_secret("TELEGRAM_BOT_TOKEN", "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
    manager.set_secret("OPENAI_API_KEY", "sk-proj-1234567890", expires_in_days=90)
    manager.set_secret(
        "GITHUB_TOKEN",
        "ghp_1234567890",
        metadata={"scope": "repo,workflow", "description": "Main workflow token"}
    )
    
    # Retrieve secrets
    bot_token = manager.get_secret("TELEGRAM_BOT_TOKEN")
    print(f"Bot Token: {bot_token[:20]}...")
    
    # Rotate a secret
    manager.rotate_secret("OPENAI_API_KEY", "sk-proj-0987654321")
    
    # List all secrets
    secrets_list = manager.list_secrets(include_values=False)
    print("\nStored secrets:")
    for key, info in secrets_list.items():
        status = "❌ Expired" if info["expired"] else "✓ Active"
        print(f"  {status} {key}")
        if info.get("metadata"):
            print(f"    Metadata: {info['metadata']}")
    
    # Clean up expired secrets
    removed = manager.cleanup_expired()
    print(f"\nRemoved {removed} expired secrets")
    
    # Export to .env file
    manager.export_to_env_file("/tmp/exported.env")
    print("\nSecrets exported to /tmp/exported.env")
