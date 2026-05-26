from app.core import audit
from app.core.config import get_settings
from app.models.book import BookInDB
from app.models.borrow import BorrowInDB
from app.models.user import UserInDB
from app.repositories.book_repo import BookRepository
from app.repositories.borrow_repo import BorrowRepository
from app.repositories.user_repo import UserRepository


class RecoveryService:
    def restore_from_audit(self, actor_id: str) -> dict[str, int]:
        """Rebuild users/books/borrows files from the signed audit log."""
        state = audit.replay_database()
        settings = get_settings()
        settings.ensure_data_dir()

        for name in ("users.dat", "books.dat", "borrows.dat"):
            path = settings.data_dir / name
            if path.exists():
                path.unlink()

        user_repo = UserRepository()
        book_repo = BookRepository()
        borrow_repo = BorrowRepository()

        for user in state["users"]:
            user_repo.save(UserInDB(**user))
        for book in state["books"]:
            book_repo.save(BookInDB(**book))
        for borrow in state["borrows"]:
            borrow_repo.save(BorrowInDB(**borrow))

        counts = {"users": len(state["users"]), "books": len(state["books"]), "borrows": len(state["borrows"])}
        audit.log(actor_id, "DATABASE_RESTORED_FROM_AUDIT", counts)
        return counts
