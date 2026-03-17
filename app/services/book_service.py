import uuid
from app.models.book import BookCreate, BookInDB, BookPublic, BookUpdate
from app.repositories.book_repo import BookRepository
from app.core import audit


class BookService:
    def __init__(self, repo: BookRepository | None = None):
        self.repo = repo or BookRepository()

    def create(self, data: BookCreate, actor_id: str) -> BookPublic:
        book = BookInDB(id=str(uuid.uuid4()), **data.model_dump())
        self.repo.save(book)
        audit.log(actor_id, "BOOK_CREATED", {"book_id": book.id, "title": book.title})
        return BookPublic(**book.model_dump())

    def list_all(self) -> list[BookPublic]:
        return [BookPublic(**b.model_dump()) for b in self.repo.all()]

    def get(self, book_id: str) -> BookPublic:
        book = self.repo.find_by_id(book_id)
        if not book:
            raise ValueError("Book not found.")
        return BookPublic(**book.model_dump())

    def update(self, book_id: str, data: BookUpdate, actor_id: str) -> BookPublic:
        book = self.repo.find_by_id(book_id)
        if not book:
            raise ValueError("Book not found.")
        updated = book.model_copy(update={k: v for k, v in data.model_dump().items() if v is not None})
        self.repo.save(updated)
        audit.log(actor_id, "BOOK_UPDATED", {"book_id": book_id})
        return BookPublic(**updated.model_dump())

    def delete(self, book_id: str, actor_id: str) -> None:
        if not self.repo.delete(book_id):
            raise ValueError("Book not found.")
        audit.log(actor_id, "BOOK_DELETED", {"book_id": book_id})
