import pytest
from src.pension_calculator import calculate_pension_details

def test_calculate_pension_details_12k_positive():
    """Test 1: Dla pensji UoP 12 000 zł, sprawdź, czy invoice_increase wynosi ok. 1302 zł, a pension_gap_monthly ok. 2834 zł."""
    pension_details = calculate_pension_details(12000)
    assert pension_details is not None
    assert isinstance(pension_details, dict)
    assert pytest.approx(pension_details.get("invoice_increase"), 0.1) == 1302.0
    assert pytest.approx(pension_details.get("pension_gap_monthly"), 0.1) == 2834.0

def test_calculate_pension_details_25k_positive():
    """Test 2: Dla pensji UoP 25 000 zł, sprawdź, czy invoice_increase wynosi ok. 3190 zł."""
    pension_details = calculate_pension_details(25000)
    assert pension_details is not None
    assert isinstance(pension_details, dict)
    assert pytest.approx(pension_details.get("invoice_increase"), 0.1) == 3190.0

def test_calculate_pension_details_zero_salary_negative():
    """Test 3: Dla zerowej pensji UoP, sprawdź, czy funkcja zwraca pusty obiekt."""
    pension_details = calculate_pension_details(0)
    assert pension_details == {}

def test_calculate_pension_details_savings_allocation_positive():
    """Test 4: Sprawdź poprawność alokacji oszczędności (IKE/IKZE/Standard) dla różnych kwot."""
    pension_details = calculate_pension_details(20000)
    allocation = pension_details.get("savings_allocation", {})
    required_savings = pension_details.get("required_monthly_savings", 0)
    assert allocation is not None
    assert isinstance(allocation, dict)
    assert pytest.approx(allocation.get("ike", 0) + allocation.get("ikze", 0) + allocation.get("standard", 0)) == required_savings

def test_calculate_pension_details_negative_salary_negative():
    """Test 5: Dla ujemnej pensji UoP, sprawdź, czy funkcja zwraca pusty obiekt."""
    pension_details = calculate_pension_details(-1000)
    assert pension_details == {}

def test_calculate_pension_details_none_salary_negative():
    """Test 6: Dla pensji UoP równej None, sprawdź, czy funkcja zwraca pusty obiekt."""
    pension_details = calculate_pension_details(None)
    assert pension_details == {}