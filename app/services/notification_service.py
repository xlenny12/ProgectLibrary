import smtplib
from email.mime.text import MIMEText

from app.core import audit
from app.core.config import get_settings
from app.core.logger import get_logger
from app.models.borrow import BorrowInDB
from app.models.user import UserInDB

logger = get_logger(__name__)


class NotificationService:
    def send_overdue_sms(self, user: UserInDB, borrow: BorrowInDB) -> bool:
        settings = get_settings()
        if not all([settings.twilio_account_sid, settings.twilio_auth_token, settings.twilio_from_number]):
            logger.info(f"SMS no-op: credentials are not configured. user_id={user.id}, borrow={borrow.id}")
            audit.log("system", "SMS_SKIPPED", {"user_id": user.id, "borrow_id": borrow.id, "reason": "missing_credentials"})
            return False

        try:
            from twilio.rest import Client

            client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
            client.messages.create(
                body=f"Library reminder: your book (due {borrow.due_date}) is overdue. Please return it.",
                from_=settings.twilio_from_number,
                to=user.phone,
            )
            audit.log("system", "SMS_SENT", {"user_id": user.id, "borrow_id": borrow.id})
            return True
        except Exception as exc:
            audit.log("system", "SMS_FAILED", {"user_id": user.id, "error_type": type(exc).__name__})
            return False

    def send_overdue_email(self, user: UserInDB, borrow: BorrowInDB) -> bool:
        settings = get_settings()
        if not all([settings.smtp_user, settings.smtp_password]):
            logger.info(f"Email no-op: credentials are not configured. user_id={user.id}, borrow={borrow.id}")
            audit.log("system", "EMAIL_SKIPPED", {"user_id": user.id, "borrow_id": borrow.id, "reason": "missing_credentials"})
            return False

        try:
            msg = MIMEText(
                f"Dear {user.full_name},\n\n"
                f"Your borrowed book (borrow ID: {borrow.id}) was due on {borrow.due_date}.\n"
                "Please return it to the library as soon as possible.\n\n"
                "Library System"
            )
            msg["Subject"] = "Library - Overdue Book Reminder"
            msg["From"] = settings.smtp_user
            msg["To"] = user.email
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                server.starttls()
                server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(msg)
            audit.log("system", "EMAIL_SENT", {"user_id": user.id, "borrow_id": borrow.id})
            return True
        except Exception as exc:
            audit.log("system", "EMAIL_FAILED", {"user_id": user.id, "error_type": type(exc).__name__})
            return False
