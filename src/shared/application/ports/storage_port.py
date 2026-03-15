from typing import BinaryIO, Protocol, runtime_checkable


@runtime_checkable
class StoragePort(Protocol):
    """
    Abstract port for object storage operations.
    Implementations: GCSStorage, S3Storage, FakeStorage (tests).
    """

    async def upload(
        self,
        file: BinaryIO,
        destination_path: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Upload a file and return its storage path."""
        ...

    async def download(self, source_path: str) -> bytes:
        """Download a file by its storage path."""
        ...

    async def delete(self, path: str) -> None:
        """Delete a file by its storage path."""
        ...

    async def get_signed_url(self, path: str, expiration_seconds: int = 3600) -> str:
        """Generate a time-limited signed URL for direct client access."""
        ...

    async def exists(self, path: str) -> bool:
        """Check if a file exists at the given path."""
        ...
