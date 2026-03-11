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
            faturamento_bruto=Decimal('1000.00'),
            total_atendimentos=20,
            clientes_distintos=10,
            dias_trabalhados=5,
        )
        ranking_row = SimpleNamespace(
            employee_id=employee_id,
            employee_name='Hedris',
            faturamento=Decimal('600.00'),
            atendimentos=12,
            clientes_distintos=8,
        )
        base_period_row = SimpleNamespace(total_atendimentos=20, clientes_distintos=10)

        mock_session.execute = AsyncMock(
            side_effect=[
                _one_result(paid_row),  # paid_query
                _scalar_result(Decimal('250.00')),  # expense_query
                _scalar_result(3),  # _count_new_clients (summary)
                _scalar_result(4),  # clients_with_multiple_visits_query
                _all_result([ranking_row]),  # ranking query
                _scalar_result(2),  # _count_new_clients (ranking row)
                _scalar_result(3),  # retorno_query
                _one_result(base_period_row),  # base_period_query
                _scalar_result(3),  # _count_new_clients (customer metrics)
                _scalar_result(2),  # clientes_nunca_voltaram_query
                _scalar_result(5),  # clientes_com_mais_de_uma_visita_query
            ]
        )

        result = await repo.get_dashboard_metrics(filter_dto)
        arrange_values = 20
        arrange_values_2 = 10
        arrange_values_3 = 3

        assert result.resumo_mes.faturamento_bruto == Decimal('1000.00')
        assert result.resumo_mes.despesas == Decimal('250.00')
        assert result.resumo_mes.total_atendimentos == arrange_values
        assert result.resumo_mes.clientes_novos_periodo == arrange_values_3
        assert len(result.ranking_barbeiros) == 1
        assert result.ranking_barbeiros[0].employee_id == employee_id
        assert result.indicadores_clientes.clientes_distintos == arrange_values_2

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
            faturamento_bruto=Decimal('0.00'),
            total_atendimentos=0,
            clientes_distintos=0,
            dias_trabalhados=0,
        )
        base_period_row = SimpleNamespace(total_atendimentos=0, clientes_distintos=0)

        mock_session.execute = AsyncMock(
            side_effect=[
                _one_result(paid_row),  # paid_query
                _scalar_result(Decimal('0.00')),  # expense_query
                _scalar_result(0),  # _count_new_clients (summary)
                _scalar_result(0),  # clients_with_multiple_visits_query
                _all_result([]),  # ranking query
                _one_result(base_period_row),  # base_period_query
                _scalar_result(0),  # _count_new_clients (customer metrics)
                _scalar_result(0),  # clientes_nunca_voltaram_query
                _scalar_result(0),  # clientes_com_mais_de_uma_visita_query
            ]
        )

        result = await repo.get_dashboard_metrics(filter_dto)

        # Valida linha de proteção de divisão por zero (_safe_rate -> 0.0)
        assert result.resumo_mes.taxa_retorno_percentual == 0.0
        assert result.indicadores_clientes.taxa_retorno_percentual == 0.0
        # Valida também que o fluxo com employee_id não quebra
        assert result.resumo_mes.despesas == Decimal('0')
