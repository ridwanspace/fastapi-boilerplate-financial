import asyncio
import json
from datetime import timedelta
from typing import BinaryIO

from google.cloud import storage
from google.oauth2 import service_account

from src.settings import Settings


class GCSStorageError(Exception):
    pass


class GCSStorage:
    """
    Google Cloud Storage adapter implementing StoragePort.
    Credentials are loaded from settings (file path or inline JSON).
    All blocking GCS SDK calls are offloaded to a thread pool via asyncio.
    """

    def __init__(self, settings: Settings) -> None:
        self._bucket_name = settings.gcs_bucket_name
        self._client = self._build_client(settings)

    def _build_client(self, settings: Settings) -> storage.Client:
        if settings.gcs_credentials_json:
            creds_dict = json.loads(settings.gcs_credentials_json)
            credentials = service_account.Credentials.from_service_account_info(creds_dict)  # type: ignore[no-untyped-call]
            return storage.Client(project=settings.gcs_project_id, credentials=credentials)

        if settings.gcs_credentials_path:
            credentials = service_account.Credentials.from_service_account_file(  # type: ignore[no-untyped-call]
                settings.gcs_credentials_path
            )
            return storage.Client(project=settings.gcs_project_id, credentials=credentials)

        # Application Default Credentials (ADC) — works in GCP environments
        return storage.Client(project=settings.gcs_project_id)

    async def upload(
        self,
        file: BinaryIO,
        destination_path: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        def _upload() -> str:
            bucket = self._client.bucket(self._bucket_name)
            blob = bucket.blob(destination_path)
            blob.upload_from_file(file, content_type=content_type)
            return destination_path

        return await asyncio.to_thread(_upload)

    async def download(self, source_path: str) -> bytes:
        def _download() -> bytes:
            bucket = self._client.bucket(self._bucket_name)
            blob = bucket.blob(source_path)
            return blob.download_as_bytes()  # type: ignore[no-any-return]

        return await asyncio.to_thread(_download)

    async def delete(self, path: str) -> None:
        def _delete() -> None:
            bucket = self._client.bucket(self._bucket_name)
            blob = bucket.blob(path)
            blob.delete()

        await asyncio.to_thread(_delete)

    async def get_signed_url(self, path: str, expiration_seconds: int = 3600) -> str:
        def _sign() -> str:
            bucket = self._client.bucket(self._bucket_name)
            blob = bucket.blob(path)
            return blob.generate_signed_url(  # type: ignore[no-any-return]
                expiration=timedelta(seconds=expiration_seconds),
                method="GET",
                version="v4",
            )

        return await asyncio.to_thread(_sign)

    async def exists(self, path: str) -> bool:
        def _exists() -> bool:
            bucket = self._client.bucket(self._bucket_name)
            blob = bucket.blob(path)
            return blob.exists()  # type: ignore[no-any-return]

        return await asyncio.to_thread(_exists)
