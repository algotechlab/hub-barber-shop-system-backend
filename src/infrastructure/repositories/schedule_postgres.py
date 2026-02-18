from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.schedule import (
    ScheduleCreateDTO,
    ScheduleOutDTO,
    ScheduleUpdateDTO,
)
from src.domain.repositories.schedule import ScheduleRepository
from src.infrastructure.database.models.schedule import Schedule


class ScheduleRepositoryPostgres(ScheduleRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

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
        self, pagination: PaginationParamsDTO, company_id: UUID
    ) -> List[ScheduleOutDTO]:
        try:
            query = select(Schedule).where(
                Schedule.is_deleted.__eq__(False),
                Schedule.company_id.__eq__(company_id),
            )
            result = await self.session.execute(query)
            schedules = result.scalars().all()
            return [ScheduleOutDTO.model_validate(schedule) for schedule in schedules]
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
