from src.domain.dtos.auth import OwnerLoginDTO
from src.domain.use_case.auth import AuthUseCase
from src.interface.api.v1.schema.auth import OwnerLoginSchema, TokenOutSchema


class AuthController:
    def __init__(self, auth_use_case: AuthUseCase):
        self.auth_use_case = auth_use_case

    async def login_owner(self, credentials: OwnerLoginSchema) -> TokenOutSchema:
        dto = OwnerLoginDTO(**credentials.model_dump())
        token = await self.auth_use_case.login_owner(dto)
        return TokenOutSchema(**token.model_dump())
