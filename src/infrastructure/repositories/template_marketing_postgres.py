from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.marketing import TemplateMarketingRecordDTO
from src.domain.repositories.template_marketing import TemplateMarketingRepository
from src.infrastructure.database.models.template_marketing import TemplateMarketingModel

_DEFAULT_NAME = 'Mensagem marketing'
_DEFAULT_DESCRIPTION = 'Template de mensagem para campanhas WhatsApp'


class TemplateMarketingRepositoryPostgres(TemplateMarketingRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_active_for_company(
        self, company_id: UUID
    ) -> TemplateMarketingRecordDTO | None:
        try:
            query = (
                select(TemplateMarketingModel)
                .where(
                    TemplateMarketingModel.company_id.__eq__(company_id),
                    TemplateMarketingModel.is_deleted.__eq__(False),
                    TemplateMarketingModel.is_active.__eq__(True),
                )
                .order_by(TemplateMarketingModel.updated_at.desc())
                .limit(1)
            )
            result = await self.session.execute(query)
            row = result.scalar_one_or_none()
            if row is None:
                return None
            return TemplateMarketingRecordDTO(
                id=row.id,
                company_id=row.company_id,
                name=row.name,
                description=row.description,
                context_template=dict(row.context_template or {}),
                is_active=row.is_active,
            )
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def get_latest_for_company(
        self, company_id: UUID
    ) -> TemplateMarketingRecordDTO | None:
        try:
            query = (
                select(TemplateMarketingModel)
                .where(
                    TemplateMarketingModel.company_id.__eq__(company_id),
                    TemplateMarketingModel.is_deleted.__eq__(False),
                )
                .order_by(TemplateMarketingModel.updated_at.desc())
                .limit(1)
            )
            result = await self.session.execute(query)
            row = result.scalar_one_or_none()
            if row is None:
                return None
            return TemplateMarketingRecordDTO(
                id=row.id,
                company_id=row.company_id,
                name=row.name,
                description=row.description,
                context_template=dict(row.context_template or {}),
                is_active=row.is_active,
            )
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def upsert_default_template(
        self, company_id: UUID, template_text: str
    ) -> TemplateMarketingRecordDTO:
        try:
            existing = await self.get_latest_for_company(company_id)
            payload = {'template': template_text}
            if existing:
                query = select(TemplateMarketingModel).where(
                    TemplateMarketingModel.id == existing.id
                )
                result = await self.session.execute(query)
                row = result.scalar_one()
                row.context_template = payload
                row.name = _DEFAULT_NAME
                row.description = _DEFAULT_DESCRIPTION
                row.is_active = True
            else:
                row = TemplateMarketingModel(
                    company_id=company_id,
                    name=_DEFAULT_NAME,
                    description=_DEFAULT_DESCRIPTION,
                    context_template=payload,
                    is_active=True,
                )
                self.session.add(row)
            await self.session.commit()
            await self.session.refresh(row)
            return TemplateMarketingRecordDTO(
                id=row.id,
                company_id=row.company_id,
                name=row.name,
                description=row.description,
                context_template=dict(row.context_template or {}),
                is_active=row.is_active,
            )
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))
