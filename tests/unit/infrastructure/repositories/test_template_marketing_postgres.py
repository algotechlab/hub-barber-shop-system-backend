from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.marketing import TemplateMarketingRecordDTO
from src.infrastructure.repositories.template_marketing_postgres import (
    TemplateMarketingRepositoryPostgres,
)


@pytest.mark.unit
class TestTemplateMarketingRepositoryPostgres:
    @pytest.fixture
    def mock_session(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repo(self, mock_session):
        return TemplateMarketingRepositoryPostgres(mock_session)

    async def test_get_active_for_company_none(self, repo, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        assert await repo.get_active_for_company(uuid4()) is None

    async def test_get_active_for_company_success(self, repo, mock_session):
        row = MagicMock()
        row.id = uuid4()
        row.company_id = uuid4()
        row.name = 'n'
        row.description = 'd'
        row.context_template = {'template': 't'}
        row.is_active = True
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = row
        mock_session.execute = AsyncMock(return_value=mock_result)
        out = await repo.get_active_for_company(row.company_id)
        assert out is not None
        assert out.context_template == {'template': 't'}

    async def test_get_active_for_company_raises(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=RuntimeError('x'))
        with pytest.raises(DatabaseException, match='x'):
            await repo.get_active_for_company(uuid4())

    async def test_get_latest_for_company_none(self, repo, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        assert await repo.get_latest_for_company(uuid4()) is None

    async def test_get_latest_for_company_success(self, repo, mock_session):
        cid = uuid4()
        row = MagicMock()
        row.id = uuid4()
        row.company_id = cid
        row.name = 'n'
        row.description = 'd'
        row.context_template = {'template': 't'}
        row.is_active = True
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = row
        mock_session.execute = AsyncMock(return_value=mock_result)
        out = await repo.get_latest_for_company(cid)
        assert out is not None
        assert out.context_template == {'template': 't'}

    async def test_get_latest_for_company_raises(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=RuntimeError('y'))
        with pytest.raises(DatabaseException, match='y'):
            await repo.get_latest_for_company(uuid4())

    async def test_upsert_creates_new(self, repo, mock_session):
        fake_row = MagicMock()
        fake_row.id = uuid4()
        fake_row.company_id = uuid4()
        fake_row.name = 'Mensagem marketing'
        fake_row.description = 'Template de mensagem para campanhas WhatsApp'
        fake_row.context_template = {'template': 'hello'}
        fake_row.is_active = True

        with (
            patch.object(
                repo,
                'get_latest_for_company',
                new_callable=AsyncMock,
                return_value=None,
            ),
            patch(
                'src.infrastructure.repositories.template_marketing_postgres.TemplateMarketingModel',
                return_value=fake_row,
            ) as model_cls,
        ):
            mock_session.refresh = AsyncMock()
            out = await repo.upsert_default_template(uuid4(), 'hello')

        model_cls.assert_called_once()
        mock_session.add.assert_called_once()
        assert out.context_template == {'template': 'hello'}

    async def test_upsert_updates_existing(self, repo, mock_session):
        existing_id = uuid4()
        company_id = uuid4()
        existing = TemplateMarketingRecordDTO(
            id=existing_id,
            company_id=company_id,
            name='old',
            description='old',
            context_template={},
            is_active=True,
        )
        db_row = MagicMock()
        db_row.id = existing_id
        db_row.company_id = company_id
        db_row.name = 'Mensagem marketing'
        db_row.description = 'Template de mensagem para campanhas WhatsApp'
        db_row.context_template = {'template': 'new'}
        db_row.is_active = True

        mock_exec = MagicMock()
        mock_exec.scalar_one.return_value = db_row

        with patch.object(
            repo,
            'get_latest_for_company',
            new_callable=AsyncMock,
            return_value=existing,
        ):
            mock_session.execute = AsyncMock(return_value=mock_exec)
            await repo.upsert_default_template(company_id, 'new')

        assert db_row.context_template == {'template': 'new'}
        mock_session.commit.assert_awaited()

    async def test_upsert_raises(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=RuntimeError('z'))
        with pytest.raises(DatabaseException, match='z'):
            await repo.upsert_default_template(uuid4(), 'x')
