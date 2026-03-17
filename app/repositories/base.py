"""
Generic encrypted file repository.

File format (plaintext after decryption):
  RECORD_TYPE|field1|field2|...|fieldN
  One record per line. Empty lines ignored.

Subclasses define:
  RECORD_TYPE: str
  _to_line(obj) -> str
  _from_line(parts: list[str]) -> T
"""
from pathlib import Path
from typing import TypeVar, Generic, Iterator
from app.core.crypto import encrypt, decrypt
from app.core.config import get_settings

T = TypeVar("T")


class FileRepository(Generic[T]):
    RECORD_TYPE: str = "RECORD"

    def _get_path(self) -> Path:
        raise NotImplementedError

    def _to_line(self, obj: T) -> str:
        raise NotImplementedError

    def _from_line(self, parts: list[str]) -> T:
        raise NotImplementedError

    # ── internal helpers ────────────────────────────────────────────────────

    def _read_all_lines(self) -> list[str]:
        path = self._get_path()
        if not path.exists() or path.stat().st_size == 0:
            return []
        return [l for l in decrypt(path.read_bytes()).splitlines() if l.strip()]

    def _write_all_lines(self, lines: list[str]) -> None:
        self._get_path().write_bytes(encrypt("\n".join(lines)))

    def _iter_records(self) -> Iterator[T]:
        for line in self._read_all_lines():
            parts = line.split("|")
            if parts[0] == self.RECORD_TYPE:
                yield self._from_line(parts[1:])

    # ── public API ──────────────────────────────────────────────────────────

    def all(self) -> list[T]:
        return list(self._iter_records())

    def find_by_id(self, id_: str) -> T | None:
        for obj in self._iter_records():
            if getattr(obj, "id", None) == id_:
                return obj
        return None

    def save(self, obj: T) -> None:
        """Insert or replace (matched by obj.id)."""
        lines = self._read_all_lines()
        new_line = f"{self.RECORD_TYPE}|{self._to_line(obj)}"
        replaced = False
        for i, line in enumerate(lines):
            parts = line.split("|")
            if parts[0] == self.RECORD_TYPE and parts[1] == getattr(obj, "id", ""):
                lines[i] = new_line
                replaced = True
                break
        if not replaced:
            lines.append(new_line)
        self._write_all_lines(lines)

    def delete(self, id_: str) -> bool:
        lines = self._read_all_lines()
        new_lines = [
            l for l in lines
            if not (l.startswith(self.RECORD_TYPE + "|") and l.split("|")[1] == id_)
        ]
        if len(new_lines) == len(lines):
            return False
        self._write_all_lines(new_lines)
        return True
