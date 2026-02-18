from http import HTTPStatus

from src.core.exceptions.custom import DomainException


class CompanyAlreadyExistsException(DomainException):
    """Raised when a company already exists."""

    status_code: int = HTTPStatus.CONFLICT.value
    code: str = 'COMPANY_ALREADY_EXISTS'
    message: str


class CompanyNotFoundException(DomainException):
    """Raised when a company is not found."""

    status_code: int = HTTPStatus.NOT_FOUND.value
    code: str = 'COMPANY_NOT_FOUND'
    message: str
