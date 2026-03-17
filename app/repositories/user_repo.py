from pathlib import Path
from app.core.config import get_settings
from app.models.user import UserInDB, Role
from app.repositories.base import FileRepository


class UserRepository(FileRepository[UserInDB]):
    RECORD_TYPE = "USER"

    def _get_path(self) -> Path:
        return get_settings().data_dir / "users.dat"

    def _to_line(self, obj: UserInDB) -> str:
        return "|".join([
            obj.id, obj.full_name, obj.date_of_birth,
            obj.address, obj.phone, obj.email,
            obj.role.value, obj.password_hash,
        ])

    def _from_line(self, parts: list[str]) -> UserInDB:
        return UserInDB(
            id=parts[0], full_name=parts[1], date_of_birth=parts[2],
            address=parts[3], phone=parts[4], email=parts[5],
            role=Role(parts[6]), password_hash=parts[7],
        )

    def find_by_email(self, email: str) -> UserInDB | None:
        for u in self._iter_records():
            if u.email.lower() == email.lower():
                return u
        return None
