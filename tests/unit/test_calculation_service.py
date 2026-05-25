from backend.services.calculation_service import run_full_calculation


def _request(calculation_mode="uop_to_b2b"):
    return {
        "b2b": {
            "monthly_invoice_amount": 20000,
            "monthly_business_costs": 500,
            "zus_type": "full",
            "sickness_insurance": False,
            "tax_form": "lump_sum_it",
            "vacation_days": 0,
            "sick_days": 0,
            "stoppage_months": 0,
            "age": 30,
            "customBenefits": 0,
            "companyBenefits": {},
        },
        "uop": {
            "monthly_gross_salary": 15000,
            "deductible_cost_settings": {"type": "standard", "creative_work_percentage": 0},
            "selected_benefits": [],
            "age": 30,
            "youth_relief": False,
        },
        "calculation_mode": calculation_mode,
        "language": "pl",
    }


def test_run_full_calculation_returns_api_shape_for_uop_to_b2b():
    result = run_full_calculation(_request())

    assert "b2b_results" in result
    assert "uop_results" in result
    assert "break_even_invoice_amount" in result
    assert "pension_limits_2026" in result
    assert result["analysis"]["summary"]


def test_run_full_calculation_returns_uop_break_even_for_b2b_to_uop():
    result = run_full_calculation(_request("b2b_to_uop"))

    assert "break_even_gross_salary" in result
    assert "break_even_invoice_amount" not in result
