from http import HTTPStatus

from src.core.exceptions.custom import DomainException


class CashRegisterOpenSessionExistsException(DomainException):
    status_code: int = HTTPStatus.CONFLICT.value
    code: str = 'CASH_REGISTER_OPEN_EXISTS'
    message: str = 'Já existe um caixa aberto para esta empresa.'


class CashRegisterSessionNotFoundException(DomainException):
    status_code: int = HTTPStatus.NOT_FOUND.value
    code: str = 'CASH_REGISTER_NOT_FOUND'
    message: str


class CashRegisterNoOpenSessionException(DomainException):
    status_code: int = HTTPStatus.NOT_FOUND.value
    code: str = 'CASH_REGISTER_NO_OPEN_SESSION'
    message: str = 'Não há caixa aberto para esta empresa.'


class CashRegisterSessionAlreadyClosedException(DomainException):
    status_code: int = HTTPStatus.BAD_REQUEST.value
    code: str = 'CASH_REGISTER_ALREADY_CLOSED'
    message: str = 'Este turno de caixa já está fechado.'


class CashRegisterSessionClosedException(DomainException):
    status_code: int = HTTPStatus.BAD_REQUEST.value
    code: str = 'CASH_REGISTER_SESSION_CLOSED'
    message: str = 'Não é possível lançar ajustes em um caixa fechado.'
