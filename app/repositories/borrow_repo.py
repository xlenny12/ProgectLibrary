from pathlib import Path
from app.core.config import get_settings
from app.models.borrow import BorrowInDB
from app.models.book import BookType
from app.repositories.base import FileRepository


class BorrowRepository(FileRepository[BorrowInDB]):
    RECORD_TYPE = "BORROW"

    def _get_path(self) -> Path:
        return get_settings().data_dir / "borrows.dat"

    def _to_line(self, obj: BorrowInDB) -> str:
        return "|".join([
            obj.id, obj.user_id, obj.book_id,
            obj.book_type.value, obj.date_taken, str(obj.days), str(obj.quantity),
            str(int(obj.returned)),
        ])

    def _from_line(self, parts: list[str]) -> BorrowInDB:
        if len(parts) == 7:
            # Backward compatibility for records created before book_type was snapshotted.
            parts = [parts[0], parts[1], parts[2], BookType.FANTASY.value, *parts[3:]]
        return BorrowInDB(
            id=parts[0], user_id=parts[1], book_id=parts[2],
            book_type=BookType(parts[3]), date_taken=parts[4], days=int(parts[5]),
            quantity=int(parts[6]), returned=bool(int(parts[7])),
        )

    def find_by_user(self, user_id: str) -> list[BorrowInDB]:
        return [b for b in self._iter_records() if b.user_id == user_id]

    def find_active(self) -> list[BorrowInDB]:
        return [b for b in self._iter_records() if not b.returned]
