import uuid
from datetime import UTC, datetime


class Entity:
    """Base class for all domain entities. Identity is defined by id, not attributes."""

    def __init__(self, id: uuid.UUID | None = None) -> None:
        self._id = id or uuid.uuid4()
        self._created_at: datetime = datetime.now(UTC)
        self._updated_at: datetime = datetime.now(UTC)

    @property
    def id(self) -> uuid.UUID:
        return self._id

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def _touch(self) -> None:
        self._updated_at = datetime.now(UTC)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id})"
