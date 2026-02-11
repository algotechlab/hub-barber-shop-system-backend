import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from src.domain.execptions.upload import (
    FileTooLargeException,
    InvalidFileTypeException,
    UploadFailedException,
)
from src.infrastructure.storage.s3 import (
    S3Storage,
    _build_public_url,
    _guess_extension,
    _split_csv,
)


@pytest.mark.unit
class TestS3UrlBuilder:
    def test_build_public_url_uses_base_url(self):
        url = _build_public_url(
            bucket='b',
            region='us-east-1',
            key='k/a.png',
            base_url='https://cdn.example.com/',
        )
        assert url == 'https://cdn.example.com/k/a.png'

    def test_build_public_url_us_east_1_default(self):
        url = _build_public_url(bucket='b', region='us-east-1', key='x', base_url='')
        assert url == 'https://b.s3.amazonaws.com/x'

    def test_build_public_url_other_region_default(self):
        url = _build_public_url(bucket='b', region='sa-east-1', key='x', base_url='')
        assert url == 'https://b.s3.sa-east-1.amazonaws.com/x'


@pytest.mark.unit
class TestS3StorageUpload:
    def test_split_csv(self):
        assert _split_csv('a, b,,c') == {'a', 'b', 'c'}

    def test_guess_extension_prefers_filename(self):
        assert _guess_extension('photo.JPG', 'image/png') == '.jpg'

    def test_guess_extension_uses_content_type(self):
        assert _guess_extension(None, 'image/png') == '.png'

    def test_guess_extension_fallback(self):
        assert _guess_extension(None, None) == ''

    def test_from_settings_builds_client(self, monkeypatch):
        settings = SimpleNamespace(
            AWS_REGION='us-east-1',
            AWS_S3_ENDPOINT_URL='http://localhost:4566',
            AWS_ACCESS_KEY_ID='id',
            AWS_SECRET_ACCESS_KEY='secret',
        )
        monkeypatch.setattr(
            'src.infrastructure.storage.s3.get_settings', lambda: settings
        )
        fake_client = Mock()
        boto_client = Mock(return_value=fake_client)
        monkeypatch.setattr('src.infrastructure.storage.s3.boto3.client', boto_client)

        storage = S3Storage.from_settings()

        boto_client.assert_called_once()
        assert storage._client is fake_client  # noqa: SLF001

    @pytest.mark.asyncio
    async def test_rejects_invalid_content_type(self, monkeypatch):
        settings = SimpleNamespace(
            AWS_REGION='us-east-1',
            AWS_S3_BUCKET_NAME='bucket',
            AWS_S3_PUBLIC_BASE_URL='',
            AWS_S3_ENDPOINT_URL='',
            AWS_S3_PUBLIC_READ=True,
            AWS_ACCESS_KEY_ID='',
            AWS_SECRET_ACCESS_KEY='',
            S3_UPLOAD_MAX_SIZE_MB=5,
            S3_ALLOWED_IMAGE_CONTENT_TYPES='image/png',
        )
        monkeypatch.setattr(
            'src.infrastructure.storage.s3.get_settings', lambda: settings
        )

        client = Mock()
        storage = S3Storage(client=client)
        file = AsyncMock()
        file.filename = 'a.txt'
        file.content_type = 'text/plain'
        file.read.return_value = b'123'

        with pytest.raises(InvalidFileTypeException):
            await storage.upload_product_image(file=file, company_id=uuid.uuid4())

    @pytest.mark.asyncio
    async def test_rejects_large_file(self, monkeypatch):
        settings = SimpleNamespace(
            AWS_REGION='us-east-1',
            AWS_S3_BUCKET_NAME='bucket',
            AWS_S3_PUBLIC_BASE_URL='',
            AWS_S3_ENDPOINT_URL='',
            AWS_S3_PUBLIC_READ=True,
            AWS_ACCESS_KEY_ID='',
            AWS_SECRET_ACCESS_KEY='',
            S3_UPLOAD_MAX_SIZE_MB=1,
            S3_ALLOWED_IMAGE_CONTENT_TYPES='image/png',
        )
        monkeypatch.setattr(
            'src.infrastructure.storage.s3.get_settings', lambda: settings
        )

        client = Mock()
        storage = S3Storage(client=client)
        big = b'a' * (1024 * 1024 + 1)
        file = AsyncMock()
        file.filename = 'a.png'
        file.content_type = 'image/png'
        file.read.return_value = big

        with pytest.raises(FileTooLargeException):
            await storage.upload_product_image(file=file, company_id=uuid.uuid4())

    @pytest.mark.asyncio
    async def test_requires_bucket_name(self, monkeypatch):
        settings = SimpleNamespace(
            AWS_REGION='us-east-1',
            AWS_S3_BUCKET_NAME='',
            AWS_S3_PUBLIC_BASE_URL='',
            AWS_S3_ENDPOINT_URL='',
            AWS_S3_PUBLIC_READ=True,
            AWS_ACCESS_KEY_ID='',
            AWS_SECRET_ACCESS_KEY='',
            S3_UPLOAD_MAX_SIZE_MB=5,
            S3_ALLOWED_IMAGE_CONTENT_TYPES='image/png',
        )
        monkeypatch.setattr(
            'src.infrastructure.storage.s3.get_settings', lambda: settings
        )

        client = Mock()
        storage = S3Storage(client=client)
        file = AsyncMock()
        file.filename = 'a.png'
        file.content_type = 'image/png'
        file.read.return_value = b'123'

        with pytest.raises(UploadFailedException):
            await storage.upload_product_image(file=file, company_id=uuid.uuid4())

    @pytest.mark.asyncio
    async def test_upload_success_calls_put_object_and_returns_url(self, monkeypatch):
        settings = SimpleNamespace(
            AWS_REGION='us-east-1',
            AWS_S3_BUCKET_NAME='bucket',
            AWS_S3_PUBLIC_BASE_URL='https://cdn.example.com',
            AWS_S3_ENDPOINT_URL='',
            AWS_S3_PUBLIC_READ=True,
            AWS_ACCESS_KEY_ID='',
            AWS_SECRET_ACCESS_KEY='',
            S3_UPLOAD_MAX_SIZE_MB=5,
            S3_ALLOWED_IMAGE_CONTENT_TYPES='image/png',
        )
        monkeypatch.setattr(
            'src.infrastructure.storage.s3.get_settings', lambda: settings
        )

        async def immediate(fn, *args, **kwargs):
            return fn(*args, **kwargs)

        monkeypatch.setattr(
            'src.infrastructure.storage.s3.run_in_threadpool', immediate
        )

        client = Mock()
        storage = S3Storage(client=client)
        file = AsyncMock()
        file.filename = 'a.png'
        file.content_type = 'image/png'
        file.read.return_value = b'123'

        result = await storage.upload_product_image(
            file=file, company_id=uuid.UUID(int=1)
        )

        assert result.url.startswith('https://cdn.example.com/companies/')
        assert result.key.startswith('companies/')
        client.put_object.assert_called_once()
