import os
from functools import lru_cache
from typing import Any, ClassVar, List, Union

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurações de ambiente usando pydantic_settings.
    O arquivo .env deve estar na mesma pasta ou ser informado via env_file.
    """

    ENVIRONMENT: ClassVar[str] = os.getenv('ENVIRONMENT', 'production')
    model_config = SettingsConfigDict(
        env_file='.env.test' if ENVIRONMENT == 'test' else '.env',
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore',
    )
    # APP
    APP_NAME: str = 'hub-barbersystem'
    APP_NAME_FOR_CALLBACKS: str = ''
    API_VERSION: str = '/api/v1'

    # CORS
    BACKEND_CORS_ORIGINS: Union[List[str], List[AnyHttpUrl]] = []

    DEBUG: bool = False

    # Banco de dados com placeholder para o docker
    SQLALCHEMY_DATABASE_URI: str = (
        'postgresql+asyncpg://postgres:postgres@localhost:5477/barbersystem'
    )
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_TIMEOUT: int = 30

    # schema
    POSTGRES_SCHEMA: str = 'barbersystem'

    # Mercado Pago (preapproval_plan / assinaturas)
    # OBS: essas configs não devem impedir boot/migrations. A integração valida
    # a presença do token quando for realmente usada.
    MARKET_PAID_BASE_URL: str = 'https://api.mercadopago.com'
    MARKET_PAID_ACCESS_TOKEN: str = (
        'APP_USR-8460062634622735-011612-8d722fea2036739252f1f96b7015a251-1930594081'
    )

    # Auth (JWT)
    JWT_SECRET: str = 'algobarbersystem'
    JWT_ALGORITHM: str = 'HS256'
    JWT_EXPIRE_MINUTES: int = 36000

    # AWS S3 (Upload de imagens)
    AWS_REGION: str = 'us-east-1'
    AWS_S3_BUCKET_NAME: str = ''
    AWS_S3_PUBLIC_BASE_URL: str = ''
    AWS_S3_ENDPOINT_URL: str = ''
    AWS_S3_PUBLIC_READ: bool = True

    AWS_ACCESS_KEY_ID: str = ''
    AWS_SECRET_ACCESS_KEY: str = ''

    S3_UPLOAD_MAX_SIZE_MB: int = 5
    S3_ALLOWED_IMAGE_CONTENT_TYPES: str = 'image/jpeg,image/png,image/webp'

    @field_validator('BACKEND_CORS_ORIGINS', mode='before')
    def split_origins(cls, value: Any) -> Union[List[str], List[AnyHttpUrl]]:
        """
        Se for uma string separada por vírgulas
        (ex: "http://localhost:3000, http://localhost:4200"),
        converte em lista. Caso não seja, retorna no estado atual.
        """
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(',')]
        return value or []


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna instância única das configurações (singleton),
    aproveitando cache de functools.lru_cache.
    """
    return Settings()
