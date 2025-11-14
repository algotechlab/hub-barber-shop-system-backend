# src/utils/pagination.py

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple


@dataclass
class PaginationParams:
    current_page: int
    rows_per_page: int
    sort_by: str
    order_by: str
    filter_by: str


class Pagination:
    def __init__(self, params: Optional[Dict[str, Any]] = None):
        self.params = params or {}
        self.default_pagination = {
            "current_page": 1,
            "rows_per_page": 10,
            "sort_by": "asc",
            "order_by": "id",
            "filter_by": "",
        }

    def validate_params(
        self,
    ) -> Tuple[PaginationParams, Optional[Dict[str, Any]]]:
        """Check params and return PaginationParams if valid."""
        try:
            current_page = max(int(self.params.get("current_page", 1)), 1)
            rows_per_page = max(int(self.params.get("rows_per_page", 10)), 1)
            sort_by = self.params.get("sort_by", "asc").lower()
            if sort_by not in ["asc", "desc"]:
                raise ValueError("sort_by must be 'asc' or 'desc'")

            order_by = self.params.get("order_by", "id")
            filter_by = self.params.get("filter_by", "")

            pagination_params = PaginationParams(
                current_page=current_page,
                rows_per_page=rows_per_page,
                sort_by=sort_by,
                order_by=order_by,
                filter_by=filter_by,
            )
            return pagination_params, None
        except ValueError as ve:
            return None, {
                "status_code": 400,
                "data": None,
                "metadata": None,
                "message_id": "invalid_parameters",
                "error": True,
                "exception": str(ve),
            }

    def get_pagination(self) -> Dict[str, Any]:
        """Return default or validated pagination parameters."""
        pagination_params, error = self.validate_params()
        if error:
            return error
        return {
            "current_page": pagination_params.current_page,
            "rows_per_page": pagination_params.rows_per_page,
            "sort_by": pagination_params.sort_by,
            "order_by": pagination_params.order_by,
            "filter_by": pagination_params.filter_by,
        }

    def build_metadata(
        self, total_count: int, params: PaginationParams
    ) -> Dict[str, Any]:
        """Build metadata for the response."""
        return {
            "total_count": total_count,
            "current_page": params.current_page,
            "rows_per_page": params.rows_per_page,
            "total_pages": (total_count + params.rows_per_page - 1)
            // params.rows_per_page,
        }
