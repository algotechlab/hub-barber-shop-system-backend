from __future__ import annotations

from http import HTTPStatus
from typing import Any
from uuid import UUID

import httpx

from src.core.exceptions.custom import DomainException
from src.domain.dtos.marketing import (
    InactiveClientsPayloadDTO,
    MessageTemplateDTO,
    WhatsappConnectionDTO,
)
from src.domain.repositories.marketing_inactive import MarketingInactiveRepository
from src.domain.repositories.template_marketing import TemplateMarketingRepository
from src.infrastructure.external_apis.evolution_api import (
    EvolutionApi,
    EvolutionApiNotConfiguredError,
)


def _template_text_from_context(context: dict[str, Any]) -> str:
    if not context:
        return ''
    return (
        str(context.get('template', ''))
        or str(context.get('body', ''))
        or str(context.get('message', ''))
    )


def _map_evolution_state(raw: str) -> str:
    if not raw:
        return 'unknown'
    s = raw.lower()
    if s == 'open':
        return 'open'
    if s in ('connecting', 'qr', 'pairing'):
        return 'connecting'
    if s == 'connected':
        return 'open'
    return 'close'


def _extract_qr_base64(data: dict[str, object]) -> str | None:
    qrcode = data.get('qrcode')
    if isinstance(qrcode, dict):
        b64 = qrcode.get('base64') or qrcode.get('code')
        if isinstance(b64, str) and b64.strip():
            return b64.strip()
    for key in ('base64', 'code'):
        v = data.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def _whatsapp_state_from_mapping(
    mapped: str, raw_state: str, qr_b64: str | None
) -> str:
    if mapped == 'connecting':
        state_out = 'connecting'
    elif raw_state:
        state_out = mapped
    else:
        state_out = 'close'

    if qr_b64 and state_out in ('close', 'unknown'):
        return 'connecting'
    return state_out


def _evolution_http_message(exc: httpx.HTTPStatusError) -> str:
    try:
        data = exc.response.json()
        if isinstance(data, dict):
            inner = data.get('response')
            if isinstance(inner, dict):
                messages = inner.get('message')
                if isinstance(messages, list) and messages:
                    return str(messages[0])
                if isinstance(messages, str):
                    return messages
            err = data.get('error')
            if isinstance(err, str):
                return err
        return exc.response.text or str(exc)
    except Exception:
        return str(exc)


class MarketingService:
    def __init__(
        self,
        template_repo: TemplateMarketingRepository,
        evolution: EvolutionApi,
        inactive_clients: MarketingInactiveRepository,
    ):
        self._templates = template_repo
        self._evolution = evolution
        self._inactive_clients = inactive_clients

    @staticmethod
    def instance_name_for_company(company_id: UUID) -> str:
        return f'barber-{company_id}'

    async def get_message_template(self, company_id: UUID) -> MessageTemplateDTO:
        row = await self._templates.get_active_for_company(company_id)
        if row is None:
            return MessageTemplateDTO(template='')
        text = _template_text_from_context(row.context_template)
        return MessageTemplateDTO(template=text)

    async def save_message_template(
        self, company_id: UUID, text: str
    ) -> MessageTemplateDTO:
        await self._templates.upsert_default_template(company_id, text)
        return MessageTemplateDTO(template=text)

    async def _connection_state_json(self, instance: str) -> dict[str, Any]:
        res = await self._evolution.get_connection_state_raw(instance)
        if res.status_code == HTTPStatus.NOT_FOUND:
            await self._evolution.create_instance(instance)
            res = await self._evolution.get_connection_state_raw(instance)
        if res.status_code != HTTPStatus.OK:
            res.raise_for_status()
        return res.json()

    async def _connect_qr_json(self, instance: str) -> dict[str, Any]:
        qr_res = await self._evolution.get_connect_raw(instance)
        if qr_res.status_code != HTTPStatus.OK:
            qr_res.raise_for_status()
        return qr_res.json()

    async def get_whatsapp_connection(self, company_id: UUID) -> WhatsappConnectionDTO:
        if not self._evolution.is_configured():
            return WhatsappConnectionDTO(state='unknown', qr_base64=None)

        instance = self.instance_name_for_company(company_id)
        try:
            data = await self._connection_state_json(instance)
        except EvolutionApiNotConfiguredError:
            return WhatsappConnectionDTO(state='unknown', qr_base64=None)
        except httpx.HTTPStatusError as exc:
            raise DomainException(_evolution_http_message(exc)) from exc
        except httpx.HTTPError as exc:
            raise DomainException(f'Evolution API indisponível: {exc}') from exc

        inst = data.get('instance') if isinstance(data, dict) else None
        raw_state = ''
        if isinstance(inst, dict):
            raw_state = str(inst.get('state') or '')
        mapped = _map_evolution_state(raw_state)

        if mapped == 'open':
            return WhatsappConnectionDTO(state='open', qr_base64=None)

        try:
            qr_data = await self._connect_qr_json(instance)
        except httpx.HTTPStatusError as exc:
            raise DomainException(_evolution_http_message(exc)) from exc
        except httpx.HTTPError as exc:
            raise DomainException(f'Evolution API indisponível: {exc}') from exc

        qr_b64: str | None = None
        if isinstance(qr_data, dict):
            qr_b64 = _extract_qr_base64(qr_data)

        state_out = _whatsapp_state_from_mapping(mapped, raw_state, qr_b64)

        return WhatsappConnectionDTO(
            state=state_out,
            qr_base64=qr_b64,
        )

    async def get_inactive_clients(
        self,
        company_id: UUID,
        *,
        email: str | None = None,
        min_days: int | None = None,
        max_days: int | None = None,
        lookback_years: int = 2,
        schedules_limit: int = 3000,
    ) -> InactiveClientsPayloadDTO:
        return await self._inactive_clients.fetch_inactive_clients(
            company_id,
            email=email,
            min_days=min_days,
            max_days=max_days,
            lookback_years=lookback_years,
            schedules_limit=schedules_limit,
        )

    async def send_template_message(
        self, company_id: UUID, number: str, override_text: str | None = None
    ) -> None:
        text = (override_text or '').strip()
        if not text:
            dto = await self.get_message_template(company_id)
            text = dto.template.strip()
        if not text:
            raise DomainException('Nenhum template de mensagem configurado.')

        if not self._evolution.is_configured():
            raise DomainException('Evolution API não configurada no servidor.')

        instance = self.instance_name_for_company(company_id)
        try:
            await self._evolution.send_text(instance, number=number.strip(), text=text)
        except EvolutionApiNotConfiguredError as exc:
            raise DomainException(str(exc)) from exc
        except httpx.HTTPStatusError as exc:
            raise DomainException(_evolution_http_message(exc)) from exc
        except httpx.HTTPError as exc:
            raise DomainException(f'Evolution API indisponível: {exc}') from exc
