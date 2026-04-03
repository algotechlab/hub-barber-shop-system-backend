from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.marketing import (
    InactiveClientsPayloadDTO,
    InactiveClientUserDTO,
    MessageTemplateDTO,
    WhatsappConnectionDTO,
)
from src.domain.dtos.schedule import ScheduleOutDTO
from src.interface.api.v1.controller.marketing import MarketingController
from src.interface.api.v1.schema.marketing import MessageTemplatePutSchema


@pytest.mark.unit
class TestMarketingController:
    @pytest.fixture
    def mock_use_case(self):
        return AsyncMock()

    @pytest.fixture
    def controller(self, mock_use_case):
        return MarketingController(mock_use_case)

    async def test_get_message_template(self, controller, mock_use_case):
        mock_use_case.get_message_template.return_value = MessageTemplateDTO(
            template='hello'
        )
        cid = uuid4()
        out = await controller.get_message_template(cid)
        assert out.template == 'hello'

    async def test_save_message_template(self, controller, mock_use_case):
        mock_use_case.save_message_template.return_value = MessageTemplateDTO(
            template='saved'
        )
        cid = uuid4()
        body = MessageTemplatePutSchema(template='saved')
        out = await controller.save_message_template(cid, body)
        assert out.template == 'saved'

    async def test_get_whatsapp_connection(self, controller, mock_use_case):
        mock_use_case.get_whatsapp_connection.return_value = WhatsappConnectionDTO(
            state='open',
            qr_base64=None,
        )
        out = await controller.get_whatsapp_connection(uuid4())
        assert out.state == 'open'
        assert out.status == 'open'

    async def test_send_message(self, controller, mock_use_case):
        cid = uuid4()
        await controller.send_message(cid, '5511', None)
        mock_use_case.send_template_message.assert_awaited_once_with(
            cid, '5511', override_text=None
        )

    async def test_get_inactive_clients(self, controller, mock_use_case):
        now = datetime.now(timezone.utc)
        uid = uuid4()
        cid = uuid4()
        user_dto = InactiveClientUserDTO(
            id=uid,
            name='N',
            email='e@e.com',
            phone='5511',
            company_id=cid,
            is_active=True,
            last_visit_at=None,
            days_since_last_visit=10,
        )
        sched = ScheduleOutDTO(
            id=uuid4(),
            user_id=uid,
            service_id=[uuid4()],
            employee_id=uuid4(),
            company_id=cid,
            time_register=now,
            is_confirmed=True,
            is_canceled=False,
            created_at=now,
            updated_at=now,
            is_deleted=False,
        )
        mock_use_case.get_inactive_clients.return_value = InactiveClientsPayloadDTO(
            users=[user_dto],
            schedules=[sched],
        )
        out = await controller.get_inactive_clients(
            cid,
            email=None,
            min_days=None,
            max_days=None,
            lookback_years=2,
            schedules_limit=3000,
        )
        assert len(out.users) == 1
        assert len(out.schedules) == 1
