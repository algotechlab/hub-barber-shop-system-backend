from abc import abstractmethod
from uuid import UUID

from src.domain.dtos.marketing import TemplateMarketingRecordDTO


class TemplateMarketingRepository:
    @abstractmethod
    async def get_active_for_company(
        self, company_id: UUID
    ) -> TemplateMarketingRecordDTO | None: ...

    @abstractmethod
    async def upsert_default_template(
        self, company_id: UUID, template_text: str
    ) -> TemplateMarketingRecordDTO: ...

    @abstractmethod
    async def get_latest_for_company(
        self, company_id: UUID
    ) -> TemplateMarketingRecordDTO | None: ...
