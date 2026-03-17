"""
Notification tests — verify no-op mode and that audit entries are written
without real Twilio/SMTP credentials.
"""
from unittest.mock import patch, MagicMock
from app.services.notification_service import NotificationService
from app.models.user import UserInDB, Role
from app.models.borrow import BorrowInDB
from datetime import date, timedelta


def _make_user():
    return UserInDB(
        id="u1", full_name="Test User", email="test@example.com",
        phone="+380991234567", role=Role.USER,
        date_of_birth="1990-01-01", address="Lviv",
        password_hash="x",
    )


def _make_overdue_borrow():
    past = (date.today() - timedelta(days=5)).isoformat()
    return BorrowInDB(id="b1", user_id="u1", book_id="bk1", date_taken=past, days=1, quantity=1)


def test_sms_noop_when_no_credentials(capsys):
    svc = NotificationService()
    result = svc.send_overdue_sms(_make_user(), _make_overdue_borrow())
    assert result is False
    captured = capsys.readouterr()
    assert "no-op" in captured.out


def test_email_noop_when_no_credentials(capsys):
    svc = NotificationService()
    result = svc.send_overdue_email(_make_user(), _make_overdue_borrow())
    assert result is False
    captured = capsys.readouterr()
    assert "no-op" in captured.out


# def test_sms_sends_when_credentials_set(monkeypatch):
#     monkeypatch.setenv("TWILIO_ACCOUNT_SID", "ACtest")
#     monkeypatch.setenv("TWILIO_AUTH_TOKEN", "token")
#     monkeypatch.setenv("TWILIO_FROM_NUMBER", "+1555000000")
#     from app.core.config import get_settings
#     get_settings.cache_clear()

#     mock_client = MagicMock()
#     with patch("app.services.notification_service.Client", return_value=mock_client):
#         svc = NotificationService()
#         result = svc.send_overdue_sms(_make_user(), _make_overdue_borrow())
#     assert result is True
#     mock_client.messages.create.assert_called_once()

def test_sms_sends_when_credentials_set(monkeypatch):
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "ACtest")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "token")
    monkeypatch.setenv("TWILIO_FROM_NUMBER", "+1555000000")
    from app.core.config import get_settings
    get_settings.cache_clear()

    mock_client = MagicMock()
    with patch("twilio.rest.Client", return_value=mock_client):
        svc = NotificationService()
        result = svc.send_overdue_sms(_make_user(), _make_overdue_borrow())
    assert result is True
    mock_client.messages.create.assert_called_once()