from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.analytics import DashboardFilterDTO
from src.infrastructure.repositories.analytics_postgres import (
    AnalyticsRepositoryPostgres,
)


def _one_result(row):
    result = MagicMock()
    result.one.return_value = row
    return result


def _scalar_result(value):
    result = MagicMock()
    result.scalar_one.return_value = value
    return result


def _all_result(rows):
    result = MagicMock()
    result.all.return_value = rows
    return result


@pytest.mark.unit
class TestAnalyticsRepositoryPostgres:
    @pytest.fixture
    def mock_session(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repo(self, mock_session):
        return AnalyticsRepositoryPostgres(session=mock_session)

    @pytest.mark.asyncio
    async def test_get_dashboard_metrics_success(self, repo, mock_session):
        employee_id = uuid4()
        filter_dto = DashboardFilterDTO(
            company_id=uuid4(),
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            employee_id=None,
        )

        paid_row = SimpleNamespace(
            gross_revenue=Decimal('1000.00'),
            total_appointments=20,
            distinct_customers=10,
            working_days=5,
        )
        ranking_row = SimpleNamespace(
            employee_id=employee_id,
            employee_name='Hedris',
            revenue=Decimal('600.00'),
            appointments_count=12,
            distinct_customers=8,
        )
        service_a = uuid4()
        service_b = uuid4()
        service_ranking_row_1 = SimpleNamespace(
            service_id=service_a,
            service_name='Corte',
            appointments_count=7,
            revenue=Decimal('150.50'),
        )
        service_ranking_row_2 = SimpleNamespace(
            service_id=service_b,
            service_name='Barba',
            appointments_count=None,
            revenue=None,
        )
        base_period_row = SimpleNamespace(total_appointments=20, distinct_customers=10)

        mock_session.execute = AsyncMock(
            side_effect=[
                _one_result(paid_row),  # paid_query
                _scalar_result(Decimal('250.00')),  # expense_query
                _scalar_result(3),  # _count_new_clients (summary)
                _scalar_result(4),  # clients_with_multiple_visits_query
                _all_result([ranking_row]),  # ranking query
                _scalar_result(2),  # _count_new_clients (ranking row)
                _scalar_result(3),  # return_rate_subquery
                _all_result([
                    service_ranking_row_1,
                    service_ranking_row_2,
                ]),  # service ranking
                _one_result(base_period_row),  # base_period_query
                _scalar_result(3),  # _count_new_clients (customer metrics)
                _scalar_result(2),  # never_returned_query
                _scalar_result(5),  # multiple_visits_query
            ]
        )

        result = await repo.get_dashboard_metrics(filter_dto)
        arrange_values = 20
        arrange_values_2 = 10
        arrange_values_3 = 3
        arrange_values_4 = 1
        arrange_values_5 = 2
        arrange_values_6 = 7

        assert result.monthly_summary.gross_revenue == Decimal('1000.00')
        assert result.monthly_summary.expenses == Decimal('250.00')
        assert result.monthly_summary.total_appointments == arrange_values
        assert result.monthly_summary.new_customers_in_period == arrange_values_3
        assert len(result.barber_ranking) == arrange_values_4
        assert result.barber_ranking[0].employee_id == employee_id
        assert len(result.service_ranking) == arrange_values_5
        assert result.service_ranking[0].service_id == service_a
        assert result.service_ranking[0].service_name == 'Corte'
        assert result.service_ranking[0].appointments_count == arrange_values_6
        assert result.service_ranking[0].revenue == Decimal('150.50')
        assert result.service_ranking[1].service_id == service_b
        assert result.service_ranking[1].appointments_count == 0
        assert result.service_ranking[1].revenue == Decimal('0')
        assert result.customer_metrics.distinct_customers == arrange_values_2

    @pytest.mark.asyncio
    async def test_get_dashboard_metrics_rollback_on_error(self, repo, mock_session):
        filter_dto = DashboardFilterDTO(
            company_id=uuid4(),
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            employee_id=None,
        )
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.get_dashboard_metrics(filter_dto)

        mock_session.rollback.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_dashboard_metrics_handles_zero_denominators_with_employee_filter(
        self, repo, mock_session
    ):
        employee_id = uuid4()
        filter_dto = DashboardFilterDTO(
            company_id=uuid4(),
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            employee_id=employee_id,
        )

        paid_row = SimpleNamespace(
            gross_revenue=Decimal('0.00'),
            total_appointments=0,
            distinct_customers=0,
            working_days=0,
        )
        base_period_row = SimpleNamespace(total_appointments=0, distinct_customers=0)

        mock_session.execute = AsyncMock(
            side_effect=[
                _one_result(paid_row),  # paid_query
                _scalar_result(Decimal('0.00')),  # expense_query
                _scalar_result(0),  # _count_new_clients (summary)
                _scalar_result(0),  # clients_with_multiple_visits_query
                _all_result([]),  # ranking query
                _all_result([]),  # service ranking
                _one_result(base_period_row),  # base_period_query
                _scalar_result(0),  # _count_new_clients (customer metrics)
                _scalar_result(0),  # never_returned_query
                _scalar_result(0),  # multiple_visits_query
            ]
        )

        result = await repo.get_dashboard_metrics(filter_dto)

        assert result.monthly_summary.return_rate_percent == 0.0
        assert result.customer_metrics.return_rate_percent == 0.0
        assert result.monthly_summary.expenses == Decimal('0')
