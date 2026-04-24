from enum import Enum


class UserSubscriptionStatus(Enum):
    """
    Status da assinatura do usuário a um plano (catálogo).
    """

    active = 'ACTIVE'
    canceled = 'CANCELED'
    expired = 'EXPIRED'
