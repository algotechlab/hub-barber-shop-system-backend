from __future__ import annotations

import mimetypes
from dataclasses import dataclass
from uuid import UUID, uuid4

import boto3
from botocore.client import BaseClient
from fastapi import UploadFile
from starlette.concurrency import run_in_threadpool

from src.core.config.settings import get_settings
from src.domain.execptions.upload import (
    FileTooLargeException,
    InvalidFileTypeException,
    UploadFailedException,
)

MAX_EXTENSION_LEN = 10


def _split_csv(value: str) -> set[str]:
    return {v.strip() for v in value.split(',') if v.strip()}


def _guess_extension(filename: str | None, content_type: str | None) -> str:
    if filename and '.' in filename:
        ext = '.' + filename.rsplit('.', 1)[-1].lower()
        if len(ext) <= MAX_EXTENSION_LEN:
            return ext
    if content_type:
        ext = mimetypes.guess_extension(content_type) or ''
        if ext:
            return ext
    return ''


def _build_public_url(*, bucket: str, region: str, key: str, base_url: str) -> str:
    if base_url:
        return f'{base_url.rstrip("/")}/{key.lstrip("/")}'
    if region == 'us-east-1':
        return f'https://{bucket}.s3.amazonaws.com/{key}'
    return f'https://{bucket}.s3.{region}.amazonaws.com/{key}'


@dataclass(frozen=True, slots=True)
class UploadResult:
    url: str
    key: str
    content_type: str
    size_bytes: int


class S3Storage:
    def __init__(self, client: BaseClient):
        self._client = client

    @staticmethod
    def from_settings() -> S3Storage:
        settings = get_settings()

        kwargs: dict[str, object] = {'region_name': settings.AWS_REGION}

        if settings.AWS_S3_ENDPOINT_URL:
            kwargs['endpoint_url'] = settings.AWS_S3_ENDPOINT_URL

        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            kwargs['aws_access_key_id'] = settings.AWS_ACCESS_KEY_ID
            kwargs['aws_secret_access_key'] = settings.AWS_SECRET_ACCESS_KEY

        client = boto3.client('s3', **kwargs)
        return S3Storage(client=client)

    async def upload_product_image(
        self,
        *,
        file: UploadFile,
        company_id: UUID,
    ) -> UploadResult:
        settings = get_settings()

        allowed = _split_csv(settings.S3_ALLOWED_IMAGE_CONTENT_TYPES)
        content_type = (file.content_type or '').lower()
        if not content_type or content_type not in allowed:
            raise InvalidFileTypeException('Tipo de arquivo inválido')

        data = await file.read()
        size_bytes = len(data)
        max_bytes = settings.S3_UPLOAD_MAX_SIZE_MB * 1024 * 1024
        if size_bytes > max_bytes:
            raise FileTooLargeException('Arquivo muito grande')

        if not settings.AWS_S3_BUCKET_NAME:
            raise UploadFailedException('Bucket não configurado')

        ext = _guess_extension(file.filename, content_type)
        key = f'companies/{company_id}/products/{uuid4().hex}{ext}'

        extra_args: dict[str, str] = {'ContentType': content_type}
        if settings.AWS_S3_PUBLIC_READ:
            extra_args['ACL'] = 'public-read'

        try:
            await run_in_threadpool(
                self._client.put_object,
                Bucket=settings.AWS_S3_BUCKET_NAME,
                Key=key,
                Body=data,
                **extra_args,
            )
        except Exception as error:  # pragma: no cover (driver-specific)
            raise UploadFailedException('Erro ao enviar arquivo') from error

        url = _build_public_url(
            bucket=settings.AWS_S3_BUCKET_NAME,
            region=settings.AWS_REGION,
            key=key,
            base_url=settings.AWS_S3_PUBLIC_BASE_URL,
        )
        return UploadResult(
            url=url, key=key, content_type=content_type, size_bytes=size_bytes
        )

    async def upload_service_image(
        self,
        *,
        file: UploadFile,
        company_id: UUID,
    ) -> UploadResult:
        settings = get_settings()

        allowed = _split_csv(settings.S3_ALLOWED_IMAGE_CONTENT_TYPES)
        content_type = (file.content_type or '').lower()
        if not content_type or content_type not in allowed:
            raise InvalidFileTypeException('Tipo de arquivo inválido')

        data = await file.read()
        size_bytes = len(data)
        max_bytes = settings.S3_UPLOAD_MAX_SIZE_MB * 1024 * 1024
        if size_bytes > max_bytes:
            raise FileTooLargeException('Arquivo muito grande')

        if not settings.AWS_S3_BUCKET_NAME:
            raise UploadFailedException('Bucket não configurado')

        ext = _guess_extension(file.filename, content_type)
        key = f'companies/{company_id}/services/{uuid4().hex}{ext}'

        extra_args: dict[str, str] = {'ContentType': content_type}
        if settings.AWS_S3_PUBLIC_READ:
            extra_args['ACL'] = 'public-read'

        try:
            await run_in_threadpool(
                self._client.put_object,
                Bucket=settings.AWS_S3_BUCKET_NAME,
                Key=key,
                Body=data,
                **extra_args,
            )
        except Exception as error:  # pragma: no cover (driver-specific)
            raise UploadFailedException('Erro ao enviar arquivo') from error

        url = _build_public_url(
            bucket=settings.AWS_S3_BUCKET_NAME,
            region=settings.AWS_REGION,
            key=key,
            base_url=settings.AWS_S3_PUBLIC_BASE_URL,
        )
        return UploadResult(
            url=url, key=key, content_type=content_type, size_bytes=size_bytes
        )
