from http import HTTPStatus

from src.core.exceptions.custom import DomainException


class ScheduleNotFoundException(DomainException):
    status_code: int = HTTPStatus.NOT_FOUND.value
    code: str = 'SCHEDULE_NOT_FOUND'
    message: str


class ScheduleAlreadyClosedException(DomainException):
    status_code: int = HTTPStatus.CONFLICT.value
    code: str = 'SCHEDULE_ALREADY_CLOSED'
    message: str


class ScheduleCanceledException(DomainException):
    status_code: int = HTTPStatus.BAD_REQUEST.value
    code: str = 'SCHEDULE_CANCELED'
    message: str


class ScheduleCloseServicesException(DomainException):
    """
    Serviços do agendamento ausentes, inativos ou não pertencentes à empresa.
    """

    status_code: int = HTTPStatus.BAD_REQUEST.value
    code: str = 'SCHEDULE_CLOSE_SERVICES_INVALID'
    message: str


class ScheduleCloseAmountMismatchException(DomainException):
    """amount_service diferente da soma dos preços dos serviços vinculados."""

    status_code: int = HTTPStatus.BAD_REQUEST.value
    code: str = 'SCHEDULE_CLOSE_AMOUNT_MISMATCH'
    message: str
