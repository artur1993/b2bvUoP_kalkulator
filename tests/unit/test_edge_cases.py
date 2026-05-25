import pytest

from backend.calculations import calculate_uop_results


def test_author_costs_no_div_by_zero():
    results = calculate_uop_results(
        {
            "monthly_gross_salary": 0,
            "deductible_cost_settings": {"type": "author_50", "creative_work_percentage": 50},
            "youth_relief": False,
            "selected_benefits": [],
        }
    )

    assert results["annual_net_income"] == 0
    assert results["steps"]["annual_deductible_costs"] == 0


def test_author_costs_value_unchanged():
    results = calculate_uop_results(
        {
            "monthly_gross_salary": 10000,
            "deductible_cost_settings": {"type": "author_50", "creative_work_percentage": 70},
            "youth_relief": False,
            "selected_benefits": [],
        }
    )

    assert pytest.approx(results["steps"]["annual_deductible_costs"], 0.01) == 36241.80
