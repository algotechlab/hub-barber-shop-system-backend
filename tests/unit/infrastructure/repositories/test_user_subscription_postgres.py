from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.subscription_plan import SubscriptionPlanProductLineOutDTO
from src.domain.dtos.user_subscription import (
    UserSubscriptionCreateDTO,
    UserSubscriptionOutDTO,
    UserSubscriptionWithPlanAndClientOutDTO,
    UserSubscriptionWithPlanOutDTO,
)
from src.infrastructure.database.models.commom.payment_method import PaymentMethod
from src.infrastructure.database.models.commom.user_subscription_status import (
    UserSubscriptionStatus,
)
from src.infrastructure.repositories.user_subscription_postgres import (
    UserSubscriptionRepositoryPostgres,
    _status_for_create,
)


@pytest.mark.unit
def test_status_for_create_branches():
    assert (
        _status_for_create('PENDING_PAYMENT') == UserSubscriptionStatus.pending_payment
    )
    assert _status_for_create('ACTIVE') == UserSubscriptionStatus.active


@pytest.mark.unit
class TestUserSubscriptionRepositoryPostgres:
    @pytest.fixture
    def mock_session(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repo(self, mock_session):
        return UserSubscriptionRepositoryPostgres(session=mock_session)

    async def test_service_ids_by_plan_empty_and_populated(self, repo, mock_session):
        assert await repo._service_ids_by_plan(()) == {}
        pid, sid = uuid4(), uuid4()
        mock_r = MagicMock()
        mock_r.all.return_value = [(pid, sid)]
        mock_session.execute = AsyncMock(return_value=mock_r)
        got = await repo._service_ids_by_plan([pid])
        assert got == {pid: [sid]}

    async def test_product_lines_by_plan_empty_and_populated(self, repo, mock_session):
        assert await repo._product_lines_by_plan(()) == {}
        pid, pr_id = uuid4(), uuid4()
        mock_r = MagicMock()
        mock_r.all.return_value = [(pid, pr_id, 2)]
        mock_session.execute = AsyncMock(return_value=mock_r)
        got = await repo._product_lines_by_plan([pid])
        assert len(got[pid]) == 1
        assert got[pid][0] == SubscriptionPlanProductLineOutDTO(
            product_id=pr_id, quantity=2
        )

    def test_to_out_non_enum_status_string_path(self, repo):
        row = MagicMock()
        row.id = uuid4()
        row.user_id = uuid4()
        row.subscription_plan_id = uuid4()
        row.company_id = uuid4()
        row.status = 'ACTIVE'
        now = datetime.now(timezone.utc)
        row.started_at = now
        row.ended_at = None
        row.external_subscription_id = None
        row.payment_at = None
        row.payment_method = None
        row.created_at = now
        row.updated_at = now
        row.is_deleted = False
        o = UserSubscriptionRepositoryPostgres._to_out(row)
        assert o.status == 'ACTIVE'

    def test_payment_method_to_str_variants(self, repo):
        r = MagicMock()
        r.payment_method = None
        assert UserSubscriptionRepositoryPostgres._payment_method_to_str(r) is None
        r.payment_method = PaymentMethod.debit_card
        assert (
            UserSubscriptionRepositoryPostgres._payment_method_to_str(r) == 'DEBIT_CARD'
        )
        r.payment_method = 'CREDIT_CARD'
        assert (
            UserSubscriptionRepositoryPostgres._payment_method_to_str(r)
            == 'CREDIT_CARD'
        )
        r.payment_method = object()
        assert UserSubscriptionRepositoryPostgres._payment_method_to_str(r) == str(
            r.payment_method
        )

    def test_to_out_enum_status(self, repo):
        row = MagicMock()
        row.id = uuid4()
        row.user_id = uuid4()
        row.subscription_plan_id = uuid4()
        row.company_id = uuid4()
        row.status = UserSubscriptionStatus.active
        now = datetime.now(timezone.utc)
        row.started_at = now
        row.ended_at = None
        row.external_subscription_id = None
        row.payment_at = None
        row.payment_method = None
        row.created_at = now
        row.updated_at = now
        row.is_deleted = False
        o = UserSubscriptionRepositoryPostgres._to_out(row)
        assert o.status == 'ACTIVE'

    async def test_get_by_id_found_and_none(self, repo, mock_session):
        sub_id, cid = uuid4(), uuid4()
        row = MagicMock()
        row.id = sub_id
        row.user_id = uuid4()
        row.subscription_plan_id = uuid4()
        row.company_id = cid
        row.status = UserSubscriptionStatus.pending_payment
        now = datetime.now(timezone.utc)
        row.started_at = now
        row.ended_at = None
        row.external_subscription_id = None
        row.payment_at = None
        row.payment_method = None
        row.created_at = now
        row.updated_at = now
        row.is_deleted = False
        mock_r = MagicMock()
        mock_r.scalar_one_or_none.return_value = row
        mock_session.execute = AsyncMock(return_value=mock_r)
        o = await repo.get_by_id(sub_id, cid)
        assert o is not None
        assert o.status == 'PENDING_PAYMENT'

        mock_r2 = MagicMock()
        mock_r2.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_r2)
        assert await repo.get_by_id(sub_id, cid) is None

    async def test_get_by_id_rollback(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('e'))
        mock_session.rollback = AsyncMock()
        with pytest.raises(DatabaseException, match='e'):
            await repo.get_by_id(uuid4(), uuid4())
        mock_session.rollback.assert_awaited_once()

    async def test_has_active_for_plan(self, repo, mock_session):
        mock_r = MagicMock()
        mock_r.scalar_one_or_none.return_value = uuid4()
        mock_session.execute = AsyncMock(return_value=mock_r)
        assert await repo.has_active_for_plan(uuid4(), uuid4(), uuid4()) is True

    async def test_has_active_for_plan_rollback(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('e'))
        mock_session.rollback = AsyncMock()
        with pytest.raises(DatabaseException, match='e'):
            await repo.has_active_for_plan(uuid4(), uuid4(), uuid4())
        mock_session.rollback.assert_awaited_once()

    async def test_list_by_user(self, repo, mock_session):
        us = MagicMock()
        us.id = uuid4()
        us.user_id = uuid4()
        us.subscription_plan_id = uuid4()
        us.company_id = uuid4()
        us.status = UserSubscriptionStatus.active
        now = datetime.now(timezone.utc)
        us.started_at = now
        us.ended_at = None
        us.external_subscription_id = None
        us.payment_at = None
        us.payment_method = None
        us.created_at = now
        us.updated_at = now
        us.is_deleted = False

        row_tuple = (us, 'Plano A', Decimal('10'), 'Desc', 2)
        mock_r = MagicMock()
        mock_r.all.return_value = [row_tuple]
        mock_session.execute = AsyncMock(return_value=mock_r)
        ps = uuid4()
        with patch.object(
            repo,
            '_service_ids_by_plan',
            AsyncMock(return_value={us.subscription_plan_id: [ps]}),
        ):
            with patch.object(
                repo,
                '_product_lines_by_plan',
                AsyncMock(return_value={us.subscription_plan_id: []}),
            ):
                r = await repo.list_by_user(PaginationParamsDTO(), uuid4(), us.user_id)
        assert len(r) == 1
        assert isinstance(r[0], UserSubscriptionWithPlanOutDTO)
        assert r[0].plan_name == 'Plano A'
        assert r[0].service_ids == [ps]

    async def test_list_by_user_rollback(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('e'))
        mock_session.rollback = AsyncMock()
        with pytest.raises(DatabaseException, match='e'):
            await repo.list_by_user(PaginationParamsDTO(), uuid4(), uuid4())
        mock_session.rollback.assert_awaited_once()

    async def test_has_pending_for_plan(self, repo, mock_session):
        mock_r = MagicMock()
        mock_r.scalar_one_or_none.return_value = uuid4()
        mock_session.execute = AsyncMock(return_value=mock_r)
        assert await repo.has_pending_for_plan(uuid4(), uuid4(), uuid4()) is True

    async def test_has_pending_for_plan_rollback(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('e'))
        mock_session.rollback = AsyncMock()
        with pytest.raises(DatabaseException, match='e'):
            await repo.has_pending_for_plan(uuid4(), uuid4(), uuid4())
        mock_session.rollback.assert_awaited_once()

    async def test_list_pending_by_company(self, repo, mock_session):
        us = MagicMock()
        us.id = uuid4()
        us.user_id = uuid4()
        us.subscription_plan_id = uuid4()
        us.company_id = uuid4()
        us.status = UserSubscriptionStatus.pending_payment
        now = datetime.now(timezone.utc)
        us.started_at = now
        us.ended_at = None
        us.external_subscription_id = None
        us.payment_at = None
        us.payment_method = None
        us.created_at = now
        us.updated_at = now
        us.is_deleted = False
        row_tuple = (us, 'Plano P', Decimal('20'), None, 1, 'Cliente X')
        mock_r = MagicMock()
        mock_r.all.return_value = [row_tuple]
        mock_session.execute = AsyncMock(return_value=mock_r)
        ps = uuid4()
        with patch.object(
            repo,
            '_service_ids_by_plan',
            AsyncMock(return_value={us.subscription_plan_id: [ps]}),
        ):
            with patch.object(
                repo,
                '_product_lines_by_plan',
                AsyncMock(return_value={us.subscription_plan_id: []}),
            ):
                r = await repo.list_pending_by_company(
                    PaginationParamsDTO(), us.company_id
                )
        assert len(r) == 1
        assert isinstance(r[0], UserSubscriptionWithPlanAndClientOutDTO)
        assert r[0].plan_name == 'Plano P'
        assert r[0].status == 'PENDING_PAYMENT'
        assert r[0].client_name == 'Cliente X'

    async def test_list_pending_by_company_with_client_name_filter(
        self, repo, mock_session
    ):
        us = MagicMock()
        us.id = uuid4()
        us.user_id = uuid4()
        us.subscription_plan_id = uuid4()
        us.company_id = uuid4()
        us.status = UserSubscriptionStatus.pending_payment
        now = datetime.now(timezone.utc)
        us.started_at = now
        us.ended_at = None
        us.external_subscription_id = None
        us.payment_at = None
        us.payment_method = None
        us.created_at = now
        us.updated_at = now
        us.is_deleted = False
        row_tuple = (us, 'P', Decimal('1'), None, 1, 'João')
        mock_r = MagicMock()
        mock_r.all.return_value = [row_tuple]
        mock_session.execute = AsyncMock(return_value=mock_r)
        with patch.object(
            repo,
            '_service_ids_by_plan',
            AsyncMock(return_value={us.subscription_plan_id: [uuid4()]}),
        ):
            with patch.object(
                repo,
                '_product_lines_by_plan',
                AsyncMock(return_value={us.subscription_plan_id: []}),
            ):
                r = await repo.list_pending_by_company(
                    PaginationParamsDTO(), us.company_id, client_name='jo'
                )
        assert len(r) == 1
        assert r[0].client_name == 'João'

    async def test_list_pending_by_company_rollback(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('e'))
        mock_session.rollback = AsyncMock()
        with pytest.raises(DatabaseException, match='e'):
            await repo.list_pending_by_company(PaginationParamsDTO(), uuid4())
        mock_session.rollback.assert_awaited_once()

    async def test_activate_pending_success_and_none(self, repo, mock_session):
        sid, cid = uuid4(), uuid4()
        now = datetime.now(timezone.utc)
        row = MagicMock()
        row.id = sid
        row.user_id = uuid4()
        row.subscription_plan_id = uuid4()
        row.company_id = cid
        row.status = UserSubscriptionStatus.active
        row.started_at = now
        row.ended_at = None
        row.external_subscription_id = 'ext'
        row.payment_at = now
        row.payment_method = None
        row.created_at = now
        row.updated_at = now
        row.is_deleted = False
        mock_r = MagicMock()
        mock_r.scalar_one_or_none.return_value = row
        mock_session.execute = AsyncMock(return_value=mock_r)
        mock_session.commit = AsyncMock()
        o = await repo.activate_pending(
            sid, cid, external_subscription_id='ext', payment_method='PIX'
        )
        assert o is not None
        assert o.status == 'ACTIVE'
        mock_session.commit.assert_awaited_once()

        mock_r2 = MagicMock()
        mock_r2.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_r2)
        mock_session.commit = AsyncMock()
        assert await repo.activate_pending(sid, cid, payment_method='PIX') is None

    async def test_activate_pending_without_external_id(self, repo, mock_session):
        sid, cid = uuid4(), uuid4()
        now = datetime.now(timezone.utc)
        row = MagicMock()
        row.id = sid
        row.user_id = uuid4()
        row.subscription_plan_id = uuid4()
        row.company_id = cid
        row.status = UserSubscriptionStatus.active
        row.started_at = now
        row.ended_at = None
        row.external_subscription_id = None
        row.payment_at = now
        row.payment_method = None
        row.created_at = now
        row.updated_at = now
        row.is_deleted = False
        mock_r = MagicMock()
        mock_r.scalar_one_or_none.return_value = row
        mock_session.execute = AsyncMock(return_value=mock_r)
        mock_session.commit = AsyncMock()
        o = await repo.activate_pending(
            sid, cid, external_subscription_id=None, payment_method='CREDIT_CARD'
        )
        assert o is not None

    async def test_activate_pending_rollback(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('e'))
        mock_session.rollback = AsyncMock()
        with pytest.raises(DatabaseException, match='e'):
            await repo.activate_pending(uuid4(), uuid4(), payment_method='MONEY')
        mock_session.rollback.assert_awaited_once()

    async def test_create_rollback_on_error(self, repo, mock_session):
        mock_session.add = MagicMock(side_effect=ValueError('fail'))
        mock_session.rollback = AsyncMock()
        dto = UserSubscriptionCreateDTO(
            user_id=uuid4(), company_id=uuid4(), subscription_plan_id=uuid4()
        )
        with pytest.raises(DatabaseException, match='fail'):
            await repo.create(dto)
        mock_session.rollback.assert_awaited_once()

    async def test_create_rollback_when_commit_fails(self, repo, mock_session):
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock(side_effect=RuntimeError('commit err'))
        mock_session.rollback = AsyncMock()
        dto = UserSubscriptionCreateDTO(
            user_id=uuid4(), company_id=uuid4(), subscription_plan_id=uuid4()
        )
        with pytest.raises(DatabaseException, match='commit err'):
            await repo.create(dto)
        mock_session.rollback.assert_awaited_once()

    async def test_create_success_commits_refreshes_and_returns(
        self, repo, mock_session
    ):
        uid, cid, pid = uuid4(), uuid4(), uuid4()
        dto = UserSubscriptionCreateDTO(
            user_id=uid, company_id=cid, subscription_plan_id=pid
        )
        now = datetime.now(timezone.utc)
        row = MagicMock()
        row.id = uuid4()
        row.user_id = uid
        row.subscription_plan_id = pid
        row.company_id = cid
        row.status = UserSubscriptionStatus.active
        row.started_at = now
        row.ended_at = None
        row.external_subscription_id = None
        row.created_at = now
        row.updated_at = now
        row.is_deleted = False
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        expected = UserSubscriptionOutDTO(
            id=row.id,
            user_id=uid,
            subscription_plan_id=pid,
            company_id=cid,
            status='ACTIVE',
            started_at=row.started_at,
            ended_at=None,
            external_subscription_id=None,
            payment_at=None,
            payment_method=None,
            created_at=row.created_at,
            updated_at=row.updated_at,
            is_deleted=False,
        )
        with patch(
            'src.infrastructure.repositories.user_subscription_postgres.UserSubscriptionModel',
            return_value=row,
        ):
            with patch.object(
                UserSubscriptionRepositoryPostgres, '_to_out', return_value=expected
            ):
                r = await repo.create(dto)
        assert r == expected
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once_with(row)
