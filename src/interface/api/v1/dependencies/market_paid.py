from typing import Annotated

from fastapi import Depends

from src.domain.service.market_paid import MarketPaidService
from src.domain.use_case.market_paid import MarketPaidUseCase
from src.infrastructure.repositories.market_paid_api import MarketPaidRepositoryApi
from src.interface.api.v1.controller.market_paid import MarketPaidController
from src.interface.api.v1.dependencies.common.session import VerifiedSessionDep


async def get_market_paid_controller(
    session: VerifiedSessionDep,
) -> MarketPaidController:
    """
    Singleton para o controller de planos de assinatura (Mercado Pago).
    """
    market_paid_repository = MarketPaidRepositoryApi(session)
    market_paid_service = MarketPaidService(market_paid_repository)
    market_paid_use_case = MarketPaidUseCase(market_paid_service)
    return MarketPaidController(market_paid_use_case)


MarketPaidControllerDep = Annotated[
    MarketPaidController, Depends(get_market_paid_controller)
]
