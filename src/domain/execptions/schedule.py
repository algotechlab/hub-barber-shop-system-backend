from http import HTTPStatus

from src.core.exceptions.custom import DomainException


class ScheduleNotFoundException(DomainException):
    status_code: int = HTTPStatus.NOT_FOUND.value
    code: str = 'SCHEDULE_NOT_FOUND'
    message: str
