from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException
from src.interface.api.v1.dependencies.marketing import (
    get_marketing_controller,
    resolve_marketing_company_id,
)
from starlette import status

pytestmark = pytest.mark.unit


async def test_get_marketing_controller_wires_dependencies():
    fake_session = object()
    fake_template_repo = object()
    fake_inactive_repo = object()
    fake_evolution = object()
    fake_service = object()
    fake_use_case = object()
    fake_controller = object()

    with (
        patch(
            'src.interface.api.v1.dependencies.marketing.TemplateMarketingRepositoryPostgres',
            return_value=fake_template_repo,
        ) as tr,
        patch(
            'src.interface.api.v1.dependencies.marketing.MarketingInactiveRepositoryPostgres',
            return_value=fake_inactive_repo,
        ) as ir,
        patch(
            'src.interface.api.v1.dependencies.marketing.EvolutionApi',
            return_value=fake_evolution,
        ) as evo,
        patch(
            'src.interface.api.v1.dependencies.marketing.MarketingService',
            return_value=fake_service,
        ) as svc,
        patch(
            'src.interface.api.v1.dependencies.marketing.MarketingUseCase',
            return_value=fake_use_case,
        ) as uc,
        patch(
            'src.interface.api.v1.dependencies.marketing.MarketingController',
            return_value=fake_controller,
        ) as ctl,
    ):
        controller = await get_marketing_controller(session=fake_session)

    assert controller is fake_controller
    tr.assert_called_once_with(fake_session)
    ir.assert_called_once_with(fake_session)
    evo.assert_called_once_with()
    svc.assert_called_once_with(fake_template_repo, fake_evolution, fake_inactive_repo)
    uc.assert_called_once_with(fake_service)
    ctl.assert_called_once_with(fake_use_case)


async def test_resolve_marketing_company_id_prefers_token_state():
    cid = uuid4()
    req = MagicMock()
    req.state.company_id = cid
    other = uuid4()
    assert await resolve_marketing_company_id(req, other, None) == cid


async def test_resolve_marketing_company_id_from_query():
    cid = uuid4()
    req = MagicMock()

    class _State:
        pass

    req.state = _State()
    assert await resolve_marketing_company_id(req, cid, None) == cid


async def test_resolve_marketing_company_id_from_header():
    cid = uuid4()
    req = MagicMock()

    class _State:
        pass

    req.state = _State()
    assert await resolve_marketing_company_id(req, None, cid) == cid


async def test_resolve_marketing_company_id_raises_without_company():
    req = MagicMock()

    class _State:
        pass

    req.state = _State()
    with pytest.raises(HTTPException) as exc:
        await resolve_marketing_company_id(req, None, None)
    assert exc.value.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
