#REVIEW LATER
from enum import Enum
from pydantic import BaseModel, field_validator


class BookType(str, Enum):
    FANTASY = "fantasy"
    CRIMINAL = "criminal"
    DRAMA = "drama"


class BookBase(BaseModel):
    title: str
    author: str
    book_type: BookType
    total_qty: int
    available_qty: int

    @field_validator("title", "author")
    @classmethod
    def not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Field cannot be empty.")
        return v

    @field_validator("total_qty", "available_qty")
    @classmethod
    def non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Quantity cannot be negative.")
        return v


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    book_type: BookType | None = None
    total_qty: int | None = None
    available_qty: int | None = None


class BookInDB(BookBase):
    id: str


class BookPublic(BookBase):
    id: str
