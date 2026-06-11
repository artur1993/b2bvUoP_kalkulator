from backend.domain.rounding import round_tax


def test_round_tax_half_up_positive():
    assert round_tax(100.49) == 100
    assert round_tax(100.50) == 101
    assert round_tax(0.50) == 1
    assert round_tax(0.49) == 0


def test_round_tax_is_not_bankers_rounding_neutral():
    # Wbudowane round(2.5) == 2 (banker's rounding) — art. 63 §1 Ordynacji
    # wymaga podwyższenia końcówki ≥ 50 gr do pełnego złotego.
    assert round_tax(2.5) == 3
    assert round_tax(3.5) == 4
