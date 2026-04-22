from enum import Enum


class CashMovementKind(Enum):
    """Suprimento (entrada manual) ou sangria (saída manual) no caixa."""

    supply = 'SUPPLY'
    withdrawal = 'WITHDRAWAL'
