import pytest
from backend.calculations import calculate_b2b_results, calculate_uop_results


def test_ppk_zero_salary_grants_no_state_subsidy_negative():
    # Dopłata roczna państwa wymaga faktycznych wpłat pracownika — przy zerowej
    # pensji kapitał PPK ma być zerowy, bez "darmowych" 240 zł.
    results = calculate_uop_results(
        {
            "monthly_gross_salary": 0,
            "deductible_cost_settings": {"type": "standard", "creative_work_percentage": 0},
            "youth_relief": False,
            "selected_benefits": ["ppk"],
        }
    )

    assert results["steps"]["annual_ppk_state_subsidy"] == 0
    assert results["annual_ppk_capital"] == 0


def test_author_costs_no_div_by_zero():
    # monthly_gross_salary = 0 + creative_work_percentage > 0
    results = calculate_uop_results(
        {
            "monthly_gross_salary": 0,
            "deductible_cost_settings": {"type": "author_50", "creative_work_percentage": 50},
            "youth_relief": False,
            "selected_benefits": [],
            "age": 30,
        }
    )

    assert results["annual_net_income"] == 0
    assert results["steps"]["annual_deductible_costs"] == 0


def test_b2b_zero_invoice_amount():
    # monthly_invoice_amount = 0 -> business has negative net income due to fixed ZUS
    results = calculate_b2b_results(
        {
            "monthly_invoice_amount": 0,
            "tax_form": "flat_tax",
            "zus_type": "full",
            "sickness_insurance": True,
            "monthly_business_costs": 0,
            "vacation_days": 0,
            "sick_days": 0,
            "stoppage_months": 0,
            "age": 30,
            "customBenefits": 0,
            "companyBenefits": {},
        }
    )
    # Full ZUS 2026 is approx 2349 PLN monthly (social + min health)
    assert results["annual_net_income"] < 0


def test_uop_thirty_times_limit_exactly():
    # Thirty times limit exactly (282600)
    results = calculate_uop_results(
        {
            "monthly_gross_salary": 282600 / 12,
            "deductible_cost_settings": {"type": "standard"},
            "youth_relief": False,
            "selected_benefits": [],
            "age": 30,
        }
    )
    # annual_zus = social + health
    # health = 0.09 * (gross - social)
    # annual_zus = 0.91 * social + 0.09 * gross
    # social = (annual_zus - 0.09 * gross) / 0.91
    gross = 282600
    social = (results["annual_zus"] - 0.09 * gross) / 0.91
    
    expected_social = 282600 * 0.1371 # 0.0976 + 0.0150 + 0.0245
    assert pytest.approx(social, 1.0) == expected_social


def test_uop_thirty_times_limit_plus_one():
    # Thirty times limit + 1 PLN
    results = calculate_uop_results(
        {
            "monthly_gross_salary": (282600 + 1) / 12,
            "deductible_cost_settings": {"type": "standard"},
            "youth_relief": False,
            "selected_benefits": [],
            "age": 30,
        }
    )
    gross = 282601
    social = (results["annual_zus"] - 0.09 * gross) / 0.91
    
    # Pension and disability should stop at 282600. Sickness continues.
    expected_social = (282600 * (0.0976 + 0.0150)) + (282601 * 0.0245)
    assert pytest.approx(social, 1.0) == expected_social


def test_b2b_very_high_amount_solidarity_tax():
    # Solidarity tax kicks in above 1,000,000 PLN annual income
    results = calculate_b2b_results(
        {
            "monthly_invoice_amount": 100000,
            "tax_form": "flat_tax",
            "zus_type": "full",
            "sickness_insurance": True,
            "monthly_business_costs": 0,
            "vacation_days": 0,
            "sick_days": 0,
            "stoppage_months": 0,
            "age": 30,
            "customBenefits": 0,
            "companyBenefits": {},
        }
    )
    assert results["annual_solidarity_tax"] > 0


def test_b2b_lump_sum_health_thresholds():
    # 60k limit
    res_under_60k = calculate_b2b_results({
        "monthly_invoice_amount": 4000, # 48k annual
        "tax_form": "lump_sum_it", "zus_type": "full", "sickness_insurance": True,
        "monthly_business_costs": 0, "vacation_days": 0, "sick_days": 0, "stoppage_months": 0,
        "age": 30, "customBenefits": 0, "companyBenefits": {}
    })
    assert pytest.approx(res_under_60k["steps"]["annual_health_contribution"], 1) == 498.35 * 12

    # 300k limit
    res_under_300k = calculate_b2b_results({
        "monthly_invoice_amount": 10000, # 120k annual
        "tax_form": "lump_sum_it", "zus_type": "full", "sickness_insurance": True,
        "monthly_business_costs": 0, "vacation_days": 0, "sick_days": 0, "stoppage_months": 0,
        "age": 30, "customBenefits": 0, "companyBenefits": {}
    })
    assert pytest.approx(res_under_300k["steps"]["annual_health_contribution"], 1) == 830.58 * 12

    # above 300k
    res_above_300k = calculate_b2b_results({
        "monthly_invoice_amount": 30000, # 360k annual
        "tax_form": "lump_sum_it", "zus_type": "full", "sickness_insurance": True,
        "monthly_business_costs": 0, "vacation_days": 0, "sick_days": 0, "stoppage_months": 0,
        "age": 30, "customBenefits": 0, "companyBenefits": {}
    })
    assert pytest.approx(res_above_300k["steps"]["annual_health_contribution"], 1) == 1495.04 * 12


def test_regression_zus_type_small_business_rejected(client):
    payload = {
        "b2b": {
            "monthly_invoice_amount": 10000, "tax_form": "flat_tax", "zus_type": "small_business",
            "age": 30
        },
        "uop": {
            "monthly_gross_salary": 8000, "deductible_cost_settings": {"type": "standard"}, "age": 30
        },
        "calculation_mode": "uop_to_b2b"
    }
    response = client.post("/api/calculate", json=payload)
    assert response.status_code == 400


def test_regression_b2b_youth_relief_rejected(client):
    payload = {
        "b2b": {
            "monthly_invoice_amount": 10000, "tax_form": "flat_tax", "zus_type": "full",
            "age": 24, "youth_relief": True
        },
        "uop": {
            "monthly_gross_salary": 8000, "deductible_cost_settings": {"type": "standard"}, "age": 24
        },
        "calculation_mode": "uop_to_b2b"
    }
    response = client.post("/api/calculate", json=payload)
    assert response.status_code == 400
