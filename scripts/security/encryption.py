"""
Data Encryption Module
Provides encryption at rest and in transit for sensitive data.
"""

import base64
import hashlib
import os
from typing import Optional, Union

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class DataEncryptor:
    """
    Handles encryption and decryption of sensitive data.
    
    Uses Fernet (symmetric encryption) for data encryption.
    Supports both key-based and password-based encryption.
    """

    def __init__(self, key: Optional[bytes] = None, password: Optional[str] = None):
        """
        Initialize the encryptor with either a key or password.
        
        Args:
            key: Encryption key (32 url-safe base64-encoded bytes)
            password: Password to derive encryption key from
        """
        if key:
            self.key = key
        elif password:
            self.key = self._derive_key_from_password(password)
        else:
            # Generate a new key
            self.key = Fernet.generate_key()
        
        self.cipher = Fernet(self.key)

    @staticmethod
    def _derive_key_from_password(password: str, salt: Optional[bytes] = None) -> bytes:
        """
        Derive an encryption key from a password using PBKDF2.
        
        Args:
            password: Password to derive key from
            salt: Optional salt (generated if not provided)
            
        Returns:
            Derived encryption key
        """
        if salt is None:
            salt = b"top-tier-global-hub-ai-salt"  # Should be stored securely in production
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    @staticmethod
    def generate_key() -> bytes:
        """Generate a new encryption key."""
        return Fernet.generate_key()

    def encrypt(self, data: Union[str, bytes]) -> bytes:
        """
        Encrypt data.
        
        Args:
            data: Data to encrypt (string or bytes)
            
        Returns:
            Encrypted data as bytes
        """
        if isinstance(data, str):
            data = data.encode()
        return self.cipher.encrypt(data)

    def decrypt(self, encrypted_data: bytes) -> str:
        """
        Decrypt data.
        
        Args:
            encrypted_data: Encrypted data to decrypt
            
        Returns:
            Decrypted data as string
        """
        return self.cipher.decrypt(encrypted_data).decode()

    def encrypt_to_string(self, data: Union[str, bytes]) -> str:
        """
        Encrypt data and return as base64 string.
        
        Args:
            data: Data to encrypt
            
        Returns:
            Encrypted data as base64 string
        """
        encrypted = self.encrypt(data)
        return base64.b64encode(encrypted).decode()

    def decrypt_from_string(self, encrypted_string: str) -> str:
        """
        Decrypt data from base64 string.
        
        Args:
            encrypted_string: Base64 encoded encrypted data
            
        Returns:
            Decrypted data as string
        """
        encrypted = base64.b64decode(encrypted_string.encode())
        return self.decrypt(encrypted)

    @staticmethod
    def hash_data(data: Union[str, bytes]) -> str:
        """
        Create a SHA256 hash of data (one-way, for verification).
        
        Args:
            data: Data to hash
            
        Returns:
            Hexadecimal hash string
        """
        if isinstance(data, str):
            data = data.encode()
        return hashlib.sha256(data).hexdigest()

    def get_key(self) -> str:
        """
        Get the encryption key as a string (for storage).
        
        Returns:
            Base64 encoded key
        """
        return self.key.decode()


class SecureStorage:
    """
    Secure storage for sensitive data with encryption.
    """

    def __init__(self, encryptor: DataEncryptor):
        """
        Initialize secure storage with an encryptor.
        
        Args:
            encryptor: DataEncryptor instance
        """
        self.encryptor = encryptor
        self._storage = {}

    def store(self, key: str, value: str) -> None:
        """
        Store encrypted data.
        
        Args:
            key: Storage key
            value: Value to store (will be encrypted)
        """
        encrypted_value = self.encryptor.encrypt_to_string(value)
        self._storage[key] = encrypted_value

    def retrieve(self, key: str) -> Optional[str]:
        """
        Retrieve and decrypt data.
        
        Args:
            key: Storage key
            
        Returns:
            Decrypted value or None if not found
        """
        encrypted_value = self._storage.get(key)
        if encrypted_value:
            return self.encryptor.decrypt_from_string(encrypted_value)
        return None

    def delete(self, key: str) -> bool:
        """
        Delete stored data.
        
        Args:
            key: Storage key
            
        Returns:
            True if deleted, False if not found
        """
        if key in self._storage:
            del self._storage[key]
            return True
        return False

    def exists(self, key: str) -> bool:
        """
        Check if key exists.
        
        Args:
            key: Storage key
            
        Returns:
            True if exists, False otherwise
        """
        return key in self._storage


# Example usage
if __name__ == "__main__":
    # Example 1: Using generated key
    encryptor = DataEncryptor()
    sensitive_data = "TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
    
    encrypted = encryptor.encrypt_to_string(sensitive_data)
    print(f"Encrypted: {encrypted}")
    
    decrypted = encryptor.decrypt_from_string(encrypted)
    print(f"Decrypted: {decrypted}")
    
    # Example 2: Using password-based encryption
    encryptor2 = DataEncryptor(password="my-secure-password")
    encrypted2 = encryptor2.encrypt_to_string("Secret API Key")
    print(f"Encrypted with password: {encrypted2}")
    
    # Example 3: Secure storage
    storage = SecureStorage(encryptor)
    storage.store("api_key", "sk-1234567890")
    retrieved = storage.retrieve("api_key")
    print(f"Retrieved from storage: {retrieved}")
