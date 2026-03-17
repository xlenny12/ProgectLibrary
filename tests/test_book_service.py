import pytest
from app.services.book_service import BookService
from app.models.book import BookCreate, BookUpdate, BookType


def _make_book(**kwargs):
    defaults = dict(
        title="The Witcher",
        author="Andrzej Sapkowski",
        book_type=BookType.FANTASY,
        total_qty=5,
        available_qty=5,
    )
    defaults.update(kwargs)
    return BookCreate(**defaults)


def test_create_book():
    svc = BookService()
    book = svc.create(_make_book(), actor_id="admin-1")
    assert book.title == "The Witcher"
    assert book.available_qty == 5


def test_list_books():
    svc = BookService()
    svc.create(_make_book(), actor_id="admin-1")
    svc.create(_make_book(title="Crime and Punishment", book_type=BookType.CRIMINAL), actor_id="admin-1")
    books = svc.list_all()
    assert len(books) == 2


def test_update_book():
    svc = BookService()
    book = svc.create(_make_book(), actor_id="admin-1")
    updated = svc.update(book.id, BookUpdate(available_qty=3), actor_id="admin-1")
    assert updated.available_qty == 3


def test_delete_book():
    svc = BookService()
    book = svc.create(_make_book(), actor_id="admin-1")
    svc.delete(book.id, actor_id="admin-1")
    with pytest.raises(ValueError):
        svc.get(book.id)


def test_negative_qty_rejected():
    with pytest.raises(ValueError):
        _make_book(available_qty=-1)
