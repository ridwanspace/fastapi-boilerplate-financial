from typing import Protocol, runtime_checkable


@runtime_checkable
class UnitOfWork(Protocol):
    """
    Coordinates atomic operations across one or more repositories.
    Usage:
        async with uow:
            repo = SomeRepository(uow.session)
            await repo.save(entity)
            await uow.commit()
    """

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...

    async def __aenter__(self) -> "UnitOfWork": ...

    async def __aexit__(self, *args: object) -> None: ...
