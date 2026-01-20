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
