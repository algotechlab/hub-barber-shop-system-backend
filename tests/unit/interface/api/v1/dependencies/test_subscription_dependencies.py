from unittest.mock import AsyncMock

import pytest
from src.interface.api.v1.controller.subscription_plan import SubscriptionPlanController
from src.interface.api.v1.controller.user_subscription import UserSubscriptionController
from src.interface.api.v1.dependencies.subscription_plan import (
    get_subscription_plan_controller,
)
from src.interface.api.v1.dependencies.user_subscription import (
    get_user_subscription_controller,
)


@pytest.mark.asyncio
async def test_get_subscription_plan_controller_builds():
    session = AsyncMock()
    c = await get_subscription_plan_controller(session)
    assert isinstance(c, SubscriptionPlanController)


@pytest.mark.asyncio
async def test_get_user_subscription_controller_builds():
    session = AsyncMock()
    c = await get_user_subscription_controller(session)
    assert isinstance(c, UserSubscriptionController)
