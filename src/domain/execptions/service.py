from http import HTTPStatus

from src.core.exceptions.custom import DomainException


class ServiceNotFoundException(DomainException):
    """Raised when a service is not found."""

    status_code: int = HTTPStatus.NOT_FOUND.value
    code: str = 'SERVICE_NOT_FOUND'
    message: str
