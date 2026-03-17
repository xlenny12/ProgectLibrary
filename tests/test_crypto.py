import pytest
from app.core.crypto import encrypt, decrypt


def test_round_trip():
    plain = "Hello, Бібліотека!"
    assert decrypt(encrypt(plain)) == plain


def test_wrong_key_raises(monkeypatch):
    from cryptography.fernet import Fernet
    ciphertext = encrypt("secret")
    # swap key
    monkeypatch.setenv("FERNET_KEY", Fernet.generate_key().decode())
    from app.core.config import get_settings
    get_settings.cache_clear()
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(ciphertext)


def test_tampered_ciphertext_raises():
    ct = bytearray(encrypt("data"))
    ct[10] ^= 0xFF          # flip a byte
    with pytest.raises(ValueError):
        decrypt(bytes(ct))
