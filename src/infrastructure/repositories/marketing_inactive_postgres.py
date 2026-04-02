from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.marketing import InactiveClientsPayloadDTO, InactiveClientUserDTO
from src.domain.dtos.schedule import ScheduleOutDTO
from src.domain.repositories.marketing_inactive import MarketingInactiveRepository
from src.infrastructure.database.models.employees import Employee
from src.infrastructure.database.models.product import Product
from src.infrastructure.database.models.schedule import Schedule
from src.infrastructure.database.models.service import Service
from src.infrastructure.database.models.users import User
from src.infrastructure.repositories.schedule_postgres import ScheduleRepositoryPostgres


def _utc_naive_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _since_utc_naive(lookback_years: int) -> datetime:
    return _utc_naive_now() - timedelta(days=365 * lookback_years)


def _days_since_last_visit(
    last_visit_at: datetime | None,
    fallback: datetime,
) -> int:
    base = last_visit_at if last_visit_at is not None else fallback
    if base.tzinfo is not None:
        base = base.astimezone(timezone.utc).replace(tzinfo=None)
    now_naive = _utc_naive_now()
    delta = now_naive - base
    return max(0, delta.days)


class MarketingInactiveRepositoryPostgres(MarketingInactiveRepository):
    """Usuários inativos + agendamentos recentes para o painel de marketing."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def fetch_inactive_clients(
        self,
        company_id: UUID,
        *,
        email: str | None = None,
        min_days: int | None = None,
        max_days: int | None = None,
        lookback_years: int = 2,
        schedules_limit: int = 3000,
    ) -> InactiveClientsPayloadDTO:
        try:
            last_visit_sq = (
                select(
                    Schedule.user_id.label('uid'),
                    func.max(
                        func.coalesce(
                            Schedule.time_end,
                            Schedule.time_start,
                            Schedule.time_register,
                        )
                    ).label('last_visit_at'),
                )
                .where(
                    Schedule.company_id == company_id,
                    Schedule.is_deleted.is_(False),
                    Schedule.is_canceled.is_(False),
                )
                .group_by(Schedule.user_id)
            ).subquery()

            user_query = (
                select(User, last_visit_sq.c.last_visit_at)
                .outerjoin(last_visit_sq, User.id == last_visit_sq.c.uid)
                .where(
                    User.company_id == company_id,
                    User.is_deleted.is_(False),
                )
            )
            if email and email.strip():
                user_query = user_query.where(User.email.ilike(f'%{email.strip()}%'))

            user_query = user_query.order_by(User.name.asc())
            user_result = await self.session.execute(user_query)
            rows = user_result.all()

            users_out: List[InactiveClientUserDTO] = []
            for row in rows:
                u: User = row[0]
                last_visit: datetime | None = row[1]
                days = _days_since_last_visit(last_visit, u.created_at)

                if min_days is not None and days < min_days:
                    continue
                if max_days is not None and days > max_days:
                    continue

                users_out.append(
                    InactiveClientUserDTO(
                        id=u.id,
                        name=u.name,
                        email=u.email,
                        phone=u.phone,
                        company_id=u.company_id,
                        is_active=u.is_active,
                        last_visit_at=last_visit,
                        days_since_last_visit=days,
                    )
                )

            users_out.sort(
                key=lambda x: x.days_since_last_visit,
                reverse=True,
            )

            since = _since_utc_naive(lookback_years)
            schedules = await self._list_schedules_lookback(
                company_id, since=since, limit=schedules_limit
            )

            return InactiveClientsPayloadDTO(users=users_out, schedules=schedules)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def _list_schedules_lookback(
        self,
        company_id: UUID,
        *,
        since: datetime,
        limit: int,
    ) -> List[ScheduleOutDTO]:
        id_filters = [
            Schedule.is_deleted.is_(False),
            Schedule.company_id == company_id,
            Schedule.time_register >= since,
        ]
        paginated_ids = (
            select(Schedule.id)
            .where(*id_filters)
            .order_by(Schedule.created_at.desc())
            .limit(limit)
            .subquery()
        )

        names_sq = (
            select(sa.func.array_agg(Service.name))
            .where(Service.id.__eq__(sa.any_(Schedule.service_id)))
            .scalar_subquery()
        )
        duration_sq = (
            select(sa.func.sum(Service.duration))
            .where(Service.id.__eq__(sa.any_(Schedule.service_id)))
            .scalar_subquery()
        )

        query = (
            select(
                Schedule,
                User.name.label('user_name'),
                Employee.name.label('employee_name'),
                names_sq.label('service_names'),
                Product.name.label('product_name'),
                duration_sq.label('service_duration_minutes'),
            )
            .outerjoin(User, Schedule.user_id == User.id)
            .outerjoin(Employee, Schedule.employee_id == Employee.id)
            .outerjoin(Product, Schedule.product_id == Product.id)
            .where(Schedule.id.in_(select(paginated_ids.c.id)))
            .order_by(Schedule.created_at.desc())
        )
        result = await self.session.execute(query)
        return [
            ScheduleRepositoryPostgres._schedule_row_to_out_dto(*row)
            for row in result.all()
        ]
