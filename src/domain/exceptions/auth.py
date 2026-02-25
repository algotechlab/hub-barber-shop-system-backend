from http import HTTPStatus

from src.core.exceptions.custom import DomainException


class UnauthorizedException(DomainException):
    status_code: int = HTTPStatus.UNAUTHORIZED.value
    code: str = 'UNAUTHORIZED'
    message: str


class InvalidCredentialsException(DomainException):
    status_code: int = HTTPStatus.UNAUTHORIZED.value
    code: str = 'INVALID_CREDENTIALS'
    message: str
