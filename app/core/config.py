from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Security
    secret_key: str = "changeme"
    fernet_key: str = ""
    audit_hmac_key: str = ""
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    two_factor_enabled: bool = True
    two_factor_code_ttl_minutes: int = 5
    two_factor_max_attempts: int = 5

    # Storage
    data_dir: Path = Path("./data")

    # Twilio
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""

    # Email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

    # App
    app_env: str = "development"
    log_level: str = "INFO"

    def ensure_data_dir(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def validate_security(self) -> None:
        """Fail fast for production deployments with unsafe placeholder secrets."""
        if self.app_env.lower() != "production":
            return
        if self.secret_key == "changeme" or len(self.secret_key) < 32:
            raise RuntimeError("SECRET_KEY must be a unique 32+ character secret in production.")
        if not self.fernet_key:
            raise RuntimeError("FERNET_KEY must be configured in production.")
        if not self.audit_hmac_key or len(self.audit_hmac_key) < 32:
            raise RuntimeError("AUDIT_HMAC_KEY must be a unique 32+ character secret in production.")
        if self.two_factor_enabled and not all([self.smtp_user, self.smtp_password]):
            raise RuntimeError("SMTP_USER and SMTP_PASSWORD must be configured when 2FA is enabled in production.")


@lru_cache
def get_settings() -> Settings:
    return Settings()
