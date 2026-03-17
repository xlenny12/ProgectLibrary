import uuid
import threading
from datetime import date
from app.models.borrow import BorrowCreate, BorrowInDB, BorrowPublic
from app.repositories.borrow_repo import BorrowRepository
from app.repositories.book_repo import BookRepository
from app.core.logger import get_logger
from app.core import audit

logger = get_logger(__name__)

# File-based locking to prevent race conditions on book availability
# In production, use a proper database with transactions instead
_borrow_lock = threading.RLock()


class BorrowService:
    def __init__(
        self,
        borrow_repo: BorrowRepository | None = None,
        book_repo: BookRepository | None = None,
    ):
        self.borrow_repo = borrow_repo or BorrowRepository()
        self.book_repo = book_repo or BookRepository()

    def borrow(self, user_id: str, data: BorrowCreate) -> BorrowPublic:
        """Borrow a book with thread-safe availability check."""
        with _borrow_lock:
            book = self.book_repo.find_by_id(data.book_id)
            if not book:
                logger.warning(f"Borrow failed: book not found. user={user_id}, book_id={data.book_id}")
                raise ValueError("Book not found.")
            if book.available_qty < data.quantity:
                logger.warning(f"Insufficient copies: requested={data.quantity}, available={book.available_qty}. user={user_id}, book={data.book_id}")
                raise ValueError(f"Only {book.available_qty} copies available.")
            
            # Create borrow record
            record = BorrowInDB(
                id=str(uuid.uuid4()),
                user_id=user_id,
                book_id=data.book_id,
                date_taken=date.today().isoformat(),
                days=data.days,
                quantity=data.quantity,
                returned=False,
            )
            
            # Atomically decrement available and save borrow
            updated_book = book.model_copy(update={"available_qty": book.available_qty - data.quantity})
            self.book_repo.save(updated_book)
            self.borrow_repo.save(record)
            logger.info(f"Book borrowed: user={user_id}, book={data.book_id}, qty={data.quantity}, borrow_id={record.id}")
            audit.log(user_id, "BOOK_BORROWED", {"borrow_id": record.id, "book_id": data.book_id})
            return BorrowPublic(**record.model_dump())

    def return_book(self, borrow_id: str, user_id: str) -> BorrowPublic:
        record = self.borrow_repo.find_by_id(borrow_id)
        if not record:
            logger.warning(f"Return failed: borrow record not found. user={user_id}, borrow_id={borrow_id}")
            raise ValueError("Borrow record not found.")
        if record.user_id != user_id:
            logger.warning(f"Return unauthorized: user mismatch. user={user_id}, borrow.user={record.user_id}")
            raise ValueError("Not your borrow record.")
        if record.returned:
            logger.warning(f"Return failed: already returned. user={user_id}, borrow_id={borrow_id}")
            raise ValueError("Already returned.")
        book = self.book_repo.find_by_id(record.book_id)
        if book:
            self.book_repo.save(book.model_copy(update={"available_qty": book.available_qty + record.quantity}))
        updated = record.model_copy(update={"returned": True})
        self.borrow_repo.save(updated)
        logger.info(f"Book returned: user={user_id}, borrow_id={borrow_id}, book={record.book_id}, qty={record.quantity}")
        audit.log(user_id, "BOOK_RETURNED", {"borrow_id": borrow_id})
        return BorrowPublic(**updated.model_dump())

    def my_borrows(self, user_id: str) -> list[BorrowPublic]:
        return [BorrowPublic(**b.model_dump()) for b in self.borrow_repo.find_by_user(user_id)]

    def overdue_borrows(self) -> list[BorrowInDB]:
        today = date.today()
        return [b for b in self.borrow_repo.find_active() if b.is_overdue(today)]

    def delete_all_for_user(self, user_id: str, actor_id: str) -> int:
        """GDPR: remove all borrow records for a user."""
        records = self.borrow_repo.find_by_user(user_id)
        for r in records:
            self.borrow_repo.delete(r.id)
        audit.log(actor_id, "BORROWS_DELETED_GDPR", {"user_id": user_id, "count": len(records)})
        return len(records)
