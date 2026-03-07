from http import HTTPStatus

from src.core.exceptions.custom import DomainException


class ScheduleBlockNotFoundException(DomainException):
    status_code: int = HTTPStatus.NOT_FOUND.value
    code: str = 'SCHEDULE_BLOCK_NOT_FOUND'
    message: str
