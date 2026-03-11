from enum import Enum


class PaymentStatus(Enum):
    pending = 'PENDING'
    paid = 'PAID'
    canceled = 'CANCELED'
    refunded = 'REFUNDED'
