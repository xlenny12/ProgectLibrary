"""
NotificationService — SMS via Twilio, email via SMTP.
Both methods are no-ops when credentials are not configured (dev mode).
"""
import smtplib
from email.mime.text import MIMEText
from app.core.config import get_settings
from app.core.logger import get_logger
from app.core import audit
from app.models.user import UserInDB
from app.models.borrow import BorrowInDB

logger = get_logger(__name__)


class NotificationService:
    def send_overdue_sms(self, user: UserInDB, borrow: BorrowInDB) -> bool:
        settings = get_settings()
        if not all([settings.twilio_account_sid, settings.twilio_auth_token, settings.twilio_from_number]):
            logger.info(f"SMS skipped (no credentials): user={user.email}, borrow={borrow.id}")
            return False
        try:
            from twilio.rest import Client
            client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
            client.messages.create(
                body=f"Library reminder: your book (due {borrow.due_date()}) is overdue. Please return it.",
                from_=settings.twilio_from_number,
                to=user.phone,
            )
            audit.log("system", "SMS_SENT", {"user_id": user.id, "borrow_id": borrow.id})
            return True
        except Exception as e:
            audit.log("system", "SMS_FAILED", {"user_id": user.id, "error": str(e)})
            return False

    def send_overdue_email(self, user: UserInDB, borrow: BorrowInDB) -> bool:
        settings = get_settings()
        if not all([settings.smtp_user, settings.smtp_password]):
            logger.info(f"Email skipped (no credentials): user={user.email}, borrow={borrow.id}")
            return False
        try:
            msg = MIMEText(
                f"Dear {user.full_name},\n\n"
                f"Your borrowed book (borrow ID: {borrow.id}) was due on {borrow.due_date()}.\n"
                f"Please return it to the library as soon as possible.\n\nLibrary System"
            )
            msg["Subject"] = "Library — Overdue Book Reminder"
            msg["From"] = settings.smtp_user
            msg["To"] = user.email
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                server.starttls()
                server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(msg)
            audit.log("system", "EMAIL_SENT", {"user_id": user.id, "borrow_id": borrow.id})
            return True
        except Exception as e:
            audit.log("system", "EMAIL_FAILED", {"user_id": user.id, "error": str(e)})
            return False
