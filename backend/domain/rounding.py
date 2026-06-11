import math


def round_tax(value: float) -> float:
    """Zaokrąglenie do pełnych złotych wg art. 63 §1 Ordynacji podatkowej.

    Końcówki poniżej 50 groszy pomija się, 50 groszy i więcej podwyższa do
    pełnego złotego (half-up — wbudowane round() stosuje banker's rounding).
    Dotyczy zarówno podstawy opodatkowania, jak i kwoty podatku.
    """
    return float(math.floor(value + 0.5))
