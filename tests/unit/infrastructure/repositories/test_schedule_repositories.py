from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.schedule import (
    CloseScheduleDTO,
    ScheduleCreateDTO,
    ScheduleFinanceOutDTO,
    ScheduleOutDTO,
    ScheduleUpdateDTO,
    SlotsInDTO,
)
from src.infrastructure.database.models.commom.payment_method import PaymentMethod
from src.infrastructure.database.models.commom.payment_status import PaymentStatus
from src.infrastructure.repositories.schedule_postgres import ScheduleRepositoryPostgres


@pytest.mark.unit
class TestScheduleRepositoryPostgres:
    @pytest.fixture
    def mock_session(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repo(self, mock_session):
        return ScheduleRepositoryPostgres(session=mock_session)

    async def test_create_schedule_success(self, repo, mock_session):
        dto = ScheduleCreateDTO(
            user_id=uuid4(),
            service_id=[uuid4()],
            product_id=uuid4(),
            employee_id=uuid4(),
            company_id=uuid4(),
            time_register=datetime(2026, 2, 14, 20, 6, 18),
            time_start=None,
            time_end=None,
            status=True,
            is_canceled=False,
        )
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        mock_orm = MagicMock()

        expected = MagicMock(spec=ScheduleOutDTO)
        with (
            patch(
                'src.infrastructure.repositories.schedule_postgres.Schedule',
                return_value=mock_orm,
            ),
            patch.object(ScheduleOutDTO, 'model_validate', return_value=expected) as mv,
        ):
            result = await repo.create_schedule(dto)

        mock_session.add.assert_called_once_with(mock_orm)
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once_with(mock_orm)
        mv.assert_called_once_with(mock_orm)
        assert result == expected

    async def test_create_schedule_rollback_on_error(self, repo, mock_session):
        mock_session.add = MagicMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()
        dto = ScheduleCreateDTO(
            user_id=uuid4(),
            service_id=[uuid4()],
            product_id=uuid4(),
            employee_id=uuid4(),
            company_id=uuid4(),
            time_register=datetime(2026, 2, 14, 20, 6, 18),
            time_start=None,
            time_end=None,
            status=True,
            is_canceled=False,
        )

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.create_schedule(dto)

        mock_session.rollback.assert_awaited_once()

    async def test_list_schedules_success(self, repo, mock_session):
        mock_orm_schedules = [MagicMock(), MagicMock()]
        mock_result = MagicMock()
        mock_result.all.return_value = [
            (
                mock_orm_schedules[0],
                'User 1',
                'Employee 1',
                'Service 1',
                'Product 1',
                30,
            ),
            (
                mock_orm_schedules[1],
                'User 2',
                'Employee 2',
                'Service 2',
                'Product 2',
                45,
            ),
        ]
        mock_session.execute = AsyncMock(return_value=mock_result)

        expected = [MagicMock(), MagicMock()]
        with patch.object(ScheduleOutDTO, 'model_validate', side_effect=expected) as mv:
            result = await repo.list_schedules(PaginationParamsDTO(), uuid4())

        assert result == expected
        assert mv.call_count == len(mock_orm_schedules)

    async def test_list_schedules_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.list_schedules(PaginationParamsDTO(), uuid4())

        mock_session.rollback.assert_awaited_once()

    async def test_list_schedules_success_with_employee_filter(
        self, repo, mock_session
    ):
        employee_id = uuid4()
        mock_orm_schedules = [MagicMock()]
        mock_result = MagicMock()
        mock_result.all.return_value = [
            (
                mock_orm_schedules[0],
                'User 1',
                'Employee 1',
                'Service 1',
                'Product 1',
                30,
            )
        ]
        mock_session.execute = AsyncMock(return_value=mock_result)

        expected = [MagicMock()]
        with patch.object(ScheduleOutDTO, 'model_validate', side_effect=expected):
            result = await repo.list_schedules(
                PaginationParamsDTO(), uuid4(), employee_id=employee_id
            )

        mock_session.execute.assert_awaited_once()
        assert result == expected

    async def test_list_schedules_success_with_user_filter(self, repo, mock_session):
        user_id = uuid4()
        mock_orm_schedules = [MagicMock()]
        mock_result = MagicMock()
        mock_result.all.return_value = [
            (
                mock_orm_schedules[0],
                'User 1',
                'Employee 1',
                'Service 1',
                'Product 1',
                30,
            )
        ]
        mock_session.execute = AsyncMock(return_value=mock_result)

        expected = [MagicMock()]
        with patch.object(ScheduleOutDTO, 'model_validate', side_effect=expected):
            result = await repo.list_schedules(
                PaginationParamsDTO(), uuid4(), user_id=user_id
            )

        mock_session.execute.assert_awaited_once()
        assert result == expected

    async def test_list_schedules_computes_duration_when_service_duration_missing(
        self, repo, mock_session
    ):
        schedule = MagicMock()
        schedule.time_start = datetime(2026, 2, 14, 10, 0, 0)
        schedule.time_end = datetime(2026, 2, 14, 10, 31, 0)
        schedule_out = MagicMock()
        mock_result = MagicMock()
        mock_result.all.return_value = [
            (schedule, 'User', 'Employee', 'Service', 'Product', None)
        ]
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch.object(ScheduleOutDTO, 'model_validate', return_value=schedule_out):
            result = await repo.list_schedules(PaginationParamsDTO(), uuid4())
        arrange_result = 31
        assert result[0].schedule_duration_minutes == arrange_result

    async def test_list_schedules_sets_duration_none_when_missing_or_invalid(
        self, repo, mock_session
    ):
        schedule_without_times = MagicMock()
        schedule_without_times.time_start = None
        schedule_without_times.time_end = None
        out_without_times = MagicMock()

        schedule_negative = MagicMock()
        schedule_negative.time_start = datetime(2026, 2, 14, 11, 0, 0)
        schedule_negative.time_end = datetime(2026, 2, 14, 10, 59, 0)
        out_negative = MagicMock()

        mock_result = MagicMock()
        mock_result.all.return_value = [
            (schedule_without_times, 'User', 'Employee', 'Service', 'Product', None),
            (schedule_negative, 'User', 'Employee', 'Service', 'Product', None),
        ]
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch.object(
            ScheduleOutDTO,
            'model_validate',
            side_effect=[out_without_times, out_negative],
        ):
            result = await repo.list_schedules(PaginationParamsDTO(), uuid4())

        assert result[0].schedule_duration_minutes is None
        assert result[1].schedule_duration_minutes is None

    async def test_get_schedule_by_user_id_success(self, repo):
        pagination = PaginationParamsDTO()
        company_id = uuid4()
        user_id = uuid4()
        expected = [MagicMock()]

        with patch.object(
            repo, 'list_schedules', AsyncMock(return_value=expected)
        ) as list_schedules:
            result = await repo.get_schedule_by_user_id(pagination, company_id, user_id)

        list_schedules.assert_awaited_once_with(
            pagination=pagination,
            company_id=company_id,
            employee_id=None,
            user_id=user_id,
        )
        assert result == expected

    async def test_get_schedule_by_user_id_rollback_on_error(self, repo, mock_session):
        mock_session.rollback = AsyncMock()
        pagination = PaginationParamsDTO()

        with patch.object(
            repo, 'list_schedules', AsyncMock(side_effect=ValueError('DB error'))
        ):
            with pytest.raises(DatabaseException, match='DB error'):
                await repo.get_schedule_by_user_id(pagination, uuid4(), uuid4())

        mock_session.rollback.assert_awaited_once()

    async def test_get_slots_success(self, repo, mock_session):
        booked_schedule = MagicMock()
        booked_schedule.time_start = datetime(2026, 2, 14, 9, 15, 0)
        booked_schedule.time_end = datetime(2026, 2, 14, 9, 45, 0)
        mock_scalar_result = MagicMock()
        mock_scalar_result.all.return_value = [booked_schedule]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalar_result
        mock_session.execute = AsyncMock(return_value=mock_result)

        slots = SlotsInDTO(
            company_id=uuid4(),
            employee_id=uuid4(),
            work_start=datetime(2026, 2, 14, 9, 0, 0),
            work_end=datetime(2026, 2, 14, 10, 0, 0),
            slot_minutes=30,
            target_date=None,
        )
        result = await repo.get_slots(slots)
        result_range = 2
        assert len(result) == result_range
        assert result[0].is_blocked is True
        assert result[1].is_blocked is True

    async def test_get_slots_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()
        slots = SlotsInDTO(
            company_id=uuid4(),
            employee_id=uuid4(),
            work_start=datetime(2026, 2, 14, 9, 0, 0),
            work_end=datetime(2026, 2, 14, 10, 0, 0),
            slot_minutes=30,
            target_date=None,
        )

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.get_slots(slots)

        mock_session.rollback.assert_awaited_once()

    async def test_get_slots_blocks_using_target_date(self, repo, mock_session):
        booked_schedule = MagicMock()
        booked_schedule.time_start = datetime(2026, 3, 3, 13, 0, 0)
        booked_schedule.time_end = datetime(2026, 3, 3, 13, 30, 0)
        mock_scalar_result = MagicMock()
        mock_scalar_result.all.return_value = [booked_schedule]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalar_result
        mock_session.execute = AsyncMock(return_value=mock_result)

        slots = SlotsInDTO(
            company_id=uuid4(),
            employee_id=uuid4(),
            work_start=datetime(2026, 3, 1, 13, 0, 0),
            work_end=datetime(2026, 3, 1, 14, 0, 0),
            slot_minutes=30,
            target_date=datetime(2026, 3, 3, 0, 0, 0).date(),
        )

        result = await repo.get_slots(slots)
        result_range = 2
        assert len(result) == result_range
        assert result[0].time_start == datetime(2026, 3, 3, 13, 0, 0)
        assert result[0].is_blocked is True
        assert result[0].is_available is False
        assert result[1].is_blocked is False

    async def test_get_schedule_returns_none_when_not_found(self, repo, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_schedule(uuid4(), uuid4())

        assert result is None

    async def test_get_schedule_success(self, repo, mock_session):
        mock_orm = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_orm
        mock_session.execute = AsyncMock(return_value=mock_result)

        expected = MagicMock()
        with patch.object(
            ScheduleOutDTO, 'model_validate', return_value=expected
        ) as mv:
            result = await repo.get_schedule(uuid4(), uuid4())

        mv.assert_called_once_with(mock_orm)
        assert result == expected

    async def test_get_schedule_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.get_schedule(uuid4(), uuid4())

        mock_session.rollback.assert_awaited_once()

    async def test_block_schedule_returns_none_when_not_found(self, repo, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.block_schedule(uuid4(), uuid4())

        assert result is None

    async def test_block_schedule_returns_true_when_found(self, repo, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock()
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.block_schedule(uuid4(), uuid4())

        assert result is True

    async def test_block_schedule_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.block_schedule(uuid4(), uuid4())

        mock_session.rollback.assert_awaited_once()

    async def test_update_schedule_returns_none_when_not_found(
        self, repo, mock_session
    ):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        result = await repo.update_schedule(
            uuid4(), ScheduleUpdateDTO(status=False), uuid4()
        )

        assert result is None
        mock_session.commit.assert_awaited_once()

    async def test_update_schedule_success(self, repo, mock_session):
        mock_updated = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_updated
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        expected = MagicMock()
        with patch.object(
            ScheduleOutDTO, 'model_validate', return_value=expected
        ) as mv:
            result = await repo.update_schedule(
                uuid4(), ScheduleUpdateDTO(status=False), uuid4()
            )

        mock_session.commit.assert_awaited_once()
        mv.assert_called_once_with(mock_updated)
        assert result == expected

    async def test_update_schedule_coerces_string_service_ids_from_dump(
        self, repo, mock_session
    ):
        """
        Cobre normalização quando
        model_dump traz UUIDs como string
        (ex.: round-trip JSON).
        """
        mock_updated = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_updated
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        schedule_dto = MagicMock()
        schedule_dto.model_dump.return_value = {
            'service_id': [
                '3fa85f64-5717-4562-b3fc-2c963f66afa6',
                'baf26222-1b35-452d-842e-668c2c33bd0e',
            ],
        }

        expected = MagicMock()
        with patch.object(ScheduleOutDTO, 'model_validate', return_value=expected):
            result = await repo.update_schedule(uuid4(), schedule_dto, uuid4())

        mock_session.commit.assert_awaited_once()
        schedule_dto.model_dump.assert_called_once_with(
            exclude_unset=True, exclude_none=True
        )
        assert result == expected

    async def test_update_schedule_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.update_schedule(
                uuid4(), ScheduleUpdateDTO(status=False), uuid4()
            )

        mock_session.rollback.assert_awaited_once()

    async def test_delete_schedule_returns_none_when_not_found(
        self, repo, mock_session
    ):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        result = await repo.delete_schedule(uuid4(), uuid4())

        assert result is None
        mock_session.commit.assert_awaited_once()

    async def test_delete_schedule_returns_true_when_found(self, repo, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock()
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        result = await repo.delete_schedule(uuid4(), uuid4())

        assert result is True
        mock_session.commit.assert_awaited_once()

    async def test_delete_schedule_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.delete_schedule(uuid4(), uuid4())

        mock_session.rollback.assert_awaited_once()

    async def test_list_schedule_history_success(self, repo, mock_session):
        schedule_orm_1 = MagicMock()
        schedule_orm_2 = MagicMock()
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [schedule_orm_1, schedule_orm_2]
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute = AsyncMock(return_value=mock_result)

        expected_1 = MagicMock()
        expected_2 = MagicMock()
        with patch.object(
            ScheduleOutDTO, 'model_validate', side_effect=[expected_1, expected_2]
        ) as mv:
            result = await repo.list_schedule_history(uuid4())
        range_result = 2
        assert result == [expected_1, expected_2]

        assert mv.call_count == range_result

    async def test_list_schedule_history_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.list_schedule_history(uuid4())

        mock_session.rollback.assert_awaited_once()

    async def test_close_schedule_returns_none_when_already_closed(
        self, repo, mock_session
    ):
        close_dto = CloseScheduleDTO(
            schedule_id=uuid4(),
            company_id=uuid4(),
            created_by=uuid4(),
            amount_service=10,
            amount_product=None,
            amount_discount=None,
            amount_total=10,
            payment_method=PaymentMethod.pix,
            payment_status=PaymentStatus.paid,
            paid_at=datetime(2026, 2, 14, 10, 0, 0),
        )
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock()
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.close_schedule(close_dto)

        assert result is None

    async def test_close_schedule_success(self, repo, mock_session):
        close_dto = CloseScheduleDTO(
            schedule_id=uuid4(),
            company_id=uuid4(),
            created_by=uuid4(),
            amount_service=10,
            amount_product=None,
            amount_discount=None,
            amount_total=10,
            payment_method=PaymentMethod.pix,
            payment_status=PaymentStatus.paid,
            paid_at=datetime(2026, 2, 14, 10, 0, 0),
        )
        existing_result = MagicMock()
        existing_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=existing_result)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        expected = MagicMock(spec=ScheduleFinanceOutDTO)

        with patch.object(
            ScheduleFinanceOutDTO, 'model_validate', return_value=expected
        ):
            result = await repo.close_schedule(close_dto)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_awaited_once()
        added_instance = mock_session.add.call_args[0][0]
        mock_session.refresh.assert_awaited_once_with(added_instance)
        assert result == expected

    async def test_sum_sale_for_service_ids_sums_prices(self, repo, mock_session):
        company_id = uuid4()
        s1, s2 = uuid4(), uuid4()
        svc_a = MagicMock()
        svc_a.id = s1
        svc_a.price = Decimal('30')
        svc_a.status = True
        svc_b = MagicMock()
        svc_b.id = s2
        svc_b.price = Decimal('20.50')
        svc_b.status = True
        res = MagicMock()
        mock_scalar_result = MagicMock()
        mock_scalar_result.all.return_value = [svc_a, svc_b]
        res.scalars.return_value = mock_scalar_result
        mock_session.execute = AsyncMock(return_value=res)

        total = await repo.sum_sale_for_service_ids([s1, s2], company_id)

        assert total == Decimal('50.50')

    async def test_sum_sale_for_service_ids_empty_returns_none(
        self, repo, mock_session
    ):
        assert await repo.sum_sale_for_service_ids([], uuid4()) is None

    async def test_sum_sale_for_service_ids_returns_none_when_service_missing(
        self, repo, mock_session
    ):
        company_id = uuid4()
        asked = uuid4()
        other = uuid4()
        svc = MagicMock()
        svc.id = other
        svc.price = Decimal('10')
        svc.status = True
        res = MagicMock()
        mock_scalar = MagicMock()
        mock_scalar.all.return_value = [svc]
        res.scalars.return_value = mock_scalar
        mock_session.execute = AsyncMock(return_value=res)

        assert await repo.sum_sale_for_service_ids([asked], company_id) is None

    async def test_sum_sale_for_service_ids_returns_none_when_service_inactive(
        self, repo, mock_session
    ):
        company_id = uuid4()
        sid = uuid4()
        svc = MagicMock()
        svc.id = sid
        svc.price = Decimal('10')
        svc.status = False
        res = MagicMock()
        mock_scalar = MagicMock()
        mock_scalar.all.return_value = [svc]
        res.scalars.return_value = mock_scalar
        mock_session.execute = AsyncMock(return_value=res)

        assert await repo.sum_sale_for_service_ids([sid], company_id) is None

    async def test_sum_sale_for_service_ids_raises_database_exception_on_error(
        self, repo, mock_session
    ):
        mock_session.execute = AsyncMock(side_effect=RuntimeError('execute failed'))

        with pytest.raises(DatabaseException, match='execute failed'):
            await repo.sum_sale_for_service_ids([uuid4()], uuid4())

    async def test_close_schedule_rollback_on_error(self, repo, mock_session):
        close_dto = CloseScheduleDTO(
            schedule_id=uuid4(),
            company_id=uuid4(),
            created_by=uuid4(),
            amount_service=10,
            amount_product=None,
            amount_discount=None,
            amount_total=10,
            payment_method=PaymentMethod.pix,
            payment_status=PaymentStatus.paid,
            paid_at=datetime(2026, 2, 14, 10, 0, 0),
        )
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.close_schedule(close_dto)

        mock_session.rollback.assert_awaited_once()
