import pytest
from src.interface.api.v1.dependencies.common.headers import OwnerIdHeaderDep

pytestmark = pytest.mark.unit


def test_owner_id_header_dep_is_defined():
    assert OwnerIdHeaderDep is not None
