"""
User models.
UserInDB  — full model, never sent over API
UserPublic — safe model for other roles (no personal data)
UserSelf   — full view returned only to the user themselves or admin
"""
from enum import Enum
from pydantic import BaseModel, EmailStr, field_validator
import re


class Role(str, Enum):
    ADMIN = "Administrator"
    ADVANCED = "Advanced user"
    USER = "User"


class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    role: Role = Role.USER

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.fullmatch(r"\+?[0-9\s\-()]{7,20}", v):
            raise ValueError("Invalid phone number format.")
        return v

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 100:
            raise ValueError("Full name must be 2–100 characters.")
        return v


class UserCreate(UserBase):
    date_of_birth: str        # ISO date string, validated in service
    address: str
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain an uppercase letter.")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain a digit.")
        return v


class UserInDB(UserBase):
    """Full internal model stored in users.dat"""
    id: str
    date_of_birth: str
    address: str
    password_hash: str


class UserPublic(BaseModel):
    """Safe view — no personal data. Visible to Admin and Advanced users."""
    id: str
    full_name: str
    role: Role


class UserSelf(UserBase):
    """Full view returned only to the user themselves."""
    id: str
    date_of_birth: str
    address: str


class UserUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    date_of_birth: str | None = None
