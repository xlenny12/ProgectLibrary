from enum import Enum
from pydantic import HttpUrl
from pydantic import BaseModel, field_validator, model_validator


FORBIDDEN_STORAGE_CHARS = {"|", "\n", "\r"}


class BookType(str, Enum):
    FANTASY = "fantasy"
    CRIMINAL = "criminal"
    DRAMA = "drama"


def _clean_text(value: str, field_name: str) -> str:
    value = value.strip()
    if not 1 <= len(value) <= 120:
        raise ValueError(f"{field_name} must be 1-120 characters.")
    if any(ch in value for ch in FORBIDDEN_STORAGE_CHARS):
        raise ValueError(f"{field_name} contains unsupported control characters.")
    return value


class BookBase(BaseModel):
    title: str
    author: str
    book_type: BookType
    total_qty: int
    available_qty: int
    cover_image_url: str | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        return _clean_text(value, "Title")

    @field_validator("author")
    @classmethod
    def validate_author(cls, value: str) -> str:
        return _clean_text(value, "Author")

    @field_validator("total_qty", "available_qty")
    @classmethod
    def non_negative(cls, value: int) -> int:
        if value < 0:
            raise ValueError("Quantity cannot be negative.")
        if value > 10000:
            raise ValueError("Quantity is unreasonably large.")
        return value

    @model_validator(mode="after")
    def available_cannot_exceed_total(self) -> "BookBase":
        if self.available_qty > self.total_qty:
            raise ValueError("Available quantity cannot exceed total quantity.")
        return self


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    book_type: BookType | None = None
    total_qty: int | None = None
    available_qty: int | None = None
    cover_image_url: str | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        return None if value is None else _clean_text(value, "Title")

    @field_validator("author")
    @classmethod
    def validate_author(cls, value: str | None) -> str | None:
        return None if value is None else _clean_text(value, "Author")

    @field_validator("total_qty", "available_qty")
    @classmethod
    def non_negative(cls, value: int | None) -> int | None:
        if value is None:
            return None
        if value < 0:
            raise ValueError("Quantity cannot be negative.")
        if value > 10000:
            raise ValueError("Quantity is unreasonably large.")
        return value


class BookInDB(BookBase):
    id: str


class BookPublic(BookBase):
    id: str
