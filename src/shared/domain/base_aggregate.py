from src.shared.domain.base_entity import Entity
from src.shared.domain.domain_event import DomainEvent


class AggregateRoot(Entity):
    """Base class for aggregate roots. Collects domain events for deferred dispatch."""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        super().__init__(*args, **kwargs)
        self._domain_events: list[DomainEvent] = []

    def collect_events(self) -> list[DomainEvent]:
        """Return and clear all pending domain events."""
        events = list(self._domain_events)
        self._domain_events.clear()
        return events

    def _record_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)
