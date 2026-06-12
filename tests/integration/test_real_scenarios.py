import pytest

def test_case_a_mid_career_ryczalt_vs_uop(client):
    """
    Persona: 28 lat, 5 lat doświadczenia, mid Software Engineer.
    Weryfikuje: stawka zdrowotna ryczałtu B02, brak PIT-0 dla 28-latka, 
    brak podwójnego liczenia dni wolnych UoP B05.
    """
    payload = {
        "calculation_mode": "uop_to_b2b",
        "b2b": {
            "monthly_invoice_amount": 18000,
            "tax_form": "lump_sum_it",
            "zus_type": "full",
            "sickness_insurance": True,
            "monthly_business_costs": 500,
            "vacation_days": 20,
            "sick_days": 5,
            "stoppage_months": 0,
            "age": 28,
            "customBenefits": 0,
            "companyBenefits": {}
        },
        "uop": {
            "monthly_gross_salary": 12000,
            "deductible_cost_settings": { "type": "standard" },
            "selected_benefits": ["medical_care"],
            "age": 28,
            "youth_relief": False
        }
    }
    
    response = client.post("/api/calculate", json=payload)
    assert response.status_code == 200
    res = response.json
    
    # Oczekiwane (snapshot po Fazie B): 
    # B2B: ~136261, UoP: ~104271, BE: 14700
    assert pytest.approx(res["b2b_results"]["total_annual_value"], abs=1500) == 136261
    assert pytest.approx(res["uop_results"]["total_annual_value"], abs=1500) == 104271
    assert pytest.approx(res["break_even_invoice_amount"], abs=500) == 14700
    
    # Check structure
    assert "analysis" in res
    assert "summary" in res["analysis"]
    assert "methodology" in res["analysis"]


def test_case_b_junior_youth_relief_only_uop(client):
    """
    Persona: 24 lata, junior.
    Weryfikuje: PIT-0 dla UoP, brak PIT-0 dla B2B (B04), preferencyjny ZUS 2026.
    """
    payload = {
        "calculation_mode": "uop_to_b2b",
        "b2b": {
            "monthly_invoice_amount": 12000,
            "tax_form": "flat_tax",
            "zus_type": "preferential",
            "sickness_insurance": True,
            "monthly_business_costs": 300,
            "vacation_days": 20,
            "sick_days": 0,
            "stoppage_months": 0,
            "age": 24,
            "customBenefits": 0,
            "companyBenefits": {}
        },
        "uop": {
            "monthly_gross_salary": 8000,
            "deductible_cost_settings": { "type": "standard" },
            "selected_benefits": [],
            "age": 24,
            "youth_relief": True
        }
    }
    
    response = client.post("/api/calculate", json=payload)
    assert response.status_code == 200
    res = response.json
    
    # Oczekiwane (snapshot po Fazie B):
    # B2B: ~95130, UoP: ~75382, BE: 9800
    assert pytest.approx(res["b2b_results"]["total_annual_value"], abs=1500) == 95130
    assert pytest.approx(res["uop_results"]["total_annual_value"], abs=1500) == 75382
    assert pytest.approx(res["break_even_invoice_amount"], abs=500) == 9800


def test_case_c_senior_ip_box_partial_qualified(client):
    """
    Persona: 35 lat, senior, IP Box 60%.
    Weryfikuje: IP Box z qualified share (B08), limit 30-krotności UoP, lost revenue B2B.
    """
    payload = {
        "calculation_mode": "b2b_to_uop",
        "b2b": {
            "monthly_invoice_amount": 25000,
            "tax_form": "ip_box",
            "ip_box_qualified_share": 60,
            "ip_box_base_form": "flat_tax",
            "zus_type": "full",
            "sickness_insurance": True,
            "monthly_business_costs": 1000,
            "vacation_days": 25,
            "sick_days": 10,
            "stoppage_months": 1,
            "age": 35,
            "customBenefits": 0,
            "companyBenefits": {}
        },
        "uop": {
            "monthly_gross_salary": 18000,
            "deductible_cost_settings": { "type": "elevated" },
            "selected_benefits": ["medical_care", "sport_card", "training_budget"],
            "age": 35,
            "youth_relief": False
        }
    }
    
    response = client.post("/api/calculate", json=payload)
    assert response.status_code == 200
    res = response.json
    
    # Oczekiwane (snapshot po poprawce zdrowotnej IP Box — liczona wg formy bazowej,
    # tu liniowej 4,9% dochodu, zamiast rocznego minimum):
    # B2B: ~169500, UoP: ~145919, BE_GROSS: 21900
    assert pytest.approx(res["b2b_results"]["total_annual_value"], abs=2000) == 169500
    assert pytest.approx(res["uop_results"]["total_annual_value"], abs=1500) == 145919
    assert pytest.approx(res["break_even_gross_salary"], abs=1000) == 21900
