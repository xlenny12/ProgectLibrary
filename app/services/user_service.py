"""
UserService — all user-related business logic.
"""
import uuid
from datetime import date
from app.models.user import UserCreate, UserInDB, UserPublic, UserSelf, UserUpdate, Role
from app.repositories.user_repo import UserRepository
from app.core.security import hash_password, verify_password
from app.core import audit


class UserService:
    def __init__(self, repo: UserRepository | None = None):
        self.repo = repo or UserRepository()

    def register(self, data: UserCreate, actor_id: str = "self") -> UserSelf:
        if self.repo.find_by_email(data.email):
            raise ValueError("A user with this email already exists.")
        try:
            date.fromisoformat(data.date_of_birth)
        except ValueError:
            raise ValueError("date_of_birth must be a valid ISO date (YYYY-MM-DD).")
        user = UserInDB(
            id=str(uuid.uuid4()),
            full_name=data.full_name,
            date_of_birth=data.date_of_birth,
            address=data.address,
            phone=data.phone,
            email=data.email,
            role=data.role,
            password_hash=hash_password(data.password),
        )
        self.repo.save(user)
        audit.log(actor_id, "USER_CREATED", {"user_id": user.id, "email": user.email})
        return UserSelf(**user.model_dump(exclude={"password_hash"}))

    def authenticate(self, email: str, password: str) -> UserInDB:
        user = self.repo.find_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password.")
        audit.log(user.id, "USER_LOGIN", {})
        return user

    def get_self(self, user_id: str) -> UserSelf:
        user = self.repo.find_by_id(user_id)
        if not user:
            raise ValueError("User not found.")
        return UserSelf(**user.model_dump(exclude={"password_hash"}))

    def get_public(self, user_id: str) -> UserPublic:
        user = self.repo.find_by_id(user_id)
        if not user:
            raise ValueError("User not found.")
        return UserPublic(id=user.id, full_name=user.full_name, role=user.role)

    def list_public(self) -> list[UserPublic]:
        return [UserPublic(id=u.id, full_name=u.full_name, role=u.role) for u in self.repo.all()]

    def update(self, user_id: str, data: UserUpdate, actor_id: str) -> UserSelf:
        user = self.repo.find_by_id(user_id)
        if not user:
            raise ValueError("User not found.")
        updated = user.model_copy(update={k: v for k, v in data.model_dump().items() if v is not None})
        self.repo.save(updated)
        audit.log(actor_id, "USER_UPDATED", {"user_id": user_id})
        return UserSelf(**updated.model_dump(exclude={"password_hash"}))

    def delete(self, user_id: str, actor_id: str) -> None:
        """GDPR delete — removes all user data."""
        if not self.repo.delete(user_id):
            raise ValueError("User not found.")
        audit.log(actor_id, "USER_DELETED_GDPR", {"user_id": user_id})

    def admin_delete(self, user_id: str, actor_id: str) -> None:
        if not self.repo.delete(user_id):
            raise ValueError("User not found.")
        audit.log(actor_id, "USER_DELETED_ADMIN", {"user_id": user_id})
