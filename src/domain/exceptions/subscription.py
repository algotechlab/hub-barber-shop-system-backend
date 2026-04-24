from http import HTTPStatus

from src.core.exceptions.custom import DomainException


class SubscriptionPlanNotFoundException(DomainException):
    status_code: int = HTTPStatus.NOT_FOUND.value
    code: str = 'SUBSCRIPTION_PLAN_NOT_FOUND'


class SubscriptionPlanServiceMismatchException(DomainException):
    """Serviço informado não pertence à mesma empresa do plano."""

    status_code: int = HTTPStatus.BAD_REQUEST.value
    code: str = 'SUBSCRIPTION_PLAN_SERVICE_MISMATCH'


class UserSubscriptionActiveExistsException(DomainException):
    """Já existe assinatura ativa deste plano para o usuário."""

    status_code: int = HTTPStatus.CONFLICT.value
    code: str = 'USER_SUBSCRIPTION_ACTIVE_EXISTS'


class UserSubscriptionNotFoundException(DomainException):
    status_code: int = HTTPStatus.NOT_FOUND.value
    code: str = 'USER_SUBSCRIPTION_NOT_FOUND'
