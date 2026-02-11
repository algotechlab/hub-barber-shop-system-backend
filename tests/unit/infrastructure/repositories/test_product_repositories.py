from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.product import CreateProductDTO, ProductDTO, UpdateProductDTO
from src.infrastructure.repositories.product_postgres import ProductRepositoryPostgres


@pytest.mark.unit
class TestProductRepositoryPostgres:
    @pytest.fixture
    def mock_session(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repo(self, mock_session):
        return ProductRepositoryPostgres(session=mock_session)

    async def test_create_product_success(self, repo, mock_session):
        company_id = uuid4()
        dto = CreateProductDTO(
            name='Produto',
            description='Desc',
            price=Decimal('10'),
            category='Cat',
            status=True,
            url_image='https://example.com/a.png',
            company_id=company_id,
        )
        now = datetime.now(timezone.utc)
        mock_orm = MagicMock()
        mock_orm.id = uuid4()
        mock_orm.name = dto.name
        mock_orm.description = dto.description
        mock_orm.price = dto.price
        mock_orm.category = dto.category
        mock_orm.status = dto.status
        mock_orm.url_image = dto.url_image
        mock_orm.company_id = dto.company_id
        mock_orm.created_at = now
        mock_orm.updated_at = now
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        with patch(
            'src.infrastructure.repositories.product_postgres.Product',
            return_value=mock_orm,
        ):
            result = await repo.create_product(dto)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once()
        assert isinstance(result, ProductDTO)
        assert result.company_id == company_id

    async def test_create_product_rollback_on_error(self, repo, mock_session):
        mock_session.add = MagicMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()
        dto = CreateProductDTO(
            name='Produto',
            description='Desc',
            price=Decimal('10'),
            category='Cat',
            status=True,
            url_image='https://example.com/a.png',
            company_id=uuid4(),
        )

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.create_product(dto)

        mock_session.rollback.assert_awaited_once()

    async def test_get_product_returns_none_when_not_found(self, repo, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_product(uuid4(), uuid4())

        assert result is None

    async def test_get_product_success(self, repo, mock_session):
        mock_orm = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_orm
        mock_session.execute = AsyncMock(return_value=mock_result)

        expected = MagicMock()
        with patch.object(ProductDTO, 'model_validate', return_value=expected) as mv:
            result = await repo.get_product(uuid4(), uuid4())

        mv.assert_called_once_with(mock_orm)
        assert result == expected

    async def test_get_product_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.get_product(uuid4(), uuid4())

        mock_session.rollback.assert_awaited_once()

    async def test_list_products_success(self, repo, mock_session):
        mock_orm_products = [MagicMock(), MagicMock()]
        mock_scalar_result = MagicMock()
        mock_scalar_result.all.return_value = mock_orm_products
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalar_result
        mock_session.execute = AsyncMock(return_value=mock_result)

        expected = [MagicMock(), MagicMock()]
        with patch.object(ProductDTO, 'model_validate', side_effect=expected) as mv:
            result = await repo.list_products(uuid4())

        assert result == expected
        assert mv.call_count == len(mock_orm_products)

    async def test_list_products_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.list_products(uuid4())

        mock_session.rollback.assert_awaited_once()

    async def test_update_product_returns_none_when_not_found(self, repo, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        result = await repo.update_product(uuid4(), UpdateProductDTO(name='X'), uuid4())

        assert result is None
        mock_session.commit.assert_awaited_once()

    async def test_update_product_success(self, repo, mock_session):
        mock_updated = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_updated
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        expected = MagicMock()
        with patch.object(ProductDTO, 'model_validate', return_value=expected) as mv:
            result = await repo.update_product(
                uuid4(), UpdateProductDTO(name='Updated'), uuid4()
            )

        mock_session.commit.assert_awaited_once()
        mv.assert_called_once_with(mock_updated)
        assert result == expected

    async def test_update_product_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.update_product(
                uuid4(), UpdateProductDTO(name='Updated'), uuid4()
            )

        mock_session.rollback.assert_awaited_once()

    async def test_delete_product_returns_true_when_rowcount_positive(
        self, repo, mock_session
    ):
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        result = await repo.delete_product(uuid4(), uuid4())

        assert result is True
        mock_session.commit.assert_awaited_once()

    async def test_delete_product_returns_false_when_rowcount_zero(
        self, repo, mock_session
    ):
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        result = await repo.delete_product(uuid4(), uuid4())

        assert result is False

    async def test_delete_product_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.delete_product(uuid4(), uuid4())

        mock_session.rollback.assert_awaited_once()
