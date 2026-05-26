import uuid

from app.core import audit
from app.core.security import hash_password, verify_password
from app.models.user import Role, UserCreate, UserInDB, UserPublic, UserRegistration, UserSelf, UserUpdate
from app.repositories.user_repo import UserRepository


class UserService:
    def __init__(self, repo: UserRepository | None = None):
        self.repo = repo or UserRepository()

    def register(
        self,
        data: UserCreate | UserRegistration,
        actor_id: str = "self",
        allow_role_selection: bool = False,
    ) -> UserSelf:
        if self.repo.find_by_email(data.email):
            raise ValueError("A user with this email already exists.")

        requested_role = getattr(data, "role", Role.USER)
        if requested_role != Role.USER and not allow_role_selection:
            audit.log(
                "anonymous",
                "ROLE_ESCALATION_BLOCKED",
                {"email_ref": audit.subject_ref(str(data.email)), "requested_role": requested_role.value},
            )
            raise ValueError("Only administrators can assign roles.")

        user = UserInDB(
            id=str(uuid.uuid4()),
            full_name=data.full_name,
            date_of_birth=data.date_of_birth,
            address=data.address,
            phone=data.phone,
            email=data.email,
            role=requested_role if allow_role_selection else Role.USER,
            password_hash=hash_password(data.password),
        )
        self.repo.save(user)
        event_actor = user.id if actor_id == "self" else actor_id
        audit.log(event_actor, "USER_CREATED", {"user": user.model_dump(mode="json")})
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
        return UserPublic(id=user.id, role=user.role)

    def list_public(self) -> list[UserPublic]:
        return [UserPublic(id=user.id, role=user.role) for user in self.repo.all()]

    def update(self, user_id: str, data: UserUpdate, actor_id: str) -> UserSelf:
        user = self.repo.find_by_id(user_id)
        if not user:
            raise ValueError("User not found.")
        if data.email and data.email != user.email:
            existing = self.repo.find_by_email(data.email)
            if existing and existing.id != user_id:
                raise ValueError("A user with this email already exists.")

        updated = user.model_copy(update={k: v for k, v in data.model_dump().items() if v is not None})
        self.repo.save(updated)
        audit.log(actor_id, "USER_UPDATED", {"user": updated.model_dump(mode="json")})
        return UserSelf(**updated.model_dump(exclude={"password_hash"}))

    def delete(self, user_id: str, actor_id: str) -> None:
        """GDPR delete: remove the user row and redact prior subject audit events."""
        if not self.repo.delete(user_id):
            raise ValueError("User not found.")
        audit.redact_subject(user_id, actor_id=actor_id, reason="GDPR_DELETE")

    def admin_delete(self, user_id: str, actor_id: str) -> None:
        if not self.repo.delete(user_id):
            raise ValueError("User not found.")
        audit.log(actor_id, "USER_DELETED_ADMIN", {"user_id": user_id})
