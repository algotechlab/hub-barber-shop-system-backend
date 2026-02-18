from http import HTTPStatus

from src.core.exceptions.custom import DomainException


class ProductNotFoundException(DomainException):
    """Raised when a product is not found."""

    status_code: int = HTTPStatus.NOT_FOUND.value
    code: str = 'PRODUCT_NOT_FOUND'
