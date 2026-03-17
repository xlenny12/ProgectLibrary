#!/usr/bin/env python3
"""
Generate secure cryptographic keys for ProgectLibrary.

This script generates three keys needed for the application:
  1. SECRET_KEY - For signing JWT tokens
  2. FERNET_KEY - For encrypting data files
  3. AUDIT_HMAC_KEY - For signing audit log entries

Usage:
  python scripts/generate_keys.py

Then copy the output values into your .env file.
"""
import secrets
from cryptography.fernet import Fernet

print("\n" + "="*70)
print("ProgectLibrary - Key Generation Script")
print("="*70 + "\n")

print("Generated keys (copy these into your .env file):\n")

secret_key = secrets.token_hex(32)
print(f"SECRET_KEY={secret_key}")

fernet_key = Fernet.generate_key().decode()
print(f"FERNET_KEY={fernet_key}")

audit_hmac_key = secrets.token_hex(32)
print(f"AUDIT_HMAC_KEY={audit_hmac_key}")

print("\n" + "="*70)
print("Next steps:")
print("  1. Open or create .env file in the project root")
print("  2. Paste the three KEY values above")
print("  3. Run: uvicorn app.main:app --reload")
print("="*70 + "\n")