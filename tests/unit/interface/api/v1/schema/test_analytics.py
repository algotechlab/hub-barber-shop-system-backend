from datetime import date

import pytest
from pydantic import ValidationError
from src.interface.api.v1.schema.analytics import DashboardFilterInSchema


@pytest.mark.unit
def test_dashboard_filter_schema_valid_period():
    schema = DashboardFilterInSchema(
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
    )
    assert schema.start_date <= schema.end_date


@pytest.mark.unit
def test_dashboard_filter_schema_invalid_period_raises():
    with pytest.raises(ValidationError):
        DashboardFilterInSchema(
            start_date=date(2026, 2, 1),
            end_date=date(2026, 1, 31),
        )
