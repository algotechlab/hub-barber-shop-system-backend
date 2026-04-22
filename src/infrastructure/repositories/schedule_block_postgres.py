from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.schedule_block import (
    ScheduleBlockCreateDTO,
    ScheduleBlockOutDTO,
    ScheduleBlockOutListDTO,
    ScheduleBlockUpdateDTO,
)
from src.domain.repositories.schedule_block import ScheduleBlockRepository
from src.infrastructure.database.models.employees import Employee
from src.infrastructure.database.models.schedule_block import ScheduleBlock


class ScheduleBlockRepositoryPostgres(ScheduleBlockRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_schedule_block(
        self, schedule_block: ScheduleBlockCreateDTO
    ) -> ScheduleBlockOutDTO:
        try:
            payload = schedule_block.model_dump()
            schedule_block_orm = ScheduleBlock(**payload, is_block=True)
            self.session.add(schedule_block_orm)
            await self.session.commit()
            await self.session.refresh(schedule_block_orm)
            return ScheduleBlockOutDTO.model_validate(schedule_block_orm)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def list_schedule_blocks(
        self, company_id: UUID
    ) -> List[ScheduleBlockOutListDTO]:
        try:
            query = (
                select(
                    ScheduleBlock,
                    Employee.id.label('employee_id'),
                    Employee.name.label('employee_name'),
                )
                .outerjoin(
                    Employee,
                    ScheduleBlock.employee_id.__eq__(Employee.id),
                )
                .where(
                    ScheduleBlock.company_id.__eq__(company_id),
                    ScheduleBlock.is_deleted.__eq__(False),
                    ScheduleBlock.is_block.__eq__(True),
                )
            )
            result = await self.session.execute(query)
            schedule_blocks = result.all()
            return [
                ScheduleBlockOutListDTO(
                    id=row.id,
                    employee_id=employee_id or None,
                    employee_name=employee_name or '',
                    start_date=row.start_date,
                    end_date=row.end_date,
                    start_time=row.start_time,
                    end_time=row.end_time,
                    is_block=row.is_block,
                    created_at=row.created_at,
                    updated_at=row.updated_at,
                )
                for row, employee_id, employee_name in schedule_blocks
            ]
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def get_schedule_block(self, id: UUID) -> Optional[ScheduleBlockOutDTO]:
        try:
            query = select(ScheduleBlock).where(ScheduleBlock.id.__eq__(id))
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
            return ScheduleBlockOutDTO.model_validate(updated_schedule_block)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def delete_schedule_block(self, id: UUID) -> bool:
        try:
            query = (
                update(ScheduleBlock)
                .where(ScheduleBlock.id.__eq__(id))
                .values(is_deleted=True)
                .returning(ScheduleBlock)
            )
            result = await self.session.execute(query)
            await self.session.commit()
            return result.scalar_one_or_none() is not None
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))
