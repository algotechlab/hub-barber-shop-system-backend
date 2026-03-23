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
    ServiceRankingItemDTO,
)
from src.domain.repositories.analytics import AnalyticsRepository
from src.infrastructure.database.models.commom.payment_status import PaymentStatus
from src.infrastructure.database.models.employees import Employee
from src.infrastructure.database.models.expense import Expense
from src.infrastructure.database.models.schedule import Schedule
from src.infrastructure.database.models.schedule_finance import ScheduleFinance
from src.infrastructure.database.models.service import Service


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
                func.sum(ScheduleFinance.amount_total).label('gross_revenue'),
                func.count(ScheduleFinance.id).label('total_appointments'),
                func.count(func.distinct(Schedule.user_id)).label('distinct_customers'),
                func.count(func.distinct(cast(ScheduleFinance.paid_at, Date))).label(
                    'working_days'
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

        gross_revenue = self._safe_decimal(paid_row.gross_revenue)
        total_appointments = int(paid_row.total_appointments or 0)
        distinct_customers = int(paid_row.distinct_customers or 0)
        working_days = int(paid_row.working_days or 0)

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
        expenses = self._safe_decimal(
            (await self.session.execute(expense_query)).scalar_one()
        )

        profit = gross_revenue - expenses
        margin_percent = (
            0.0
            if gross_revenue == Decimal('0')
            else round(float((profit / gross_revenue) * Decimal('100')), 2)
        )
        avg_ticket_per_appointment = (
            Decimal('0')
            if total_appointments == 0
            else gross_revenue / Decimal(total_appointments)
        )
        avg_ticket_per_customer = (
            Decimal('0')
            if distinct_customers == 0
            else gross_revenue / Decimal(distinct_customers)
        )

        new_customers_in_period = await self._count_new_clients(
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
        returning_customers_count = int(
            (
                await self.session.execute(clients_with_multiple_visits_query)
            ).scalar_one()
            or 0
        )

        return MonthlySummaryDTO(
            gross_revenue=gross_revenue,
            expenses=expenses,
            profit=profit,
            margin_percent=margin_percent,
            total_appointments=total_appointments,
            distinct_customers=distinct_customers,
            avg_ticket_per_appointment=avg_ticket_per_appointment,
            avg_ticket_per_customer=avg_ticket_per_customer,
            new_customers_in_period=new_customers_in_period,
            return_rate_percent=self._safe_rate(
                returning_customers_count, distinct_customers
            ),
            appointments_per_day=round(
                (total_appointments / working_days if working_days > 0 else 0.0),
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
                func.sum(ScheduleFinance.amount_total).label('revenue'),
                func.count(ScheduleFinance.id).label('appointments_count'),
                func.count(func.distinct(Schedule.user_id)).label('distinct_customers'),
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
            revenue = self._safe_decimal(row.revenue)
            appointments_count = int(row.appointments_count or 0)
            distinct_customers = int(row.distinct_customers or 0)

            new_customers = await self._count_new_clients(
                dashboard_filter,
                period_start,
                period_end_exclusive,
                employee_id=employee_id,
            )

            return_rate_subquery = select(func.count()).select_from(
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
            returning_customers = int(
                (await self.session.execute(return_rate_subquery)).scalar_one() or 0
            )

            avg_ticket_per_appointment = (
                Decimal('0')
                if appointments_count == 0
                else revenue / Decimal(appointments_count)
            )
            avg_ticket_per_customer = (
                Decimal('0')
                if distinct_customers == 0
                else revenue / Decimal(distinct_customers)
            )
            avg_customer_frequency = round(
                (appointments_count / distinct_customers)
                if distinct_customers > 0
                else 0.0,
                2,
            )

            ranking.append(
                BarberRankingItemDTO(
                    employee_id=employee_id,
                    employee_name=row.employee_name or 'Unnamed',
                    revenue=revenue,
                    appointments_count=appointments_count,
                    distinct_customers=distinct_customers,
                    avg_ticket_per_appointment=avg_ticket_per_appointment,
                    avg_ticket_per_customer=avg_ticket_per_customer,
                    new_customers=new_customers,
                    return_rate_percent=self._safe_rate(
                        returning_customers, distinct_customers
                    ),
                    avg_customer_frequency=avg_customer_frequency,
                )
            )

        return ranking

    async def _build_service_ranking(
        self,
        dashboard_filter: DashboardFilterDTO,
        period_start: datetime,
        period_end_exclusive: datetime,
    ) -> List[ServiceRankingItemDTO]:
        period_sf = (
            select(
                ScheduleFinance.id.label('sf_id'),
                ScheduleFinance.amount_service,
                ScheduleFinance.service_id,
            )
            .select_from(ScheduleFinance)
            .join(Schedule, Schedule.id.__eq__(ScheduleFinance.schedule_id))
            .where(
                *self._period_filters(
                    dashboard_filter, period_start, period_end_exclusive
                )
            )
        ).cte('period_sf')

        expanded = (
            select(
                period_sf.c.sf_id,
                period_sf.c.amount_service,
                func.unnest(period_sf.c.service_id).label('sid'),
            ).select_from(period_sf)
        ).cte('expanded')

        price_expr = func.coalesce(Service.price, 0)
        total_price = func.sum(price_expr).over(partition_by=expanded.c.sf_id)

        priced = (
            select(
                expanded.c.sf_id,
                expanded.c.sid,
                expanded.c.amount_service,
                price_expr.label('price'),
                total_price.label('total_price'),
            )
            .select_from(expanded)
            .join(Service, Service.id.__eq__(expanded.c.sid))
            .where(
                Service.is_deleted.__eq__(False),
                Service.company_id.__eq__(dashboard_filter.company_id),
            )
        ).cte('priced')

        revenue = func.coalesce(
            func.sum(
                priced.c.amount_service
                * (priced.c.price / func.nullif(priced.c.total_price, 0))
            ),
            0,
        ).label('revenue')

        final_query = (
            select(
                priced.c.sid.label('service_id'),
                Service.name.label('service_name'),
                func.count(func.distinct(priced.c.sf_id)).label('appointments_count'),
                revenue,
            )
            .select_from(priced)
            .join(Service, Service.id.__eq__(priced.c.sid))
            .group_by(priced.c.sid, Service.name)
            .order_by(revenue.desc())
            .limit(20)
        )

        result = await self.session.execute(final_query)
        rows = result.all()
        ranking: list[ServiceRankingItemDTO] = []
        for row in rows:
            ranking.append(
                ServiceRankingItemDTO(
                    service_id=row.service_id,
                    service_name=row.service_name,
                    appointments_count=int(row.appointments_count or 0),
                    revenue=self._safe_decimal(row.revenue),
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
                func.count(ScheduleFinance.id).label('total_appointments'),
                func.count(func.distinct(Schedule.user_id)).label('distinct_customers'),
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
        total_appointments = int(base_period_row.total_appointments or 0)
        distinct_customers = int(base_period_row.distinct_customers or 0)

        new_customers = await self._count_new_clients(
            dashboard_filter, period_start, period_end_exclusive
        )
        returning_customers = max(distinct_customers - new_customers, 0)

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

        never_returned_query = select(func.count()).where(
            historical_visits_query.c.total_visits.__eq__(1)
        )
        customers_never_returned = int(
            (await self.session.execute(never_returned_query)).scalar_one() or 0
        )

        multiple_visits_query = select(func.count()).where(
            historical_visits_query.c.total_visits.__gt__(1)
        )
        returning_visits_count = int(
            (await self.session.execute(multiple_visits_query)).scalar_one() or 0
        )

        return CustomerMetricsDTO(
            distinct_customers=distinct_customers,
            new_customers=new_customers,
            returning_customers=returning_customers,
            avg_frequency=round(
                (
                    total_appointments / distinct_customers
                    if distinct_customers > 0
                    else 0.0
                ),
                2,
            ),
            customers_never_returned=customers_never_returned,
            return_rate_percent=self._safe_rate(
                returning_visits_count, distinct_customers
            ),
        )

    async def get_dashboard_metrics(
        self, dashboard_filter: DashboardFilterDTO
    ) -> DashboardMetricsDTO:
        try:
            period_start, period_end_exclusive = self._period_bounds(
                dashboard_filter.start_date, dashboard_filter.end_date
            )

            monthly_summary = await self._build_monthly_summary(
                dashboard_filter, period_start, period_end_exclusive
            )
            barber_ranking = await self._build_barber_ranking(
                dashboard_filter, period_start, period_end_exclusive
            )
            service_ranking = await self._build_service_ranking(
                dashboard_filter, period_start, period_end_exclusive
            )
            customer_metrics = await self._build_customer_metrics(
                dashboard_filter, period_start, period_end_exclusive
            )

            return DashboardMetricsDTO(
                monthly_summary=monthly_summary,
                barber_ranking=barber_ranking,
                service_ranking=service_ranking,
                customer_metrics=customer_metrics,
            )
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))
