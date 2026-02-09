from src.core.security.jwt import create_owner_access_token
from src.core.utils.get_argon import verify_password
from src.domain.dtos.auth import OwnerLoginDTO, TokenDTO
from src.domain.execptions.auth import InvalidCredentialsException
from src.domain.service.owner import OwnerService


class AuthUseCase:
    def __init__(self, owner_service: OwnerService):
        self.owner_service = owner_service

    async def login_owner(self, credentials: OwnerLoginDTO) -> TokenDTO:
        owner = await self.owner_service.get_owner_auth_by_email(credentials.email)
        if owner is None:
            raise InvalidCredentialsException('Credenciais inválidas')

        if not verify_password(owner.password, credentials.password):
            raise InvalidCredentialsException('Credenciais inválidas')

        token = create_owner_access_token(owner.id)
        return TokenDTO(access_token=token)
