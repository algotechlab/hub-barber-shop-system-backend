from __future__ import annotations

import json
from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from src.core.config.settings import get_settings
from src.infrastructure.external_apis.api_base_client import ApiBaseClient


class EvolutionApiNotConfiguredError(RuntimeError):
    """Evolution API URL ou chave ausente."""


class EvolutionApi(ApiBaseClient):
    """
    Cliente HTTP para Evolution API v2.
    Autenticação: header `apikey` (ver documentação oficial).
    """

    def __init__(self) -> None:
        self._settings = get_settings()
        base = (self._settings.EVOLUTION_API_BASE_URL or '').rstrip('/')
        super().__init__(
            name='Evolution API',
            base_url=base or 'http://127.0.0.1',
            timeout=30.0,
            default_headers={
                'Accept': 'application/json',
            },
        )

    def _api_key(self) -> str:
        key = self._settings.EVOLUTION_API_KEY or self._settings.AUTHENTICATION_API_KEY
        return (key or '').strip()

    def _auth_headers(self) -> dict[str, str]:
        return {'apikey': self._api_key()}

    def is_configured(self) -> bool:
        return bool(
            (self._settings.EVOLUTION_API_BASE_URL or '').strip() and self._api_key()
        )

    def _ensure_configured(self) -> None:
        if not self.is_configured():
            raise EvolutionApiNotConfiguredError(
                'Defina EVOLUTION_API_BASE_URL e \n'
                'EVOLUTION_API_KEY (ou AUTHENTICATION_API_KEY).\n'
            )

    @staticmethod
    def _safe_instance_path(instance: str) -> str:
        return quote(instance, safe='')

    async def get_connection_state_raw(self, instance: str) -> httpx.Response:
        self._ensure_configured()
        return await self.request({
            'method': 'GET',
            'url': f'/instance/connectionState/{self._safe_instance_path(instance)}',
            'headers': self._auth_headers(),
            'raise_for_status': False,
        })

    async def create_instance(
        self,
        instance: str,
        *,
        qrcode: bool = True,
        integration: str = 'WHATSAPP-BAILEYS',
    ) -> dict[str, Any]:
        """
        POST /instance/create — cria instância;
        403 se nome já existir (instância já criada).
        """
        self._ensure_configured()
        response = await self.request({
            'method': 'POST',
            'url': '/instance/create',
            'json': {
                'instanceName': instance,
                'integration': integration,
                'qrcode': qrcode,
            },
            'headers': self._auth_headers(),
            'raise_for_status': False,
        })
        if response.status_code in (HTTPStatus.OK, HTTPStatus.CREATED):
            return response.json()
        if response.status_code == HTTPStatus.FORBIDDEN:
            try:
                return response.json()
            except json.JSONDecodeError:
                return {}
        response.raise_for_status()
        return response.json()

    async def get_connect_raw(self, instance: str) -> httpx.Response:
        self._ensure_configured()
        return await self.request({
            'method': 'GET',
            'url': f'/instance/connect/{self._safe_instance_path(instance)}',
            'headers': self._auth_headers(),
            'raise_for_status': False,
        })

    async def send_text(
        self,
        instance: str,
        *,
        number: str,
        text: str,
    ) -> dict[str, Any]:
        self._ensure_configured()
        response = await self.request({
            'method': 'POST',
            'url': f'/message/sendText/{self._safe_instance_path(instance)}',
            'json': {'number': number, 'text': text},
            'headers': self._auth_headers(),
        })
        return response.json()
