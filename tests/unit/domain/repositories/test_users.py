from uuid import UUID

import pytest
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.users import UpdateUserDTO, UserBaseDTO, UserOutDTO
from src.domain.repositories.users import UsersRepository


@pytest.mark.unit
class TestUsersRepository:
    """Testa o contrato do repositório de usuários (interface abstrata)."""

    def test_repository_has_required_abstract_methods(self):
        assert hasattr(UsersRepository, 'list_users')
        assert hasattr(UsersRepository, 'get_user')
        assert hasattr(UsersRepository, 'create_user')
        assert hasattr(UsersRepository, 'update_user')
        assert hasattr(UsersRepository, 'delete_user')

    def test_concrete_implementation_can_be_subclassed(self):
        class ConcreteUsersRepo(UsersRepository):
            async def list_users(
                self, pagination: PaginationParamsDTO
            ) -> list[UserOutDTO]:
                return []

            async def get_user(self, id: UUID) -> UserOutDTO | None:
                return None

            async def create_user(self, user: UserBaseDTO) -> UserOutDTO:
                raise NotImplementedError

            async def update_user(
                self, id: UUID, user: UpdateUserDTO
            ) -> UserOutDTO | None:
                return None

            async def delete_user(self, id: UUID) -> bool | None:
                return None

        repo = ConcreteUsersRepo()
        assert isinstance(repo, UsersRepository)
