"""
Shared pytest fixtures.
All tests use a temporary data directory — nothing touches the real data/ folder.
"""
import os
import pytest
from pathlib import Path
from cryptography.fernet import Fernet


@pytest.fixture(autouse=True)
def tmp_data_dir(tmp_path, monkeypatch):
    """Redirect all file I/O to a fresh temp directory and set test encryption keys.
    
    This fixture:
    - Creates a fresh temporary directory for each test
    - Sets test environment variables (keys, paths)
    - Clears the cached Settings object between tests
    - Ensures test isolation (no influence on real data/)
    """
    key = Fernet.generate_key().decode()
    monkeypatch.setenv("FERNET_KEY", key)
    monkeypatch.setenv("AUDIT_HMAC_KEY", "test-hmac-key-32-chars-long-minimum-")
    monkeypatch.setenv("SECRET_KEY", "test-secret-key-not-for-production---")
    monkeypatch.setenv("DATA_DIR", str(tmp_path))

    # Clear lru_cache so Settings re-reads env vars
    from app.core.config import get_settings
    get_settings.cache_clear()

    yield tmp_path

    get_settings.cache_clear()

