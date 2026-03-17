#!/usr/bin/env python3
"""
Create the first Administrator account for ProgectLibrary.

Run this AFTER setting up your .env file:
  python scripts/seed_admin.py

This creates an admin user for accessing admin endpoints.
You'll be prompted to enter admin details interactively.
"""
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.config import get_settings
from app.services.user_service import UserService
from app.models.user import UserCreate, Role


def create_admin():
    """Interactively create an admin user."""
    settings = get_settings()
    settings.ensure_data_dir()

    print("\n" + "="*70)
    print("ProgectLibrary - Create Admin User")
    print("="*70)
    print("\nEnter admin details (all fields required):\n")

    email = input("Admin email address: ").strip()
    if not email:
        print("❌ Email cannot be empty")
        return

    password = input("Admin password (min 8 chars, needs uppercase & digit): ").strip()
    if len(password) < 8:
        print("❌ Password must be at least 8 characters")
        return

    full_name = input("Admin full name: ").strip()
    if not full_name:
        print("❌ Full name cannot be empty")
        return

    phone = input("Admin phone number (e.g., +1234567890): ").strip()
    date_of_birth = input("Date of birth (YYYY-MM-DD): ").strip()

    # Create admin
    svc = UserService()
    try:
        user = svc.register(
            UserCreate(
                full_name=full_name,
                email=email,
                phone=phone,
                date_of_birth=date_of_birth,
                address="Admin Account",
                password=password,
                role=Role.ADMIN,
            ),
            actor_id="system"
        )
        print("\n" + "="*70)
        print("✅ Admin user created successfully!")
        print("="*70)
        print(f"User ID: {user.id}")
        print(f"Email:   {user.full_name}")
        print(f"\nYou can now log in at /api/auth/login")
        print("="*70 + "\n")

    except ValueError as e:
        print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    create_admin()

