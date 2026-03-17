import pytest
from app.services.user_service import UserService
from app.models.user import UserCreate, UserUpdate, Role


def _make_user(**kwargs):
    defaults = dict(
        full_name="Іван Франко",
        email="ivan@example.com",
        phone="+380991234567",
        date_of_birth="1990-05-15",
        address="Lviv, Shevchenka 1",
        password="Secret123",
        role=Role.USER,
    )
    defaults.update(kwargs)
    return UserCreate(**defaults)


def test_register_success():
    svc = UserService()
    user = svc.register(_make_user())
    assert user.email == "ivan@example.com"
    assert user.full_name == "Іван Франко"


def test_register_duplicate_email():
    svc = UserService()
    svc.register(_make_user())
    with pytest.raises(ValueError, match="already exists"):
        svc.register(_make_user())


def test_authenticate_success():
    svc = UserService()
    svc.register(_make_user())
    user = svc.authenticate("ivan@example.com", "Secret123")
    assert user.email == "ivan@example.com"


def test_authenticate_wrong_password():
    svc = UserService()
    svc.register(_make_user())
    with pytest.raises(ValueError, match="Invalid"):
        svc.authenticate("ivan@example.com", "wrongpass")


def test_weak_password_rejected():
    with pytest.raises(ValueError):
        _make_user(password="weak")


def test_get_self():
    svc = UserService()
    created = svc.register(_make_user())
    self_view = svc.get_self(created.id)
    assert self_view.address == "Lviv, Shevchenka 1"


def test_get_public_hides_personal():
    svc = UserService()
    created = svc.register(_make_user())
    pub = svc.get_public(created.id)
    assert not hasattr(pub, "address")
    assert not hasattr(pub, "date_of_birth")
    assert not hasattr(pub, "phone")


def test_update_user():
    svc = UserService()
    created = svc.register(_make_user())
    updated = svc.update(created.id, UserUpdate(address="Kyiv, Khreshchatyk 1"), actor_id=created.id)
    assert updated.address == "Kyiv, Khreshchatyk 1"


def test_gdpr_delete():
    svc = UserService()
    created = svc.register(_make_user())
    svc.delete(created.id, actor_id=created.id)
    assert svc.repo.find_by_id(created.id) is None
