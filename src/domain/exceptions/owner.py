from http import HTTPStatus

from src.core.exceptions.custom import DomainException


class OwnerAlreadyExistsException(DomainException):
    """Raised when an owner already exists."""

    status_code: int = HTTPStatus.CONFLICT.value
    code: str = 'OWNER_ALREADY_EXISTS'
    message: str


class OwnerNotFoundException(DomainException):
    """Raised when an owner is not found."""

    status_code: int = HTTPStatus.NOT_FOUND.value
    code: str = 'OWNER_NOT_FOUND'
    message: str
