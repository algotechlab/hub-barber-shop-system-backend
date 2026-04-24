from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence
from uuid import UUID

from sqlalchemy import select, update
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
from src.domain.repositories.user_subscription import UserSubscriptionRepository
from src.infrastructure.database.models.commom.payment_method import PaymentMethod
from src.infrastructure.database.models.commom.user_subscription_status import (
    UserSubscriptionStatus,
)
from src.infrastructure.database.models.subscription_plan import SubscriptionPlan
from src.infrastructure.database.models.subscription_plan_junctions import (
    subscription_plan_product_table,
    subscription_plan_service_table,
)
from src.infrastructure.database.models.user_subscription import (
    UserSubscription as UserSubscriptionModel,
)
from src.infrastructure.database.models.users import User


def _status_for_create(status: str) -> UserSubscriptionStatus:
    if status == 'PENDING_PAYMENT':
        return UserSubscriptionStatus.pending_payment
    return UserSubscriptionStatus.active


class UserSubscriptionRepositoryPostgres(UserSubscriptionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _payment_method_to_str(
        row: UserSubscriptionModel,
    ) -> str | None:
        raw = getattr(row, 'payment_method', None)
        if raw is None:
            return None
        if isinstance(raw, PaymentMethod):
            return raw.value
        if isinstance(raw, str):
            return raw
        return str(raw)

    async def _service_ids_by_plan(
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

    async def _product_lines_by_plan(
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

    @staticmethod
    def _to_out(row: UserSubscriptionModel) -> UserSubscriptionOutDTO:
        st = row.status
        st_val: str = st.value if isinstance(st, UserSubscriptionStatus) else str(st)
        return UserSubscriptionOutDTO(
            id=row.id,
            user_id=row.user_id,
            subscription_plan_id=row.subscription_plan_id,
            company_id=row.company_id,
            status=st_val,  # type: ignore[arg-type]
            started_at=row.started_at,
            ended_at=row.ended_at,
            external_subscription_id=row.external_subscription_id,
            payment_at=getattr(row, 'payment_at', None),
            payment_method=UserSubscriptionRepositoryPostgres._payment_method_to_str(  # noqa: SLF001
                row
            ),
            created_at=row.created_at,
            updated_at=row.updated_at,
            is_deleted=row.is_deleted,
        )

    async def create(self, data: UserSubscriptionCreateDTO) -> UserSubscriptionOutDTO:
        try:
            started = data.started_at or datetime.now(timezone.utc)
            row = UserSubscriptionModel(
                user_id=data.user_id,
                subscription_plan_id=data.subscription_plan_id,
                company_id=data.company_id,
                status=_status_for_create(data.status),
                started_at=started,
                ended_at=None,
                external_subscription_id=data.external_subscription_id,
            )
            self.session.add(row)
            await self.session.commit()
            await self.session.refresh(row)
            return self._to_out(row)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error

    async def get_by_id(
        self, subscription_id: UUID, company_id: UUID
    ) -> Optional[UserSubscriptionOutDTO]:
        try:
            q = select(UserSubscriptionModel).where(
                UserSubscriptionModel.id == subscription_id,
                UserSubscriptionModel.company_id == company_id,
                UserSubscriptionModel.is_deleted.is_(False),
            )
            r = await self.session.execute(q)
            row = r.scalar_one_or_none()
            if row is None:
                return None
            return self._to_out(row)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error

    async def has_active_for_plan(
        self, user_id: UUID, subscription_plan_id: UUID, company_id: UUID
    ) -> bool:
        try:
            q = select(UserSubscriptionModel.id).where(
                UserSubscriptionModel.user_id == user_id,
                UserSubscriptionModel.subscription_plan_id == subscription_plan_id,
                UserSubscriptionModel.company_id == company_id,
                UserSubscriptionModel.is_deleted.is_(False),
                UserSubscriptionModel.status == UserSubscriptionStatus.active,
            )
            r = await self.session.execute(q)
            return r.scalar_one_or_none() is not None
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error

    async def has_pending_for_plan(
        self, user_id: UUID, subscription_plan_id: UUID, company_id: UUID
    ) -> bool:
        try:
            q = select(UserSubscriptionModel.id).where(
                UserSubscriptionModel.user_id == user_id,
                UserSubscriptionModel.subscription_plan_id == subscription_plan_id,
                UserSubscriptionModel.company_id == company_id,
                UserSubscriptionModel.is_deleted.is_(False),
                UserSubscriptionModel.status == UserSubscriptionStatus.pending_payment,
            )
            r = await self.session.execute(q)
            return r.scalar_one_or_none() is not None
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error

    async def list_by_user(
        self,
        pagination: PaginationParamsDTO,
        company_id: UUID,
        user_id: UUID,
    ) -> List[UserSubscriptionWithPlanOutDTO]:
        try:
            q = (
                select(
                    UserSubscriptionModel,
                    SubscriptionPlan.name,
                    SubscriptionPlan.price,
                    SubscriptionPlan.description,
                    SubscriptionPlan.uses_per_month,
                )
                .join(
                    SubscriptionPlan,
                    UserSubscriptionModel.subscription_plan_id == SubscriptionPlan.id,
                )
                .where(
                    UserSubscriptionModel.user_id == user_id,
                    UserSubscriptionModel.company_id == company_id,
                    UserSubscriptionModel.is_deleted.is_(False),
                )
                .order_by(UserSubscriptionModel.created_at.desc())
            )
            q = q.offset(pagination.offset).limit(pagination.limit)
            r = await self.session.execute(q)
            raw_rows = r.all()
            plan_ids = list({t[0].subscription_plan_id for t in raw_rows})
            s_map = await self._service_ids_by_plan(plan_ids)
            pl_map = await self._product_lines_by_plan(plan_ids)
            out: List[UserSubscriptionWithPlanOutDTO] = []
            for us, p_name, p_price, p_desc, p_uses in raw_rows:
                pid = us.subscription_plan_id
                base = self._to_out(us).model_dump()
                base['plan_name'] = p_name
                base['plan_price'] = p_price
                base['plan_description'] = p_desc
                base['service_ids'] = s_map.get(pid, [])
                base['plan_product_lines'] = pl_map.get(pid, [])
                base['plan_uses_per_month'] = p_uses
                out.append(UserSubscriptionWithPlanOutDTO.model_validate(base))
            return out
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error

    async def list_pending_by_company(
        self,
        pagination: PaginationParamsDTO,
        company_id: UUID,
        client_name: str | None = None,
    ) -> List[UserSubscriptionWithPlanAndClientOutDTO]:
        try:
            q = (
                select(
                    UserSubscriptionModel,
                    SubscriptionPlan.name,
                    SubscriptionPlan.price,
                    SubscriptionPlan.description,
                    SubscriptionPlan.uses_per_month,
                    User.name,
                )
                .join(
                    SubscriptionPlan,
                    UserSubscriptionModel.subscription_plan_id == SubscriptionPlan.id,
                )
                .join(User, UserSubscriptionModel.user_id == User.id)
                .where(
                    UserSubscriptionModel.company_id == company_id,
                    UserSubscriptionModel.is_deleted.is_(False),
                    UserSubscriptionModel.status
                    == UserSubscriptionStatus.pending_payment,
                )
            )
            if client_name and client_name.strip():
                like = f'%{client_name.strip()}%'
                q = q.where(User.name.ilike(like))
            q = (
                q
                .order_by(UserSubscriptionModel.created_at.desc())
                .offset(pagination.offset)
                .limit(pagination.limit)
            )
            r = await self.session.execute(q)
            raw_rows = r.all()
            plan_ids = list({t[0].subscription_plan_id for t in raw_rows})
            s_map = await self._service_ids_by_plan(plan_ids)
            pl_map = await self._product_lines_by_plan(plan_ids)
            out: List[UserSubscriptionWithPlanAndClientOutDTO] = []
            for us, p_name, p_price, p_desc, p_uses, c_name in raw_rows:
                pid = us.subscription_plan_id
                base = self._to_out(us).model_dump()
                base['plan_name'] = p_name
                base['plan_price'] = p_price
                base['plan_description'] = p_desc
                base['service_ids'] = s_map.get(pid, [])
                base['plan_product_lines'] = pl_map.get(pid, [])
                base['plan_uses_per_month'] = p_uses
                base['client_name'] = c_name
                out.append(UserSubscriptionWithPlanAndClientOutDTO.model_validate(base))
            return out
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error

    async def activate_pending(
        self,
        subscription_id: UUID,
        company_id: UUID,
        *,
        external_subscription_id: str | None = None,
        payment_method: str,
        payment_at: datetime | None = None,
    ) -> Optional[UserSubscriptionOutDTO]:
        try:
            paid_at = payment_at or datetime.now(timezone.utc)
            values: dict = {
                'status': UserSubscriptionStatus.active,
                'started_at': paid_at,
                'payment_at': paid_at,
                'payment_method': PaymentMethod(payment_method),
            }
            if external_subscription_id is not None:
                values['external_subscription_id'] = external_subscription_id
            stmt = (
                update(UserSubscriptionModel)
                .where(
                    UserSubscriptionModel.id.__eq__(subscription_id),
                    UserSubscriptionModel.company_id.__eq__(company_id),
                    UserSubscriptionModel.is_deleted.is_(False),
                    UserSubscriptionModel.status.__eq__(
                        UserSubscriptionStatus.pending_payment
                    ),
                )
                .values(**values)
                .returning(UserSubscriptionModel)
            )
            r = await self.session.execute(stmt)
            await self.session.commit()
            row = r.scalar_one_or_none()
            if row is None:
                return None
            return self._to_out(row)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error
