from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.subscription_plan import (
    SubscriptionPlanCreateDTO,
    SubscriptionPlanOutDTO,
    SubscriptionPlanUpdateDTO,
)
from src.domain.repositories.subscription_plan import SubscriptionPlanRepository
from src.infrastructure.database.models.service import Service
from src.infrastructure.database.models.subscription_plan import SubscriptionPlan


class SubscriptionPlanRepositoryPostgres(SubscriptionPlanRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def service_belongs_to_company(
        self, service_id: UUID, company_id: UUID
    ) -> bool:
        try:
            q = select(Service).where(
                Service.id == service_id,
                Service.company_id == company_id,
                Service.is_deleted.is_(False),
            )
            r = await self.session.execute(q)
            return r.scalar_one_or_none() is not None
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error

    async def create_plan(
        self, data: SubscriptionPlanCreateDTO
    ) -> SubscriptionPlanOutDTO:
        try:
            row = SubscriptionPlan(**data.model_dump())
            self.session.add(row)
            await self.session.commit()
            await self.session.refresh(row)
            return SubscriptionPlanOutDTO.model_validate(row)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error

    async def get_plan(
        self,
        id: UUID,
        company_id: UUID,
        *,
        active_only: bool = False,
    ) -> Optional[SubscriptionPlanOutDTO]:
        try:
            flt = [
                SubscriptionPlan.id == id,
                SubscriptionPlan.company_id == company_id,
                SubscriptionPlan.is_deleted.is_(False),
            ]
            if active_only:
                flt.append(SubscriptionPlan.is_active.is_(True))
            q = select(SubscriptionPlan).where(*flt)
            r = await self.session.execute(q)
            row = r.scalar_one_or_none()
            if row is None:
                return None
            return SubscriptionPlanOutDTO.model_validate(row)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error

    async def list_plans(
        self,
        pagination: PaginationParamsDTO,
        company_id: UUID,
        *,
        active_only: bool = False,
    ) -> List[SubscriptionPlanOutDTO]:
        try:
            flt = [
                SubscriptionPlan.company_id == company_id,
                SubscriptionPlan.is_deleted.is_(False),
            ]
            if active_only:
                flt.append(SubscriptionPlan.is_active.is_(True))
            q = (
                select(SubscriptionPlan)
                .where(*flt)
                .order_by(SubscriptionPlan.created_at.desc())
            )
            if (
                pagination.filter_by
                and pagination.filter_value
                and hasattr(SubscriptionPlan, pagination.filter_by)
            ):
                q = q.filter(
                    getattr(SubscriptionPlan, pagination.filter_by).ilike(
                        f'%{pagination.filter_value}%'
                    )
                )
            q = q.offset(pagination.offset).limit(pagination.limit)
            r = await self.session.execute(q)
            return [SubscriptionPlanOutDTO.model_validate(x) for x in r.scalars().all()]
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error

    async def update_plan(
        self, id: UUID, data: SubscriptionPlanUpdateDTO, company_id: UUID
    ) -> Optional[SubscriptionPlanOutDTO]:
        try:
            update_data = data.model_dump(exclude_unset=True, exclude_none=True)
            if not update_data:
                return await self.get_plan(id, company_id)
            stmt = (
                update(SubscriptionPlan)
                .where(
                    SubscriptionPlan.id == id,
                    SubscriptionPlan.company_id == company_id,
                    SubscriptionPlan.is_deleted.is_(False),
                )
                .values(**update_data)
                .returning(SubscriptionPlan)
            )
            r = await self.session.execute(stmt)
            await self.session.commit()
            row = r.scalar_one_or_none()
            if row is None:
                return None
            return SubscriptionPlanOutDTO.model_validate(row)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error

    async def delete_plan(self, id: UUID, company_id: UUID) -> bool:
        try:
            stmt = (
                update(SubscriptionPlan)
                .where(
                    SubscriptionPlan.id == id,
                    SubscriptionPlan.company_id == company_id,
                    SubscriptionPlan.is_deleted.is_(False),
                )
                .values(is_deleted=True)
            )
            r = await self.session.execute(stmt)
            await self.session.commit()
            return r.rowcount > 0
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error
