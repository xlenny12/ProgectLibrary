import pytest
from datetime import date, timedelta
from app.services.borrow_service import BorrowService
from app.services.book_service import BookService
from app.models.book import BookCreate, BookType
from app.models.borrow import BorrowCreate


def _setup():
    book_svc = BookService()
    book = book_svc.create(BookCreate(
        title="Dune", author="Herbert", book_type=BookType.FANTASY,
        total_qty=3, available_qty=3,
    ), actor_id="admin")
    return BorrowService(), book


def test_borrow_decrements_qty():
    borrow_svc, book = _setup()
    borrow_svc.borrow("user-1", BorrowCreate(book_id=book.id, days=7, quantity=2))
    book_svc = BookService()
    updated = book_svc.get(book.id)
    assert updated.available_qty == 1


def test_borrow_insufficient_qty():
    borrow_svc, book = _setup()
    with pytest.raises(ValueError, match="available"):
        borrow_svc.borrow("user-1", BorrowCreate(book_id=book.id, days=7, quantity=10))


def test_return_increments_qty():
    borrow_svc, book = _setup()
    record = borrow_svc.borrow("user-1", BorrowCreate(book_id=book.id, days=7, quantity=1))
    borrow_svc.return_book(record.id, "user-1")
    updated = BookService().get(book.id)
    assert updated.available_qty == 3


def test_double_return_rejected():
    borrow_svc, book = _setup()
    record = borrow_svc.borrow("user-1", BorrowCreate(book_id=book.id, days=7, quantity=1))
    borrow_svc.return_book(record.id, "user-1")
    with pytest.raises(ValueError, match="Already returned"):
        borrow_svc.return_book(record.id, "user-1")


def test_wrong_user_cannot_return():
    borrow_svc, book = _setup()
    record = borrow_svc.borrow("user-1", BorrowCreate(book_id=book.id, days=7, quantity=1))
    with pytest.raises(ValueError, match="Not your"):
        borrow_svc.return_book(record.id, "user-999")


def test_overdue_detection(monkeypatch):
    borrow_svc, book = _setup()
    record = borrow_svc.borrow("user-1", BorrowCreate(book_id=book.id, days=1, quantity=1))
    # travel forward 5 days
    future = date.today() + timedelta(days=5)
    overdue = [b for b in borrow_svc.borrow_repo.find_active() if b.is_overdue(future)]
    assert any(b.id == record.id for b in overdue)


def test_gdpr_delete_removes_borrows():
    borrow_svc, book = _setup()
    borrow_svc.borrow("user-42", BorrowCreate(book_id=book.id, days=7, quantity=1))
    count = borrow_svc.delete_all_for_user("user-42", actor_id="user-42")
    assert count == 1
    assert borrow_svc.my_borrows("user-42") == []
