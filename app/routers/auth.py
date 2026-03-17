from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
from pydantic import BaseModel
from app.services.user_service import UserService
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.models.user import UserCreate
from app.models.user import UserSelf

router = APIRouter(prefix="/api/auth", tags=["auth"])


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@router.post("/register", response_model=UserSelf, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate):
    """Register a new user account.
    
    Anyone can register. New users default to 'User' role.
    Email must be unique and valid.
    
    Returns: Created user profile (excluding password)
    Raises: 400 if email already exists or validation fails
    """
    try:
        return UserService().register(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user and return access + refresh tokens.
    
    Username field should contain the user's email address.
    
    Returns: JWT access token (30min expiry) + refresh token (7 days)
    Raises: 401 if credentials are invalid
    """
    try:
        user = UserService().authenticate(form.username, form.password)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    return TokenResponse(
        access_token=create_access_token(user.id, user.role.value),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(refresh_token: str):
    """Refresh an expired access token using a valid refresh token.
    
    The refresh token must be from a previous login and not expired (7 days).
    
    Returns: New JWT access token (30min) + new refresh token (7 days)
    Raises: 401 if refresh token is invalid or expired
    """
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
