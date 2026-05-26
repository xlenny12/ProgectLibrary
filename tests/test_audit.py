from app.core import audit


def test_log_and_verify():
    audit.log("user-1", "TEST_ACTION", {"key": "value"})
    ok, tampered = audit.verify_integrity()
    assert ok
    assert tampered == []


def test_replay_returns_events():
    audit.log("user-1", "USER_CREATED", {"email": "a@b.com"})
    events = audit.replay_events()
    assert len(events) >= 1
    assert events[-1]["action"] == "USER_CREATED"


def test_tampered_log_detected(tmp_path):
    audit.log("user-1", "SENSITIVE", {})
    path = tmp_path / "audit.dat"
    raw = path.read_bytes()
    # decrypt, corrupt, re-encrypt with same key
    from app.core.crypto import decrypt, encrypt
    plaintext = decrypt(raw)
    corrupted = plaintext.replace("SENSITIVE", "TAMPERED_EXTERNALLY")
    path.write_bytes(encrypt(corrupted))
    ok, tampered = audit.verify_integrity()
    assert not ok
    assert len(tampered) == 1


def test_replay_database_reconstructs_current_state():
    user = {
        "id": "u1",
        "full_name": "User One",
        "email": "one@example.com",
        "phone": "+380991234567",
        "date_of_birth": "1990-01-01",
        "address": "Lviv",
        "role": "User",
        "password_hash": "$2b$hash",
    }
    book = {
        "id": "b1",
        "title": "Dune",
        "author": "Frank Herbert",
        "book_type": "fantasy",
        "total_qty": 2,
        "available_qty": 1,
    }
    borrow = {
        "id": "br1",
        "user_id": "u1",
        "book_id": "b1",
        "book_type": "fantasy",
        "date_taken": "2026-01-01",
        "days": 14,
        "quantity": 1,
        "returned": False,
    }
    audit.log("system", "USER_CREATED", {"user": user})
    audit.log("system", "BOOK_CREATED", {"book": book})
    audit.log("u1", "BOOK_BORROWED", {"borrow": borrow})

    state = audit.replay_database()
    assert state["users"] == [user]
    assert state["books"] == [book]
    assert state["borrows"] == [borrow]
