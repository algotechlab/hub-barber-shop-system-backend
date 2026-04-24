from datetime import datetime, timezone
from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.user_subscription import (
    UserSubscriptionCreateDTO,
    UserSubscriptionOutDTO,
    UserSubscriptionWithPlanOutDTO,
)
from src.domain.repositories.user_subscription import UserSubscriptionRepository
from src.infrastructure.database.models.commom.user_subscription_status import (
    UserSubscriptionStatus,
)
from src.infrastructure.database.models.subscription_plan import SubscriptionPlan
from src.infrastructure.database.models.user_subscription import (
    UserSubscription as UserSubscriptionModel,
)


class UserSubscriptionRepositoryPostgres(UserSubscriptionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

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
                status=UserSubscriptionStatus.active,
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
                    SubscriptionPlan.service_id,
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
            out: List[UserSubscriptionWithPlanOutDTO] = []
            for us, p_name, p_price, s_id, p_uses in r.all():
                base = self._to_out(us).model_dump()
                base['plan_name'] = p_name
                base['plan_price'] = p_price
                base['service_id'] = s_id
                base['plan_uses_per_month'] = p_uses
                out.append(UserSubscriptionWithPlanOutDTO.model_validate(base))
            return out
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error
