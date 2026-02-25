from src.core.security.jwt import create_access_token, create_owner_access_token
from src.core.utils.get_argon import verify_password
from src.domain.dtos.auth import (
    EmployeeLoginDTO,
    OwnerLoginDTO,
    TokenDTO,
    TokenWithCompanyDTO,
    UserLoginDTO,
)
from src.domain.exceptions.auth import InvalidCredentialsException
from src.domain.service.employee import EmployeeService
from src.domain.service.owner import OwnerService
from src.domain.service.users import UsersService


class AuthUseCase:
    def __init__(
        self,
        owner_service: OwnerService,
        employee_service: EmployeeService,
        users_service: UsersService,
    ):
        self.owner_service = owner_service
        self.employee_service = employee_service
        self.users_service = users_service

    async def login_owner(self, credentials: OwnerLoginDTO) -> TokenDTO:
        owner = await self.owner_service.get_owner_auth_by_email(credentials.email)
        if owner is None:
            raise InvalidCredentialsException('Credenciais inválidas')

        if not verify_password(owner.password, credentials.password):
            raise InvalidCredentialsException('Credenciais inválidas')

        token = create_owner_access_token(owner.id)
        return TokenDTO(access_token=token)

    async def login_employee(
        self, credentials: EmployeeLoginDTO
    ) -> TokenWithCompanyDTO:
        employee = await self.employee_service.get_employee_auth_by_phone(
            credentials.phone
        )
        if employee is None:
            raise InvalidCredentialsException('Credenciais inválidas')

        if not verify_password(employee.password, credentials.password):
            raise InvalidCredentialsException('Credenciais inválidas')

        token = create_access_token(
            employee.id, 'employee', company_id=employee.company_id
        )
        return TokenWithCompanyDTO(
            id=employee.id,
            name=employee.name,
            access_token=token,
            company_id=employee.company_id,
        )

    async def login_user(self, credentials: UserLoginDTO) -> TokenWithCompanyDTO:
        user = await self.users_service.get_user_auth_by_phone(credentials.phone)
        if user is None:
            raise InvalidCredentialsException('Credenciais inválidas')

        token = create_access_token(user.id, 'user', company_id=user.company_id)
        return TokenWithCompanyDTO(
            id=user.id,
            name=user.name,
            access_token=token,
            company_id=user.company_id,
        )
