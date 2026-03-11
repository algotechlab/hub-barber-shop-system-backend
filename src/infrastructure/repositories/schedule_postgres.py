import math
from datetime import date, datetime, time, timedelta
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.schedule import (
    CloseScheduleDTO,
    ScheduleCreateDTO,
    ScheduleFinanceOutDTO,
    ScheduleOutDTO,
    ScheduleUpdateDTO,
    SlotOutDTO,
    SlotsInDTO,
)
from src.domain.repositories.schedule import ScheduleRepository
from src.infrastructure.database.models.employees import Employee
from src.infrastructure.database.models.product import Product
from src.infrastructure.database.models.schedule import Schedule
from src.infrastructure.database.models.schedule_block import ScheduleBlock
from src.infrastructure.database.models.schedule_finance import ScheduleFinance
from src.infrastructure.database.models.service import Service
from src.infrastructure.database.models.users import User


class ScheduleRepositoryPostgres(ScheduleRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _apply_target_date(
        base_datetime: datetime, target_date: Optional[date]
    ) -> datetime:
        if target_date is None:
            return base_datetime

        tzinfo = base_datetime.tzinfo
        target_time = time(
            base_datetime.hour,
            base_datetime.minute,
            base_datetime.second,
            base_datetime.microsecond,
        )
        return datetime.combine(target_date, target_time, tzinfo=tzinfo)

    async def create_schedule(self, schedule: ScheduleCreateDTO) -> ScheduleOutDTO:
        try:
            schedule = Schedule(**schedule.model_dump())
            self.session.add(schedule)
            await self.session.commit()
            await self.session.refresh(schedule)
            return ScheduleOutDTO.model_validate(schedule)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def list_schedules(
        self,
        pagination: PaginationParamsDTO,
        company_id: UUID,
        employee_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
    ) -> List[ScheduleOutDTO]:
        try:
            schedule_ids_query = (
                select(Schedule.id)
                .where(
                    Schedule.is_deleted.__eq__(False),
                    Schedule.company_id.__eq__(company_id),
                )
                .order_by(Schedule.created_at.desc())
            )

            if employee_id is not None:
                schedule_ids_query = schedule_ids_query.where(
                    Schedule.employee_id.__eq__(employee_id)
                )

            if user_id is not None:
                schedule_ids_query = schedule_ids_query.where(
                    Schedule.user_id.__eq__(user_id)
                )

            schedule_ids_query = schedule_ids_query.offset(pagination.offset).limit(
                pagination.limit
            )
            paginated_schedule_ids = schedule_ids_query.subquery()

            query = (
                select(
                    Schedule,
                    User.name.label('user_name'),
                    Employee.name.label('employee_name'),
                    Service.name.label('service_name'),
                    Product.name.label('product_name'),
                    Service.duration.label('service_duration_minutes'),
                )
                .outerjoin(
                    User,
                    Schedule.user_id.__eq__(User.id),
                )
                .outerjoin(
                    Employee,
                    Schedule.employee_id.__eq__(Employee.id),
                )
                .outerjoin(
                    Service,
                    Schedule.service_id.__eq__(Service.id),
                )
                .outerjoin(
                    Product,
                    Schedule.product_id.__eq__(Product.id),
                )
                .where(
                    Schedule.id.in_(select(paginated_schedule_ids.c.id)),
                )
                .order_by(Schedule.created_at.desc())
            )
            result = await self.session.execute(query)
            rows = result.all()

            enriched_schedules: List[ScheduleOutDTO] = []
            for (
                schedule,
                user_name,
                employee_name,
                service_name,
                product_name,
                service_duration_minutes,
            ) in rows:
                schedule_out = ScheduleOutDTO.model_validate(schedule)
                schedule_out.user_name = user_name
                schedule_out.employee_name = employee_name
                schedule_out.service_name = service_name
                schedule_out.product_name = product_name
                if (
                    isinstance(service_duration_minutes, int)
                    and service_duration_minutes > 0
                ):
                    schedule_out.schedule_duration_minutes = service_duration_minutes
                elif schedule.time_start is not None and schedule.time_end is not None:
                    duration_seconds = (
                        schedule.time_end - schedule.time_start
                    ).total_seconds()
                    if duration_seconds > 0:
                        schedule_out.schedule_duration_minutes = math.ceil(
                            duration_seconds / 60
                        )
                    else:
                        schedule_out.schedule_duration_minutes = None
                else:
                    schedule_out.schedule_duration_minutes = None
                enriched_schedules.append(schedule_out)

            return enriched_schedules
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def get_schedule_by_user_id(
        self, pagination: PaginationParamsDTO, company_id: UUID, user_id: UUID
    ) -> List[ScheduleOutDTO]:
        try:
            return await self.list_schedules(
                pagination=pagination,
                company_id=company_id,
                employee_id=None,
                user_id=user_id,
            )
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def get_slots(self, slots: SlotsInDTO) -> List[SlotOutDTO]:
        try:
            effective_work_start = self._apply_target_date(
                slots.work_start, slots.target_date
            )
            effective_work_end = self._apply_target_date(
                slots.work_end, slots.target_date
            )

            query = select(Schedule).where(
                Schedule.company_id.__eq__(slots.company_id),
                Schedule.employee_id.__eq__(slots.employee_id),
                Schedule.is_deleted.__eq__(False),
                Schedule.is_canceled.__eq__(False),
                Schedule.time_start.__lt__(effective_work_end),
                Schedule.time_end.__gt__(effective_work_start),
            )
            result = await self.session.execute(query)
            booked_schedules = result.scalars().all()

            slot_delta = timedelta(minutes=slots.slot_minutes)
            current = effective_work_start
            generated_slots: List[SlotOutDTO] = []

            while current + slot_delta <= effective_work_end:
                slot_end = current + slot_delta
                is_blocked = any(
                    schedule.time_start < slot_end and schedule.time_end > current
                    for schedule in booked_schedules
                )
                generated_slots.append(
                    SlotOutDTO(
                        id=uuid4(),
                        time_start=current,
                        time_end=slot_end,
                        is_available=not is_blocked,
                        is_blocked=is_blocked,
                    )
                )
                current = slot_end

            return generated_slots
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def get_schedule(
        self, id: UUID, company_id: UUID
    ) -> Optional[ScheduleOutDTO]:
        try:
            query = select(Schedule).where(
                Schedule.id.__eq__(id),
                Schedule.is_deleted.__eq__(False),
                Schedule.company_id.__eq__(company_id),
            )
            result = await self.session.execute(query)
            schedule = result.scalar_one_or_none()
            if schedule is None:
                return None
            return ScheduleOutDTO.model_validate(schedule)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def block_schedule(self, employee_id: UUID, company_id: UUID) -> None:
        try:
            query = select(ScheduleBlock).where(
                ScheduleBlock.employee_id.__eq__(employee_id),
                ScheduleBlock.company_id.__eq__(company_id),
                ScheduleBlock.is_deleted.__eq__(False),
                ScheduleBlock.is_block.__eq__(True),
            )
            result = await self.session.execute(query)
            block = result.scalar_one_or_none()
            if block is None:
                return None
            return True
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def update_schedule(
        self, id: UUID, schedule: ScheduleUpdateDTO, company_id: UUID
    ) -> Optional[ScheduleOutDTO]:
        try:
            update_data = schedule.model_dump(exclude_unset=True, exclude_none=True)
            query = (
                update(Schedule)
                .where(
                    Schedule.id.__eq__(id),
                    Schedule.is_deleted.__eq__(False),
                    Schedule.company_id.__eq__(company_id),
                )
                .values(**update_data)
                .returning(Schedule)
            )
            result = await self.session.execute(query)
            await self.session.commit()
            updated_schedule = result.scalar_one_or_none()
            if updated_schedule is None:
                return None
            return ScheduleOutDTO.model_validate(updated_schedule)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def delete_schedule(self, id: UUID, company_id: UUID) -> Optional[bool]:
        try:
            query = (
                update(Schedule)
                .where(
                    Schedule.id.__eq__(id),
                    Schedule.is_deleted.__eq__(False),
                    Schedule.company_id.__eq__(company_id),
                )
                .values(is_deleted=True)
                .returning(Schedule)
            )
            result = await self.session.execute(query)
            await self.session.commit()
            updated_schedule = result.scalar_one_or_none()
            if updated_schedule is None:
                return None
            return True
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def list_schedule_history(self, company_id: UUID) -> List[ScheduleOutDTO]:
        try:
            query = (
                select(Schedule)
                .where(
                    Schedule.company_id.__eq__(company_id),
                    Schedule.is_deleted.__eq__(False),
                )
                .order_by(Schedule.created_at.desc())
            )
            result = await self.session.execute(query)
            schedules = result.scalars().all()
            return [ScheduleOutDTO.model_validate(schedule) for schedule in schedules]
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def close_schedule(
        self, close_schedule: CloseScheduleDTO
    ) -> Optional[ScheduleFinanceOutDTO]:
        try:
            existing_query = select(ScheduleFinance).where(
                ScheduleFinance.schedule_id.__eq__(close_schedule.schedule_id),
                ScheduleFinance.company_id.__eq__(close_schedule.company_id),
                ScheduleFinance.is_deleted.__eq__(False),
            )
            existing_result = await self.session.execute(existing_query)
            existing_schedule_finance = existing_result.scalar_one_or_none()
            if existing_schedule_finance is not None:
                return None

            schedule_finance = ScheduleFinance(**close_schedule.model_dump())
            self.session.add(schedule_finance)
            await self.session.commit()
            await self.session.refresh(schedule_finance)
            return ScheduleFinanceOutDTO.model_validate(schedule_finance)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))
