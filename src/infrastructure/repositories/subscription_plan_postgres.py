from typing import Dict, List, Optional, Sequence
from uuid import UUID

from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.subscription_plan import (
    SubscriptionPlanCreateDTO,
    SubscriptionPlanOutDTO,
    SubscriptionPlanProductLineOutDTO,
    SubscriptionPlanUpdateDTO,
)
from src.domain.repositories.subscription_plan import SubscriptionPlanRepository
from src.infrastructure.database.models.product import Product
from src.infrastructure.database.models.service import Service
from src.infrastructure.database.models.subscription_plan import SubscriptionPlan
from src.infrastructure.database.models.subscription_plan_junctions import (
    subscription_plan_product_table,
    subscription_plan_service_table,
)


class SubscriptionPlanRepositoryPostgres(SubscriptionPlanRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _service_ids_for_plan(
        self, plan_ids: Sequence[UUID]
    ) -> Dict[UUID, List[UUID]]:
        if not plan_ids:
            return {}
        q = select(
            subscription_plan_service_table.c.subscription_plan_id,
            subscription_plan_service_table.c.service_id,
        ).where(
            subscription_plan_service_table.c.subscription_plan_id.in_(list(plan_ids))
        )
        r = await self.session.execute(q)
        out: Dict[UUID, List[UUID]] = {p: [] for p in plan_ids}
        for plan_id, sid in r.all():
            out[plan_id].append(sid)
        return out

    async def _product_lines_for_plan(
        self, plan_ids: Sequence[UUID]
    ) -> Dict[UUID, List[SubscriptionPlanProductLineOutDTO]]:
        if not plan_ids:
            return {}
        q = select(
            subscription_plan_product_table.c.subscription_plan_id,
            subscription_plan_product_table.c.product_id,
            subscription_plan_product_table.c.quantity,
        ).where(
            subscription_plan_product_table.c.subscription_plan_id.in_(list(plan_ids))
        )
        r = await self.session.execute(q)
        out: Dict[UUID, List[SubscriptionPlanProductLineOutDTO]] = {
            p: [] for p in plan_ids
        }
        for plan_id, pid, qty in r.all():
            out[plan_id].append(
                SubscriptionPlanProductLineOutDTO(product_id=pid, quantity=qty)
            )
        return out

    def _row_to_dto(
        self,
        row: SubscriptionPlan,
        service_ids: List[UUID],
        product_lines: List[SubscriptionPlanProductLineOutDTO],
    ) -> SubscriptionPlanOutDTO:
        return SubscriptionPlanOutDTO(
            id=row.id,
            company_id=row.company_id,
            name=row.name,
            description=row.description,
            service_ids=service_ids,
            product_lines=product_lines,
            price=row.price,
            uses_per_month=row.uses_per_month,
            is_active=row.is_active,
            created_at=row.created_at,
            updated_at=row.updated_at,
            is_deleted=row.is_deleted,
        )

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

    async def product_belongs_to_company(
        self, product_id: UUID, company_id: UUID
    ) -> bool:
        try:
            q = select(Product).where(
                Product.id == product_id,
                Product.company_id == company_id,
                Product.is_deleted.is_(False),
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
            row = SubscriptionPlan(
                company_id=data.company_id,
                name=data.name,
                description=data.description,
                price=data.price,
                uses_per_month=data.uses_per_month,
                is_active=data.is_active,
            )
            self.session.add(row)
            await self.session.flush()
            plan_id = row.id
            for sid in data.service_ids:
                await self.session.execute(
                    insert(subscription_plan_service_table).values(
                        subscription_plan_id=plan_id, service_id=sid
                    )
                )
            for pl in data.product_lines:
                await self.session.execute(
                    insert(subscription_plan_product_table).values(
                        subscription_plan_id=plan_id,
                        product_id=pl.product_id,
                        quantity=pl.quantity,
                    )
                )
            await self.session.commit()
            await self.session.refresh(row)
            svc = await self._service_ids_for_plan([plan_id])
            pr = await self._product_lines_for_plan([plan_id])
            return self._row_to_dto(row, svc.get(plan_id, []), pr.get(plan_id, []))
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
            sid_map = await self._service_ids_for_plan([id])
            pl_map = await self._product_lines_for_plan([id])
            return self._row_to_dto(row, sid_map.get(id, []), pl_map.get(id, []))
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
            rows = list(r.scalars().all())
            if not rows:
                return []
            pids = [p.id for p in rows]
            s_map = await self._service_ids_for_plan(pids)
            pl_map = await self._product_lines_for_plan(pids)
            return [
                self._row_to_dto(row, s_map.get(row.id, []), pl_map.get(row.id, []))
                for row in rows
            ]
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error

    async def update_plan(
        self, id: UUID, data: SubscriptionPlanUpdateDTO, company_id: UUID
    ) -> Optional[SubscriptionPlanOutDTO]:
        try:
            field_updates = data.model_dump(
                exclude_unset=True, exclude={'service_ids', 'product_lines'}
            )
            q = select(SubscriptionPlan).where(
                SubscriptionPlan.id == id,
                SubscriptionPlan.company_id == company_id,
                SubscriptionPlan.is_deleted.is_(False),
            )
            r0 = await self.session.execute(q)
            existing = r0.scalar_one_or_none()
            if existing is None:
                return None

            if data.service_ids is not None:
                await self.session.execute(
                    delete(subscription_plan_service_table).where(
                        subscription_plan_service_table.c.subscription_plan_id == id
                    )
                )
                for sid in data.service_ids:
                    await self.session.execute(
                        insert(subscription_plan_service_table).values(
                            subscription_plan_id=id, service_id=sid
                        )
                    )
            if data.product_lines is not None:
                await self.session.execute(
                    delete(subscription_plan_product_table).where(
                        subscription_plan_product_table.c.subscription_plan_id == id
                    )
                )
                for pl in data.product_lines:
                    await self.session.execute(
                        insert(subscription_plan_product_table).values(
                            subscription_plan_id=id,
                            product_id=pl.product_id,
                            quantity=pl.quantity,
                        )
                    )
            for k, v in field_updates.items():
                setattr(existing, k, v)
            await self.session.commit()
            await self.session.refresh(existing)
            return await self.get_plan(id, company_id)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error

    async def delete_plan(self, id: UUID, company_id: UUID) -> bool:
        try:
            stmt = select(SubscriptionPlan).where(
                SubscriptionPlan.id == id,
                SubscriptionPlan.company_id == company_id,
                SubscriptionPlan.is_deleted.is_(False),
            )
            r0 = await self.session.execute(stmt)
            row = r0.scalar_one_or_none()
            if row is None:
                return False
            row.is_deleted = True
            await self.session.commit()
            return True
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error
