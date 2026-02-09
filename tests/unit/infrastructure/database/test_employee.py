import pytest
from sqlalchemy import inspect
from src.infrastructure.database.models.employees import Employee


@pytest.mark.unit
class TestEmployeeModel:
    def test_employee_table_name_is_snake_case(self):
        assert Employee.__tablename__ == 'employee'

    def test_employee_has_required_columns(self):
        mapper = inspect(Employee)
        column_names = {c.key for c in mapper.columns}
        assert 'name' in column_names
        assert 'last_name' in column_names
        assert 'phone' in column_names
        assert 'password' in column_names
        assert 'is_active' in column_names
        assert 'company_id' in column_names
        assert 'created_at' in column_names
        assert 'updated_at' in column_names
        assert 'is_deleted' in column_names

    def test_employee_name_column_not_nullable(self):
        mapper = inspect(Employee)
        name_prop = mapper.columns['name']
        assert name_prop.nullable is False

    def test_employee_last_name_column_not_nullable(self):
        mapper = inspect(Employee)
        last_name_prop = mapper.columns['last_name']
        assert last_name_prop.nullable is False

    def test_employee_phone_column_not_nullable(self):
        mapper = inspect(Employee)
        phone_prop = mapper.columns['phone']
        assert phone_prop.nullable is False

    def test_employee_password_column_not_nullable(self):
        mapper = inspect(Employee)
        password_prop = mapper.columns['password']
        assert password_prop.nullable is False

    def test_employee_company_id_column_not_nullable(self):
        mapper = inspect(Employee)
        company_id_prop = mapper.columns['company_id']
        assert company_id_prop.nullable is False
