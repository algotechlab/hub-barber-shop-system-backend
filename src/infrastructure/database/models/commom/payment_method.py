from enum import Enum


class PaymentMethod(Enum):
    credit_card = 'CREDIT_CARD'
    debit_card = 'DEBIT_CARD'
    pix = 'PIX'
    money = 'MONEY'
    other = 'OTHER'
