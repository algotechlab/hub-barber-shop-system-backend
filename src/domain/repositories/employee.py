from abc import abstractmethod
from typing import Optional
from uuid import UUID

from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.employee import EmployeeBaseDTO, EmployeeOutDTO, UpdateEmployeeDTO


class EmployeeRepository:
    @abstractmethod
    async def list_employees(
        self, pagination: PaginationParamsDTO
    ) -> list[EmployeeOutDTO]: ...

    @abstractmethod
    async def create_employee(self, employee: EmployeeBaseDTO) -> EmployeeOutDTO: ...

    @abstractmethod
    async def get_employee(self, id: UUID) -> Optional[EmployeeOutDTO]: ...

    @abstractmethod
    async def update_employee(
        self, id: UUID, employee: UpdateEmployeeDTO
    ) -> Optional[EmployeeOutDTO]: ...

    @abstractmethod
    async def delete_employee(self, id: UUID) -> Optional[bool]: ...
