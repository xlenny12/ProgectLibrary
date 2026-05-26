import pytest

from app.models.user import Role, UserCreate, UserRegistration, UserUpdate
from app.services.user_service import UserService


def _make_user(**kwargs):
    defaults = dict(
        full_name="Ivan Franko",
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
    assert user.full_name == "Ivan Franko"
    assert user.role == Role.USER


def test_public_registration_model_rejects_role_escalation():
    with pytest.raises(ValueError):
        UserRegistration(
            full_name="Mallory",
            email="mallory@example.com",
            phone="+380991234567",
            date_of_birth="1990-05-15",
            address="Kyiv",
            password="Secret123",
            role=Role.ADMIN,
        )


def test_service_rejects_non_admin_role_assignment():
    svc = UserService()
    with pytest.raises(ValueError, match="Only administrators"):
        svc.register(_make_user(email="admin-try@example.com", role=Role.ADMIN))


def test_admin_can_assign_role():
    svc = UserService()
    user = svc.register(
        _make_user(email="advanced@example.com", role=Role.ADVANCED),
        actor_id="admin-1",
        allow_role_selection=True,
    )
    assert user.role == Role.ADVANCED


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


def test_storage_delimiter_rejected():
    with pytest.raises(ValueError):
        _make_user(full_name="Ivan|Injected")


def test_get_self():
    svc = UserService()
    created = svc.register(_make_user())
    self_view = svc.get_self(created.id)
    assert self_view.address == "Lviv, Shevchenka 1"


def test_get_public_hides_personal():
    svc = UserService()
    created = svc.register(_make_user())
    pub = svc.get_public(created.id)
    assert pub.id == created.id
    assert not hasattr(pub, "full_name")
    assert not hasattr(pub, "email")
    assert not hasattr(pub, "address")
    assert not hasattr(pub, "date_of_birth")
    assert not hasattr(pub, "phone")


def test_update_user():
    svc = UserService()
    created = svc.register(_make_user())
    updated = svc.update(created.id, UserUpdate(address="Kyiv, Khreshchatyk 1"), actor_id=created.id)
    assert updated.address == "Kyiv, Khreshchatyk 1"


def test_update_duplicate_email_rejected():
    svc = UserService()
    svc.register(_make_user(email="one@example.com"))
    second = svc.register(_make_user(email="two@example.com"))
    with pytest.raises(ValueError, match="already exists"):
        svc.update(second.id, UserUpdate(email="one@example.com"), actor_id=second.id)


def test_gdpr_delete_removes_user_and_redacts_audit():
    from app.core import audit

    svc = UserService()
    created = svc.register(_make_user())
    svc.delete(created.id, actor_id=created.id)
    assert svc.repo.find_by_id(created.id) is None
    events = audit.replay_events()
    assert all(created.id not in str(event) for event in events)
    assert events[-1]["action"] == "SUBJECT_REDACTED"
