from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from src.main import app


@pytest.fixture(scope='session')
async def client() -> AsyncGenerator[TestClient, None]:
    async with AsyncClient(app=app, base_url='http://test') as client:
        yield client
