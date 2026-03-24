from src.infrastructure.external_apis.api_base_client import ApiBaseClient
from src.core.config.settings import get_settings


settings = get_settings()


class EvolutionApi(ApiBaseClient):
    def __init__(self) -> None:
        super().__init__(
            name='Evolution API',
            base_url=settings.EVOLUTION_API_BASE_URL,
            default_headers={
                'Authentication-API-Key': settings.AUTHENTICATION_API_KEY,
            },
        )
