from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import List, Sequence
from uuid import UUID

from sqlalchemy import Date, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.analytics import (
    BarberRankingItemDTO,
    CustomerMetricsDTO,
    DashboardFilterDTO,
    DashboardMetricsDTO,
    MonthlySummaryDTO,
)
from src.domain.repositories.analytics import AnalyticsRepository
from src.infrastructure.database.models.commom.payment_status import PaymentStatus
from src.infrastructure.database.models.employees import Employee
from src.infrastructure.database.models.expense import Expense
from src.infrastructure.database.models.schedule import Schedule
from src.infrastructure.database.models.schedule_finance import ScheduleFinance


class AnalyticsRepositoryPostgres(AnalyticsRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _period_bounds(start_date: date, end_date: date) -> tuple[datetime, datetime]:
        period_start = datetime.combine(start_date, time.min)
        period_end_exclusive = datetime.combine(end_date + timedelta(days=1), time.min)
        return period_start, period_end_exclusive

    @staticmethod
    def _safe_decimal(value: Decimal | None) -> Decimal:
        return value if value is not None else Decimal('0')

    @staticmethod
    def _safe_rate(numerator: int, denominator: int) -> float:
        if denominator == 0:
            return 0.0
        return round((numerator / denominator) * 100, 2)

    def _history_filters(self, dashboard_filter: DashboardFilterDTO) -> list:
        filters: list = [
            Schedule.company_id.__eq__(dashboard_filter.company_id),
            Schedule.is_deleted.__eq__(False),
            Schedule.is_canceled.__eq__(False),
            ScheduleFinance.is_deleted.__eq__(False),
            ScheduleFinance.payment_status.__eq__(PaymentStatus.paid),
            ScheduleFinance.paid_at.is_not(None),
        ]
        if dashboard_filter.employee_id is not None:
            filters.append(Schedule.employee_id.__eq__(dashboard_filter.employee_id))
        return filters

    def _period_filters(
        self,
        dashboard_filter: DashboardFilterDTO,
        period_start: datetime,
        period_end_exclusive: datetime,
    ) -> list:
        filters = self._history_filters(dashboard_filter)
        filters.extend([
            ScheduleFinance.paid_at.__ge__(period_start),
            ScheduleFinance.paid_at.__lt__(period_end_exclusive),
        ])
        return filters

    async def _count_new_clients(
        self,
        dashboard_filter: DashboardFilterDTO,
        period_start: datetime,
        period_end_exclusive: datetime,
        employee_id: UUID | None = None,
    ) -> int:
        local_filter = DashboardFilterDTO(
            company_id=dashboard_filter.company_id,
            start_date=dashboard_filter.start_date,
            end_date=dashboard_filter.end_date,
            employee_id=(
                employee_id if employee_id is not None else dashboard_filter.employee_id
            ),
        )

        first_attendance_subquery = (
            select(
                Schedule.user_id.label('user_id'),
                func.min(ScheduleFinance.paid_at).label('first_paid_at'),
            )
            .select_from(ScheduleFinance)
            .join(Schedule, Schedule.id.__eq__(ScheduleFinance.schedule_id))
            .where(*self._history_filters(local_filter))
            .group_by(Schedule.user_id)
            .subquery()
        )

        query = select(func.count()).where(
            first_attendance_subquery.c.first_paid_at.__ge__(period_start),
            first_attendance_subquery.c.first_paid_at.__lt__(period_end_exclusive),
        )
        result = await self.session.execute(query)
        return int(result.scalar_one() or 0)

    async def _build_monthly_summary(
        self,
        dashboard_filter: DashboardFilterDTO,
        period_start: datetime,
        period_end_exclusive: datetime,
    ) -> MonthlySummaryDTO:
        paid_query = (
            select(
                func.sum(ScheduleFinance.amount_total).label('faturamento_bruto'),
                func.count(ScheduleFinance.id).label('total_atendimentos'),
                func.count(func.distinct(Schedule.user_id)).label('clientes_distintos'),
                func.count(func.distinct(cast(ScheduleFinance.paid_at, Date))).label(
                    'dias_trabalhados'
                ),
            )
            .select_from(ScheduleFinance)
            .join(Schedule, Schedule.id.__eq__(ScheduleFinance.schedule_id))
            .where(
                *self._period_filters(
                    dashboard_filter, period_start, period_end_exclusive
                )
            )
        )
        paid_row = (await self.session.execute(paid_query)).one()

        faturamento_bruto = self._safe_decimal(paid_row.faturamento_bruto)
        total_atendimentos = int(paid_row.total_atendimentos or 0)
        clientes_distintos = int(paid_row.clientes_distintos or 0)
        dias_trabalhados = int(paid_row.dias_trabalhados or 0)

        expense_filters: list = [
            Expense.company_id.__eq__(dashboard_filter.company_id),
            Expense.is_deleted.__eq__(False),
            Expense.occurred_at.__ge__(period_start),
            Expense.occurred_at.__lt__(period_end_exclusive),
        ]
        if dashboard_filter.employee_id is not None:
            expense_filters.append(
                Expense.employee_id.__eq__(dashboard_filter.employee_id)
            )

        expense_query = select(func.sum(Expense.amount)).where(*expense_filters)
        despesas = self._safe_decimal(
            (await self.session.execute(expense_query)).scalar_one()
        )

        lucro = faturamento_bruto - despesas
        margem_percentual = (
            0.0
            if faturamento_bruto == Decimal('0')
            else round(float((lucro / faturamento_bruto) * Decimal('100')), 2)
        )
        ticket_medio_atendimento = (
            Decimal('0')
            if total_atendimentos == 0
            else faturamento_bruto / Decimal(total_atendimentos)
        )
        ticket_medio_cliente = (
            Decimal('0')
            if clientes_distintos == 0
            else faturamento_bruto / Decimal(clientes_distintos)
        )

        clientes_novos_periodo = await self._count_new_clients(
            dashboard_filter, period_start, period_end_exclusive
        )

        clients_with_multiple_visits_query = select(func.count()).select_from(
            select(Schedule.user_id)
            .select_from(ScheduleFinance)
            .join(Schedule, Schedule.id.__eq__(ScheduleFinance.schedule_id))
            .where(
                *self._period_filters(
                    dashboard_filter, period_start, period_end_exclusive
                )
            )
            .group_by(Schedule.user_id)
            .having(func.count(ScheduleFinance.id) > 1)
            .subquery()
        )
        clientes_com_retorno = int(
            (
                await self.session.execute(clients_with_multiple_visits_query)
            ).scalar_one()
            or 0
        )

        return MonthlySummaryDTO(
            faturamento_bruto=faturamento_bruto,
            despesas=despesas,
            lucro=lucro,
            margem_percentual=margem_percentual,
            total_atendimentos=total_atendimentos,
            clientes_distintos=clientes_distintos,
            ticket_medio_atendimento=ticket_medio_atendimento,
            ticket_medio_cliente=ticket_medio_cliente,
            clientes_novos_periodo=clientes_novos_periodo,
            taxa_retorno_percentual=self._safe_rate(
                clientes_com_retorno, clientes_distintos
            ),
            atendimentos_por_dia=round(
                (
                    total_atendimentos / dias_trabalhados
                    if dias_trabalhados > 0
                    else 0.0
                ),
                2,
            ),
        )

    async def _build_barber_ranking(
        self,
        dashboard_filter: DashboardFilterDTO,
        period_start: datetime,
        period_end_exclusive: datetime,
    ) -> List[BarberRankingItemDTO]:
        query = (
            select(
                Schedule.employee_id.label('employee_id'),
                Employee.name.label('employee_name'),
                func.sum(ScheduleFinance.amount_total).label('faturamento'),
                func.count(ScheduleFinance.id).label('atendimentos'),
                func.count(func.distinct(Schedule.user_id)).label('clientes_distintos'),
            )
            .select_from(ScheduleFinance)
            .join(Schedule, Schedule.id.__eq__(ScheduleFinance.schedule_id))
            .outerjoin(Employee, Employee.id.__eq__(Schedule.employee_id))
            .where(
                *self._period_filters(
                    dashboard_filter, period_start, period_end_exclusive
                )
            )
            .group_by(Schedule.employee_id, Employee.name)
            .order_by(func.sum(ScheduleFinance.amount_total).desc())
        )
        rows: Sequence = (await self.session.execute(query)).all()

        ranking: list[BarberRankingItemDTO] = []
        for row in rows:
            employee_id: UUID = row.employee_id
            faturamento = self._safe_decimal(row.faturamento)
            atendimentos = int(row.atendimentos or 0)
            clientes_distintos = int(row.clientes_distintos or 0)

            clientes_novos = await self._count_new_clients(
                dashboard_filter,
                period_start,
                period_end_exclusive,
                employee_id=employee_id,
            )

            retorno_query = select(func.count()).select_from(
                select(Schedule.user_id)
                .select_from(ScheduleFinance)
                .join(Schedule, Schedule.id.__eq__(ScheduleFinance.schedule_id))
                .where(
                    *self._period_filters(
                        DashboardFilterDTO(
                            company_id=dashboard_filter.company_id,
                            start_date=dashboard_filter.start_date,
                            end_date=dashboard_filter.end_date,
                            employee_id=employee_id,
                        ),
                        period_start,
                        period_end_exclusive,
                    )
                )
                .group_by(Schedule.user_id)
                .having(func.count(ScheduleFinance.id) > 1)
                .subquery()
            )
            clientes_com_retorno = int(
                (await self.session.execute(retorno_query)).scalar_one() or 0
            )

            ticket_medio_atendimento = (
                Decimal('0')
                if atendimentos == 0
                else faturamento / Decimal(atendimentos)
            )
            ticket_medio_cliente = (
                Decimal('0')
                if clientes_distintos == 0
                else faturamento / Decimal(clientes_distintos)
            )
            frequencia_media_clientes = round(
                (atendimentos / clientes_distintos) if clientes_distintos > 0 else 0.0,
                2,
            )

            ranking.append(
                BarberRankingItemDTO(
                    employee_id=employee_id,
                    employee_name=row.employee_name or 'Sem nome',
                    faturamento=faturamento,
                    atendimentos=atendimentos,
                    clientes_distintos=clientes_distintos,
                    ticket_medio_atendimento=ticket_medio_atendimento,
                    ticket_medio_cliente=ticket_medio_cliente,
                    clientes_novos=clientes_novos,
                    taxa_retorno_percentual=self._safe_rate(
                        clientes_com_retorno, clientes_distintos
                    ),
                    frequencia_media_clientes=frequencia_media_clientes,
                )
            )

        return ranking

    async def _build_customer_metrics(
        self,
        dashboard_filter: DashboardFilterDTO,
        period_start: datetime,
        period_end_exclusive: datetime,
    ) -> CustomerMetricsDTO:
        base_period_query = (
            select(
                func.count(ScheduleFinance.id).label('total_atendimentos'),
                func.count(func.distinct(Schedule.user_id)).label('clientes_distintos'),
            )
            .select_from(ScheduleFinance)
            .join(Schedule, Schedule.id.__eq__(ScheduleFinance.schedule_id))
            .where(
                *self._period_filters(
                    dashboard_filter, period_start, period_end_exclusive
                )
            )
        )
        base_period_row = (await self.session.execute(base_period_query)).one()
        total_atendimentos = int(base_period_row.total_atendimentos or 0)
        clientes_distintos = int(base_period_row.clientes_distintos or 0)

        clientes_novos = await self._count_new_clients(
            dashboard_filter, period_start, period_end_exclusive
        )
        clientes_recorrentes = max(clientes_distintos - clientes_novos, 0)

        period_users_subquery = (
            select(func.distinct(Schedule.user_id).label('user_id'))
            .select_from(ScheduleFinance)
            .join(Schedule, Schedule.id.__eq__(ScheduleFinance.schedule_id))
            .where(
                *self._period_filters(
                    dashboard_filter, period_start, period_end_exclusive
                )
            )
            .subquery()
        )

        historical_visits_query = (
            select(
                Schedule.user_id.label('user_id'),
                func.count(ScheduleFinance.id).label('total_visits'),
            )
            .select_from(ScheduleFinance)
            .join(Schedule, Schedule.id.__eq__(ScheduleFinance.schedule_id))
            .where(
                *self._history_filters(dashboard_filter),
                Schedule.user_id.in_(select(period_users_subquery.c.user_id)),
            )
            .group_by(Schedule.user_id)
            .subquery()
        )

        clientes_nunca_voltaram_query = select(func.count()).where(
            historical_visits_query.c.total_visits.__eq__(1)
        )
        clientes_nunca_voltaram = int(
            (await self.session.execute(clientes_nunca_voltaram_query)).scalar_one()
            or 0
        )

        clientes_com_mais_de_uma_visita_query = select(func.count()).where(
            historical_visits_query.c.total_visits.__gt__(1)
        )
        clientes_com_retorno = int(
            (
                await self.session.execute(clientes_com_mais_de_uma_visita_query)
            ).scalar_one()
            or 0
        )

        return CustomerMetricsDTO(
            clientes_distintos=clientes_distintos,
            clientes_novos=clientes_novos,
            clientes_recorrentes=clientes_recorrentes,
            frequencia_media=round(
                (
                    total_atendimentos / clientes_distintos
                    if clientes_distintos > 0
                    else 0.0
                ),
                2,
            ),
            clientes_nunca_voltaram=clientes_nunca_voltaram,
            taxa_retorno_percentual=self._safe_rate(
                clientes_com_retorno, clientes_distintos
            ),
        )

    async def get_dashboard_metrics(
        self, dashboard_filter: DashboardFilterDTO
    ) -> DashboardMetricsDTO:
        try:
            period_start, period_end_exclusive = self._period_bounds(
                dashboard_filter.start_date, dashboard_filter.end_date
            )

            summary = await self._build_monthly_summary(
                dashboard_filter, period_start, period_end_exclusive
            )
            ranking = await self._build_barber_ranking(
                dashboard_filter, period_start, period_end_exclusive
            )
            customer_metrics = await self._build_customer_metrics(
                dashboard_filter, period_start, period_end_exclusive
            )

            return DashboardMetricsDTO(
                resumo_mes=summary,
                ranking_barbeiros=ranking,
                indicadores_clientes=customer_metrics,
            )
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))
