import pytest
from src.pension_calculator import calculate_pension_details

def test_calculate_pension_details_12k_positive():
    """Test dla pensji UoP 12 000 zł (2026)."""
    pension_details = calculate_pension_details(12000)
    assert pension_details is not None
    # Emerytura UoP: ~3833, Emerytura B2B: ~1805, Gap: ~2027
    assert pytest.approx(pension_details.get("pension_gap_monthly"), 0.1) == 2027.67

def test_calculate_pension_details_25k_positive():
    """Test dla pensji UoP 25 000 zł (2026)."""
    pension_details = calculate_pension_details(25000)
    assert pension_details is not None
    # Gap przy 25k brutto wynosi 6180.10
    assert pytest.approx(pension_details.get("pension_gap_monthly"), 0.1) == 6180.10

def test_calculate_pension_details_zero_salary_negative():
    pension_details = calculate_pension_details(0)
    assert pension_details == {}

def test_calculate_pension_details_savings_allocation_positive():
    pension_details = calculate_pension_details(20000)
    allocation = pension_details.get("savings_allocation", {})
    required_savings = pension_details.get("required_monthly_savings", 0)
    assert pytest.approx(allocation.get("ike", 0) + allocation.get("ikze", 0) + allocation.get("standard", 0)) == required_savings
    # IKE limit 2026 is 28260 -> monthly 2355
    assert allocation.get("ike") <= 2355.1

def test_calculate_pension_details_negative_salary_negative():
    assert calculate_pension_details(-1000) == {}

def test_calculate_pension_details_none_salary_negative():
    assert calculate_pension_details(None) == {}
