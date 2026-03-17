#REVIEWW LATER
from pydantic import BaseModel, field_validator
from datetime import date


class BorrowCreate(BaseModel):
    book_id: str
    days: int
    quantity: int = 1

    @field_validator("days")
    @classmethod
    def positive_days(cls, v: int) -> int:
        if v < 1 or v > 365:
            raise ValueError("Borrow period must be 1–365 days.")
        return v

    @field_validator("quantity")
    @classmethod
    def positive_qty(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Quantity must be at least 1.")
        return v


class BorrowInDB(BaseModel):
    id: str
    user_id: str
    book_id: str
    date_taken: str    # ISO date string
    days: int
    quantity: int
    returned: bool = False

    def is_overdue(self, today: date | None = None) -> bool:
        from datetime import date as _date, timedelta
        t = today or _date.today()
        taken = _date.fromisoformat(self.date_taken)
        due = taken + timedelta(days=self.days)
        return not self.returned and t > due

    def due_date(self) -> str:
        from datetime import date as _date, timedelta
        taken = _date.fromisoformat(self.date_taken)
        return (taken + timedelta(days=self.days)).isoformat()


class BorrowPublic(BorrowInDB):
    pass
