#REVIEW LATER
"""
Symmetric encryption for all .dat files.
Uses Fernet (AES-128-CBC + HMAC-SHA256).

Usage:
    from app.core.crypto import encrypt, decrypt
    raw = decrypt(path.read_bytes())
    path.write_bytes(encrypt(raw))
"""
from cryptography.fernet import Fernet, InvalidToken
from app.core.config import get_settings


def _get_fernet() -> Fernet:
    key = get_settings().fernet_key
    if not key:
        raise RuntimeError("FERNET_KEY is not set in environment.")
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt(plaintext: str) -> bytes:
    """Encrypt a UTF-8 string and return ciphertext bytes."""
    return _get_fernet().encrypt(plaintext.encode("utf-8"))


def decrypt(ciphertext: bytes) -> str:
    """Decrypt ciphertext bytes and return UTF-8 string. Raises ValueError on bad data."""
    try:
        return _get_fernet().decrypt(ciphertext).decode("utf-8")
    except InvalidToken as exc:
        raise ValueError("Decryption failed — file may be corrupted or key is wrong.") from exc


def generate_new_key() -> str:
    """Utility: generate a fresh Fernet key (run once, store in .env)."""
    return Fernet.generate_key().decode()
