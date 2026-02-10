from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError
from src.domain.dtos.auth import EmployeeAuthDTO
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.employee import EmployeeBaseDTO, EmployeeOutDTO, UpdateEmployeeDTO
from src.domain.repositories.employee import EmployeeRepository


@pytest.mark.unit
class TestEmployeeRepositoryContract:
    def test_employee_repository_exposes_contract_methods(self):
        assert hasattr(EmployeeRepository, 'list_employees')
        assert hasattr(EmployeeRepository, 'create_employee')
        assert hasattr(EmployeeRepository, 'get_employee')
        assert hasattr(EmployeeRepository, 'get_employee_auth_by_phone')
        assert hasattr(EmployeeRepository, 'update_employee')
        assert hasattr(EmployeeRepository, 'delete_employee')

        # Mesmo sem herdar de ABC, os métodos marcados com @abstractmethod
        # devem manter o flag __isabstractmethod__ (contrato hexagonal).
        assert getattr(EmployeeRepository.list_employees, '__isabstractmethod__', False)
        assert getattr(
            EmployeeRepository.create_employee, '__isabstractmethod__', False
        )
        assert getattr(EmployeeRepository.get_employee, '__isabstractmethod__', False)
        assert getattr(
            EmployeeRepository.get_employee_auth_by_phone, '__isabstractmethod__', False
        )
        assert getattr(
            EmployeeRepository.update_employee, '__isabstractmethod__', False
        )
        assert getattr(
            EmployeeRepository.delete_employee, '__isabstractmethod__', False
        )

    async def test_can_implement_concrete_repository(self):
        now = datetime.now(timezone.utc)
        employee_id = uuid4()
        company_id = uuid4()

        base = EmployeeBaseDTO(
            name='John',
            last_name='Doe',
            phone='11999999999',
            password='plain',
            is_active=True,
            role='admin',
            company_id=company_id,
        )
        out = EmployeeOutDTO(
            id=employee_id,
            name=base.name,
            last_name=base.last_name,
            phone=base.phone,
            password='hashed',
            is_active=base.is_active,
            role=base.role,
            company_id=company_id,
            created_at=now,
            updated_at=now,
        )

        class ConcreteEmployeeRepository(EmployeeRepository):
            async def list_employees(
                self, pagination: PaginationParamsDTO, company_id: UUID
            ) -> list[EmployeeOutDTO]:
                return [out]

            async def create_employee(
                self, employee: EmployeeBaseDTO
            ) -> EmployeeOutDTO:
                return out

            async def get_employee(
                self, id: UUID, company_id: UUID
            ) -> EmployeeOutDTO | None:
                if id != employee_id or company_id != base.company_id:
                    return None
                return out

            async def get_employee_auth_by_phone(
                self, phone: str
            ) -> EmployeeAuthDTO | None:
                if phone != base.phone:
                    return None
                return EmployeeAuthDTO(
                    id=employee_id,
                    password='hashed',
                    company_id=company_id,
                )

            async def update_employee(
                self, id: UUID, employee: UpdateEmployeeDTO, company_id: UUID
            ) -> EmployeeOutDTO | None:
                return out if id == employee_id else None

            async def delete_employee(self, id: UUID, company_id: UUID) -> bool | None:
                return id == employee_id

        repo = ConcreteEmployeeRepository()
        result_list = await repo.list_employees(PaginationParamsDTO(), company_id)
        assert result_list == [out]

        created = await repo.create_employee(base)
        assert created == out

        found = await repo.get_employee(employee_id, company_id)
        assert found == out

        updated = await repo.update_employee(
            employee_id, UpdateEmployeeDTO(name='X'), company_id
        )
        assert updated == out

        deleted = await repo.delete_employee(employee_id, company_id)
        assert deleted is True

    def test_filters_are_validated_by_pagination_dto(self):
        # Tratativa de filtros: filter_by precisa ser um campo permitido
        with pytest.raises(ValidationError):
            PaginationParamsDTO(filter_by='email', filter_value='x')
