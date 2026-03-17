from pathlib import Path
from app.core.config import get_settings
from app.models.book import BookInDB, BookType
from app.repositories.base import FileRepository


class BookRepository(FileRepository[BookInDB]):
    RECORD_TYPE = "BOOK"

    def _get_path(self) -> Path:
        return get_settings().data_dir / "books.dat"

    def _to_line(self, obj: BookInDB) -> str:
        return "|".join([
            obj.id, obj.title, obj.author,
            obj.book_type.value, str(obj.total_qty), str(obj.available_qty),
        ])

    def _from_line(self, parts: list[str]) -> BookInDB:
        return BookInDB(
            id=parts[0], title=parts[1], author=parts[2],
            book_type=BookType(parts[3]),
            total_qty=int(parts[4]), available_qty=int(parts[5]),
        )
