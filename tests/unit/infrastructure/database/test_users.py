import pytest
from sqlalchemy import inspect
from src.infrastructure.database.models.users import User


@pytest.mark.unit
class TestUserModel:
    def test_user_table_name_is_snake_case(self):
        assert User.__tablename__ == 'user'

    def test_user_has_required_columns(self):
        mapper = inspect(User)
        column_names = {c.key for c in mapper.columns}
        assert 'id' in column_names
        assert 'name' in column_names
        assert 'email' in column_names
        assert 'password' in column_names
        assert 'is_active' in column_names
        assert 'company_id' in column_names
        assert 'created_at' in column_names
        assert 'updated_at' in column_names
        assert 'is_deleted' in column_names

    def test_user_name_column_not_nullable(self):
        mapper = inspect(User)
        name_prop = mapper.columns['name']
        assert name_prop.nullable is False

    def test_user_email_column_not_nullable(self):
        mapper = inspect(User)
        email_prop = mapper.columns['email']
        assert email_prop.nullable is False

    def test_user_is_active_has_default(self):
        mapper = inspect(User)
        is_active_prop = mapper.columns['is_active']
        assert is_active_prop.default is not None
