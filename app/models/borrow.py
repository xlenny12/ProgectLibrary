from datetime import date
from uuid import UUID

from pydantic import BaseModel, computed_field, field_validator

from app.models.book import BookType


class BorrowCreate(BaseModel):
    book_id: str
    days: int
    quantity: int = 1

    @field_validator("book_id")
    @classmethod
    def valid_book_id(cls, value: str) -> str:
        try:
            UUID(value)
        except ValueError as exc:
            raise ValueError("book_id must be a valid UUID.") from exc
        return value

    @field_validator("days")
    @classmethod
    def positive_days(cls, value: int) -> int:
        if value < 1 or value > 365:
            raise ValueError("Borrow period must be 1-365 days.")
        return value

    @field_validator("quantity")
    @classmethod
    def positive_qty(cls, value: int) -> int:
        if value < 1:
            raise ValueError("Quantity must be at least 1.")
        if value > 100:
            raise ValueError("Quantity is unreasonably large.")
        return value


class BorrowInDB(BaseModel):
    id: str
    user_id: str
    book_id: str
    book_type: BookType
    date_taken: str
    days: int
    quantity: int
    returned: bool = False

    def is_overdue(self, today: date | None = None) -> bool:
        from datetime import date as _date, timedelta

        t = today or _date.today()
        taken = _date.fromisoformat(self.date_taken)
        due = taken + timedelta(days=self.days)
        return not self.returned and t > due

    def calculate_due_date(self) -> str:
        from datetime import date as _date, timedelta

        taken = _date.fromisoformat(self.date_taken)
        return (taken + timedelta(days=self.days)).isoformat()

    @computed_field
    @property
    def due_date(self) -> str:
        return self.calculate_due_date()


class BorrowPublic(BorrowInDB):
    pass
