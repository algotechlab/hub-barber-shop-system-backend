from src.domain.dtos.auth import EmployeeLoginDTO, OwnerLoginDTO, UserLoginDTO
from src.domain.use_case.auth import AuthUseCase
from src.interface.api.v1.schema.auth import (
    EmployeeLoginSchema,
    OwnerLoginSchema,
    TokenOutSchema,
    TokenWithCompanyOutSchema,
    UserLoginSchema,
)


class AuthController:
    def __init__(self, auth_use_case: AuthUseCase):
        self.auth_use_case = auth_use_case

    async def login_owner(self, credentials: OwnerLoginSchema) -> TokenOutSchema:
        dto = OwnerLoginDTO(**credentials.model_dump())
        token = await self.auth_use_case.login_owner(dto)
        return TokenOutSchema(**token.model_dump())

    async def login_employee(
        self, credentials: EmployeeLoginSchema
    ) -> TokenWithCompanyOutSchema:
        dto = EmployeeLoginDTO(**credentials.model_dump())
        token = await self.auth_use_case.login_employee(dto)
        return TokenWithCompanyOutSchema(**token.model_dump())

    async def login_user(
        self, credentials: UserLoginSchema
    ) -> TokenWithCompanyOutSchema:
        dto = UserLoginDTO(**credentials.model_dump())
        token = await self.auth_use_case.login_user(dto)
        return TokenWithCompanyOutSchema(**token.model_dump())
