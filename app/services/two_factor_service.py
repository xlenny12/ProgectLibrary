import random
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage

from app.core.config import get_settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class TwoFactorEmailError(RuntimeError):
    pass


class TwoFactorService:
    def __init__(self):
        self.codes = {}

    def send_code_to_email(self, email: str, user_id: str, role: str) -> None:
        settings = get_settings()
        if not settings.smtp_user or not settings.smtp_password:
            raise TwoFactorEmailError("Email sending is not configured.")

        code = str(random.randint(100000, 999999))

        message = EmailMessage()
        message["Subject"] = "Library verification code"
        message["From"] = settings.smtp_user
        message["To"] = email
        message.set_content(f"Your verification code is: {code}")

        try:
            if settings.smtp_port == 465:
                with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port) as smtp:
                    smtp.login(settings.smtp_user, settings.smtp_password)
                    smtp.send_message(message)
            else:
                with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
                    smtp.starttls()
                    smtp.login(settings.smtp_user, settings.smtp_password)
                    smtp.send_message(message)
        except (OSError, smtplib.SMTPException) as exc:
            logger.error("Failed to send 2FA email to %s: %s", email, exc)
            raise TwoFactorEmailError("Could not send verification code.") from exc

        self.codes[email] = {
            "code": code,
            "user_id": user_id,
            "role": role,
            "expires_at": datetime.utcnow() + timedelta(minutes=5),
        }

    def verify_code(self, email: str, code: str):
        saved = self.codes.get(email)

        if not saved:
            return None

        if datetime.utcnow() > saved["expires_at"]:
            del self.codes[email]
            return None

        if saved["code"] != code:
            return None

        del self.codes[email]

        return {
            "user_id": saved["user_id"],
            "role": saved["role"],
        }
