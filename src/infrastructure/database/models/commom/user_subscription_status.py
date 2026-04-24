from enum import Enum


class UserSubscriptionStatus(Enum):
    """
    Status da assinatura do usuário a um plano (catálogo).
    """

    pending_payment = 'PENDING_PAYMENT'
    active = 'ACTIVE'
    canceled = 'CANCELED'
    expired = 'EXPIRED'
