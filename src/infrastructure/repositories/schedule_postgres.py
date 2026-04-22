import math
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from numbers import Number
from typing import List, Optional
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy import Time, cast, func, select, update
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

    @staticmethod
    def _minutes_from_time_range(
        time_start: Optional[datetime], time_end: Optional[datetime]
    ) -> Optional[int]:
        if not isinstance(time_start, datetime) or not isinstance(time_end, datetime):
            return None
        seconds = (time_end - time_start).total_seconds()
        if seconds <= 0:
            return None
        return math.ceil(seconds / 60)

    @classmethod
    def _resolve_schedule_duration_minutes(
        cls,
        time_start: Optional[datetime],
        time_end: Optional[datetime],
        summed_service_duration: object,
    ) -> Optional[int]:
        from_slot = cls._minutes_from_time_range(time_start, time_end)
        if from_slot is not None:
            return from_slot
        if isinstance(summed_service_duration, Number) and summed_service_duration > 0:
            return int(summed_service_duration)
        return None

    @classmethod
    def _schedule_row_to_out_dto(
        cls,
        schedule: Schedule,
        user_name: Optional[str],
        employee_name: Optional[str],
        service_names: Optional[List[str]],
        product_name: Optional[str],
        service_duration_minutes: object,
    ) -> ScheduleOutDTO:
        dto = ScheduleOutDTO.model_validate(schedule)
        dto.user_name = user_name
        dto.employee_name = employee_name
        dto.service_names = service_names
        dto.product_name = product_name
        dto.schedule_duration_minutes = cls._resolve_schedule_duration_minutes(
            schedule.time_start,
            schedule.time_end,
            service_duration_minutes,
        )
        return dto

    async def create_schedule(self, schedule: ScheduleCreateDTO) -> ScheduleOutDTO:
        try:
            row_data = schedule.model_dump()
            row_data['service_id'] = [
                service_id if isinstance(service_id, UUID) else UUID(str(service_id))
                for service_id in row_data['service_id']
            ]
            schedule = Schedule(**row_data)
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
            id_filters = [
                Schedule.is_deleted.__eq__(False),
                Schedule.company_id.__eq__(company_id),
            ]
            if employee_id is not None:
                id_filters.append(Schedule.employee_id.__eq__(employee_id))
            if user_id is not None:
                id_filters.append(Schedule.user_id.__eq__(user_id))

            paginated_schedule_ids = (
                select(Schedule.id)
                .where(*id_filters)
                .order_by(Schedule.created_at.desc())
                .offset(pagination.offset)
                .limit(pagination.limit)
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
                .outerjoin(User, Schedule.user_id.__eq__(User.id))
                .outerjoin(Employee, Schedule.employee_id.__eq__(Employee.id))
                .outerjoin(Product, Schedule.product_id.__eq__(Product.id))
                .where(Schedule.id.in_(select(paginated_schedule_ids.c.id)))
                .order_by(Schedule.created_at.desc())
            )
            result = await self.session.execute(query)
            return [self._schedule_row_to_out_dto(*row) for row in result.all()]
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
            now_time = cast(func.current_timestamp(), Time)
            query = select(ScheduleBlock).where(
                ScheduleBlock.employee_id.__eq__(employee_id),
                ScheduleBlock.company_id.__eq__(company_id),
                ScheduleBlock.is_deleted.__eq__(False),
                ScheduleBlock.is_block.__eq__(True),
                ScheduleBlock.start_date.__le__(func.current_date()),
                ScheduleBlock.end_date.__ge__(func.current_date()),
                ScheduleBlock.start_time.__le__(now_time),
                ScheduleBlock.end_time.__ge__(now_time),
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
            if 'service_id' in update_data:
                update_data['service_id'] = [
                    x if isinstance(x, UUID) else UUID(str(x))
                    for x in update_data['service_id']
                ]
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

    async def sum_sale_for_service_ids(
        self, service_ids: List[UUID], company_id: UUID
    ) -> Optional[Decimal]:
        try:
            if not service_ids:
                return None
            stmt = select(Service).where(
                Service.id.in_(set(service_ids)),
                Service.company_id.__eq__(company_id),
                Service.is_deleted.__eq__(False),
            )
            result = await self.session.execute(stmt)
            rows = list(result.scalars().all())
            by_id = {row.id: row for row in rows}
            total = Decimal('0')
            for sid in service_ids:
                svc = by_id.get(sid)
                if svc is None or not svc.status:
                    return None
                total += Decimal(svc.price)
            return total
        except Exception as error:
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

            schedule_query = select(Schedule).where(
                Schedule.id.__eq__(close_schedule.schedule_id),
                Schedule.company_id.__eq__(close_schedule.company_id),
                Schedule.is_deleted.__eq__(False),
            )
            updated_confirmed = (
                update(Schedule)
                .where(
                    Schedule.id.__eq__(close_schedule.schedule_id),
                    Schedule.company_id.__eq__(close_schedule.company_id),
                    Schedule.is_deleted.__eq__(False),
                )
                .values(is_confirmed=True)
                .returning(Schedule)
            )

            updated_confirmed_result = await self.session.execute(updated_confirmed)

            updated_confirmed_row = updated_confirmed_result.scalar_one_or_none()
            if updated_confirmed_row is None:
                return None

            schedule_result = await self.session.execute(schedule_query)
            schedule_row = schedule_result.scalar_one_or_none()
            if schedule_row is None:
                return None

            finance_payload = close_schedule.model_dump()
            finance_payload['service_id'] = list(schedule_row.service_id)

            schedule_finance = ScheduleFinance(**finance_payload)
            self.session.add(schedule_finance)
            await self.session.commit()
            await self.session.refresh(schedule_finance)
            return ScheduleFinanceOutDTO.model_validate(schedule_finance)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))
