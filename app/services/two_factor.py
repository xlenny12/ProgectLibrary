# app/routers/two_factor.py
# ─────────────────────────────────────────────────────────────
# Роутер для двофакторної аутентифікації
# Підключається окремо від auth.py — нічого не змінює
# ─────────────────────────────────────────────────────────────

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

from app.services.two_factor_service import (
    generate_and_send_code,
    verify_code,
    mask_email,
    CodeExpiredError,
    CodeInvalidError,
    CodeNotFoundError,
    TooManyAttemptsError,
)
from app.services.user_service import UserService
from app.core.security import create_access_token, create_refresh_token

router = APIRouter(prefix="/api/2fa", tags=["2fa"])


# ─── Схеми запитів / відповідей ──────────────────────────────

class LoginStep1Request(BaseModel):
    email: EmailStr
    password: str

class LoginStep1Response(BaseModel):
    message: str
    masked_email: str

class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class ResendRequest(BaseModel):
    email: EmailStr


# ─── Ендпоінти ───────────────────────────────────────────────

@router.post("/login", response_model=LoginStep1Response)
def login_step1(data: LoginStep1Request):
    """
    Крок 1: перевіряє email + пароль, відправляє 2FA код на пошту.

    - Якщо дані вірні — надсилає 6-значний код на email
    - Повертає замаскований email для відображення в UI
    - Raises 401 якщо credentials невірні
    """
    try:
        user = UserService().authenticate(data.email, data.password)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний email або пароль."
        )

    try:
        generate_and_send_code(data.email, getattr(user, "full_name", ""))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Не вдалося відправити код. Спробуйте пізніше. ({e})"
        )

    return LoginStep1Response(
        message="Код підтвердження відправлено на вашу пошту.",
        masked_email=mask_email(data.email),
    )


@router.post("/verify", response_model=TokenResponse)
def login_step2(data: VerifyCodeRequest):
    """
    Крок 2: перевіряє 6-значний код, повертає JWT токени.

    - Код дійсний 10 хвилин
    - Максимум 5 спроб, після чого треба логінитися знову
    - Raises 400 якщо код невірний або прострочений
    """
    try:
        verify_code(data.email, data.code)
    except (CodeNotFoundError, CodeExpiredError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except CodeInvalidError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except TooManyAttemptsError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))

    # Код вірний — завантажуємо користувача і видаємо токени
    from app.repositories.user_repo import UserRepository
    user = UserRepository().find_by_email(data.email)
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено.")

    return TokenResponse(
        access_token=create_access_token(user.id, user.role.value),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/resend")
def resend_code(data: ResendRequest):
    """
    Повторна відправка коду (якщо не дійшов).

    Потребує що користувач вже пройшов крок 1 (login).
    """
    from app.repositories.user_repo import UserRepository
    user = UserRepository().find_by_email(data.email)
    if not user:
        # Не розкриваємо чи існує email
        raise HTTPException(status_code=400, detail="Спробуйте увійти знову.")

    try:
        generate_and_send_code(data.email, getattr(user, "full_name", ""))
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Помилка відправки: {e}")

    return {"message": "Новий код відправлено."}