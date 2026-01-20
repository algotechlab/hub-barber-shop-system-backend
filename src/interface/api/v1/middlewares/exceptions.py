from typing import Union

from fastapi import Request, status
from fastapi.responses import JSONResponse

from src.core.exceptions.custom import (
    DomainException,
    InfrastructureException,
    MultipleException,
)
from src.core.utils.get_from_sequence import get_from_sequence


async def custom_exception_handler(
    request: Request,
    exc: Union[DomainException, MultipleException, InfrastructureException, Exception],
) -> JSONResponse:
    if isinstance(exc, MultipleException):
        status_code = getattr(exc, 'status_code', status.HTTP_400_BAD_REQUEST)
        errors = []
        for error in exc.args:
            error_message = get_from_sequence(error.args, 0, '')
            error_field = get_from_sequence(error.args, 1)
            error_code = getattr(error, 'code', 'HTTP_ERROR')
            errors.append({
                'field': error_field,
                'code': error_code,
                'message': error_message,
            })
        return JSONResponse(status_code=status_code, content=errors)
    status_code = getattr(exc, 'status_code', status.HTTP_500_INTERNAL_SERVER_ERROR)
    code = getattr(exc, 'code', 'HTTP_ERROR')
    return JSONResponse(
        status_code=status_code,
        content={
            'code': code,
            'message': str(exc),
        },
    )
