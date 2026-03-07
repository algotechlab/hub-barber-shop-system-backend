from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.schedule_block import (
    ScheduleBlockCreateDTO,
    ScheduleBlockOutDTO,
    ScheduleBlockUpdateDTO,
)
from src.domain.repositories.schedule_block import ScheduleBlockRepository
from src.infrastructure.database.models.schedule_block import ScheduleBlock


class ScheduleBlockRepositoryPostgres(ScheduleBlockRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_db_naive_utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value
        return value.astimezone(timezone.utc).replace(tzinfo=None)

    async def create_schedule_block(
        self, schedule_block: ScheduleBlockCreateDTO
    ) -> ScheduleBlockOutDTO:
        try:
            payload = schedule_block.model_dump()
            payload['start_time'] = self._to_db_naive_utc(payload['start_time'])
            payload['end_time'] = self._to_db_naive_utc(payload['end_time'])

            schedule_block = ScheduleBlock(**payload)
            self.session.add(schedule_block)
            await self.session.commit()
            await self.session.refresh(schedule_block)
            return ScheduleBlockOutDTO.model_validate(schedule_block)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def get_schedule_block(self, id: UUID) -> Optional[ScheduleBlockOutDTO]:
        try:
            query = select(ScheduleBlock).where(ScheduleBlock.employee_id.__eq__(id))
            result = await self.session.execute(query)
            schedule_block = result.scalar_one_or_none()
            if schedule_block is None:
                return None
            return ScheduleBlockOutDTO.model_validate(schedule_block)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def update_schedule_block(
        self, id: UUID, schedule_block: ScheduleBlockUpdateDTO
    ) -> Optional[ScheduleBlockOutDTO]:
        try:
            update_data = schedule_block.model_dump(
                exclude_unset=True, exclude_none=True
            )
            if 'start_time' in update_data:
                update_data['start_time'] = self._to_db_naive_utc(
                    update_data['start_time']
                )
            if 'end_time' in update_data:
                update_data['end_time'] = self._to_db_naive_utc(update_data['end_time'])
            query = (
                update(ScheduleBlock)
                .where(ScheduleBlock.id.__eq__(id))
                .values(**update_data)
                .returning(ScheduleBlock)
            )
            result = await self.session.execute(query)
            updated_schedule_block = result.scalar_one_or_none()
            if updated_schedule_block is None:
                return None
            await self.session.commit()
            return ScheduleBlockOutDTO.model_validate(result.scalar_one_or_none())
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def delete_schedule_block(self, id: UUID) -> bool:
        try:
            query = (
                update(ScheduleBlock)
                .where(ScheduleBlock.employee_id.__eq__(id))
                .values(is_deleted=True)
                .returning(ScheduleBlock)
            )
            result = await self.session.execute(query)
            await self.session.commit()
            return result.scalar_one_or_none() is not None
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))
