import hmac
import secrets
import smtplib
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage

from app.core import audit
from app.core.config import get_settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class TwoFactorEmailError(RuntimeError):
    pass


class TwoFactorService:
    def __init__(self) -> None:
        self._pending: dict[str, dict[str, object]] = {}

    def send_code_to_email(self, email: str, user_id: str, role: str) -> str | None:
        code = self._generate_code()
        self._store_code(email, code, user_id, role)
        return self._send_email(email, code, user_id)

    def verify_code(self, email: str, code: str) -> dict[str, str] | None:
        key = self._normalize_email(email)
        saved = self._pending.get(key)

        if not saved:
            return None

        if datetime.now(timezone.utc) > saved["expires_at"]:
            self._pending.pop(key, None)
            return None

        if not hmac.compare_digest(str(saved["code_hash"]), self._hash_code(code)):
            saved["attempts"] = int(saved["attempts"]) + 1
            if int(saved["attempts"]) >= get_settings().two_factor_max_attempts:
                self._pending.pop(key, None)
                audit.log(str(saved["user_id"]), "TWO_FACTOR_LOCKED", {})
            return None

        self._pending.pop(key, None)
        audit.log(str(saved["user_id"]), "TWO_FACTOR_VERIFIED", {})
        return {
            "user_id": str(saved["user_id"]),
            "role": str(saved["role"]),
        }

    def _store_code(self, email: str, code: str, user_id: str, role: str) -> None:
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=get_settings().two_factor_code_ttl_minutes)
        self._pending[self._normalize_email(email)] = {
            "code_hash": self._hash_code(code),
            "user_id": user_id,
            "role": role,
            "expires_at": expires_at,
            "attempts": 0,
        }

    def _send_email(self, email: str, code: str, user_id: str) -> str | None:
        settings = get_settings()
        if not settings.smtp_user or not settings.smtp_password:
            if settings.app_env.lower() == "production":
                self._pending.pop(self._normalize_email(email), None)
                raise TwoFactorEmailError("Email sending is not configured.")
            logger.warning("Development 2FA code for %s: %s", email, code)
            audit.log(user_id, "TWO_FACTOR_CODE_LOGGED_DEV", {})
            return code

        message = EmailMessage()
        message["Subject"] = "Readly verification code"
        message["From"] = settings.smtp_user
        message["To"] = email
        message.set_content(f"Your Readly verification code is: {code}\n\nThis code expires in 5 minutes.")

        try:
            if settings.smtp_port == 465:
                with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port) as server:
                    server.login(settings.smtp_user, settings.smtp_password)
                    server.send_message(message)
            else:
                with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                    server.starttls()
                    server.login(settings.smtp_user, settings.smtp_password)
                    server.send_message(message)
            audit.log(user_id, "TWO_FACTOR_CODE_SENT", {})
            return None
        except (OSError, smtplib.SMTPException) as exc:
            self._pending.pop(self._normalize_email(email), None)
            audit.log(user_id, "TWO_FACTOR_CODE_FAILED", {"error_type": type(exc).__name__})
            logger.error("Failed to send 2FA code to %s: %s", email, exc)
            raise TwoFactorEmailError("Could not send verification code.") from exc

    @staticmethod
    def _generate_code() -> str:
        return "".join(secrets.choice("0123456789") for _ in range(6))

    @staticmethod
    def _normalize_email(email: str) -> str:
        return email.strip().lower()

    @staticmethod
    def _hash_code(code: str) -> str:
        return hmac.new(
            get_settings().secret_key.encode("utf-8"),
            code.strip().encode("utf-8"),
            "sha256",
        ).hexdigest()
