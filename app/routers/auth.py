from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.core import audit
from app.core.config import get_settings
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.models.user import UserRegistration, UserSelf
from app.services.two_factor_service import TwoFactorEmailError, TwoFactorService
from app.services.user_service import UserService

router = APIRouter(prefix="/api/auth", tags=["auth"])
two_factor_service = TwoFactorService()


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginTwoFactorResponse(BaseModel):
    message: str
    requires_2fa: bool = True
    email: str
    dev_code: str | None = None


class VerifyTwoFactorRequest(BaseModel):
    email: str
    code: str


@router.post("/register", response_model=UserSelf, status_code=status.HTTP_201_CREATED)
def register(data: UserRegistration):
    try:
        return UserService().register(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse | LoginTwoFactorResponse)
def login(form: OAuth2PasswordRequestForm = Depends()):
    settings = get_settings()
    try:
        user = UserService().authenticate(form.username, form.password, log_success=not settings.two_factor_enabled)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")

    if settings.two_factor_enabled:
        try:
            dev_code = two_factor_service.send_code_to_email(user.email, user.id, user.role.value)
        except TwoFactorEmailError as exc:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

        return LoginTwoFactorResponse(
            message="Verification code sent to email.",
            email=user.email,
            dev_code=dev_code,
        )

    return TokenResponse(
        access_token=create_access_token(user.id, user.role.value),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/verify-2fa", response_model=TokenResponse)
def verify_2fa(data: VerifyTwoFactorRequest):
    pending_login = two_factor_service.verify_code(data.email, data.code)

    if not pending_login:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code.",
        )

    audit.log(pending_login["user_id"], "USER_LOGIN", {})

    return TokenResponse(
        access_token=create_access_token(pending_login["user_id"], pending_login["role"]),
        refresh_token=create_refresh_token(pending_login["user_id"]),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(refresh_token: str):
    try:
        payload = decode_token(refresh_token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid refresh token.")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Wrong token type.")

    from app.repositories.user_repo import UserRepository

    user = UserRepository().find_by_id(payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found.")

    return TokenResponse(
        access_token=create_access_token(user.id, user.role.value),
        refresh_token=create_refresh_token(user.id),
    )
