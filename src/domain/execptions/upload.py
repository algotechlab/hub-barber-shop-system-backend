from http import HTTPStatus

from src.core.exceptions.custom import DomainException, InfrastructureException


class InvalidFileTypeException(DomainException):
    status_code: int = HTTPStatus.BAD_REQUEST.value
    code: str = 'INVALID_FILE_TYPE'


class FileTooLargeException(DomainException):
    status_code: int = HTTPStatus.REQUEST_ENTITY_TOO_LARGE.value
    code: str = 'FILE_TOO_LARGE'


class UploadFailedException(InfrastructureException):
    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR.value
    code: str = 'UPLOAD_FAILED'
