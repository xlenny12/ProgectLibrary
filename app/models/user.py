from datetime import date
from enum import Enum
import re

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


FORBIDDEN_STORAGE_CHARS = {"|", "\n", "\r"}


class Role(str, Enum):
    ADMIN = "Administrator"
    ADVANCED = "Advanced user"
    USER = "User"


def _clean_text(value: str, field_name: str, min_len: int, max_len: int) -> str:
    value = value.strip()
    if len(value) < min_len or len(value) > max_len:
        raise ValueError(f"{field_name} must be {min_len}-{max_len} characters.")
    if any(ch in value for ch in FORBIDDEN_STORAGE_CHARS):
        raise ValueError(f"{field_name} contains unsupported control characters.")
    return value


def _validate_iso_date(value: str) -> str:
    value = value.strip()
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("date_of_birth must be a valid ISO date (YYYY-MM-DD).") from exc
    if parsed >= date.today():
        raise ValueError("date_of_birth must be in the past.")
    return value


def _validate_password(value: str) -> str:
    if len(value) < 8:
        raise ValueError("Password must be at least 8 characters.")
    if len(value) > 128:
        raise ValueError("Password must not exceed 128 characters.")
    if not re.search(r"[A-Z]", value):
        raise ValueError("Password must contain an uppercase letter.")
    if not re.search(r"[0-9]", value):
        raise ValueError("Password must contain a digit.")
    return value


class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: str

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return _clean_text(value, "Full name", 2, 100)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        value = value.strip()
        if not re.fullmatch(r"\+?[0-9\s\-()]{7,20}", value):
            raise ValueError("Invalid phone number format.")
        return value


class UserCreate(UserBase):
    date_of_birth: str
    address: str
    password: str
    role: Role = Role.USER

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, value: str) -> str:
        return _validate_iso_date(value)

    @field_validator("address")
    @classmethod
    def validate_address(cls, value: str) -> str:
        return _clean_text(value, "Address", 3, 200)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return _validate_password(value)


class UserRegistration(UserBase):
    """Public registration payload. Role is intentionally not accepted here."""

    model_config = ConfigDict(extra="forbid")

    date_of_birth: str
    address: str
    password: str

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, value: str) -> str:
        return _validate_iso_date(value)

    @field_validator("address")
    @classmethod
    def validate_address(cls, value: str) -> str:
        return _clean_text(value, "Address", 3, 200)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return _validate_password(value)


class UserInDB(UserBase):
    """Full internal model stored in users.dat. Never expose this in API responses."""

    id: str
    date_of_birth: str
    address: str
    role: Role
    password_hash: str


class UserPublic(BaseModel):
    """Safe view for Admin/Advanced users: no name, email, phone, address, or DOB."""

    id: str
    role: Role


class UserSelf(UserBase):
    """Full profile returned only to the user who owns it."""

    id: str
    date_of_birth: str
    address: str
    role: Role


class UserUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    date_of_birth: str | None = None

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        return None if value is None else _clean_text(value, "Full name", 2, 100)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr | None) -> str | None:
        return None if value is None else str(value).strip().lower()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not re.fullmatch(r"\+?[0-9\s\-()]{7,20}", value):
            raise ValueError("Invalid phone number format.")
        return value

    @field_validator("address")
    @classmethod
    def validate_address(cls, value: str | None) -> str | None:
        return None if value is None else _clean_text(value, "Address", 3, 200)

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, value: str | None) -> str | None:
        return None if value is None else _validate_iso_date(value)
