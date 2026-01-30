from src.core.config.settings import get_settings
from src.domain.dtos.market_paid import PreapprovalPlanSearchResponseDTO
from src.infrastructure.external_apis.api_base_client import ApiBaseClient

settings = get_settings()


class MarketPaidApi(ApiBaseClient):
    """Cliente para a API Mercado Pago (planos de assinatura / preapproval_plan)."""

    def __init__(self) -> None:
        super().__init__(
            name='Mercado Pago',
            base_url=settings.MARKET_PAID_BASE_URL,
            default_headers={
                'Authorization': f'Bearer {settings.MARKET_PAID_ACCESS_TOKEN}',
                'Content-Type': 'application/json',
            },
        )

    async def search_preapproval_plans(
        self,
        offset: int = 0,
        limit: int = 10,
    ) -> PreapprovalPlanSearchResponseDTO:
        """
        Busca planos de assinatura (preapproval_plan) no Mercado Pago.
        GET /preapproval_plan/search
        """
        url = f'/preapproval_plan/search?offset={offset}&limit={limit}'
        response = await self.request({
            'method': 'GET',
            'url': url,
        })
        data = response.json()
        return PreapprovalPlanSearchResponseDTO.model_validate(data)
