from dataclasses import dataclass


@dataclass(frozen=True)
class ValueObject:
    """
    Base class for value objects.
    Immutable by default (frozen=True). Equality is determined by field values.
    Subclasses should define fields as dataclass fields.
    """
