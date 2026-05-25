from backend.calculations import _calculate_progressive_tax, compute_solidarity_tax
from backend.config import config_manager
from backend.domain.b2b.benefits import compute_benefits_value
from backend.domain.b2b.health_contribution import compute_health_contribution
from backend.domain.b2b.income_tax import compute_income_tax
from backend.domain.b2b.lost_revenue import compute_lost_revenue
from backend.domain.b2b.social_contributions import compute_social_contributions


def test_compute_lost_revenue_accounts_for_paid_time_off():
    config = config_manager.get_config()
    result = compute_lost_revenue({
        "monthly_invoice_amount": 21000,
        "vacation_days": 10,
        "sick_days": 5,
        "stoppage_months": 1,
        "companyBenefits": {
            "paidVacationDays": {"enabled": True, "days": 4},
            "paidSickDays": {"enabled": True, "days": 2},
        },
    }, config)

    assert result["daily_rate"] == 1000
    assert result["total_lost_revenue"] == 29400
    assert result["annual_invoice_amount"] == 222600


def test_compute_social_contributions_respects_sickness_toggle():
    config = config_manager.get_config()
    without_sickness = compute_social_contributions({
        "zus_type": "full",
        "sickness_insurance": False,
    }, config)
    with_sickness = compute_social_contributions({
        "zus_type": "full",
        "sickness_insurance": True,
    }, config)

    assert without_sickness["sickness_insurance_contribution"] == 0
    assert with_sickness["sickness_insurance_contribution"] == config["zus_2026"]["full"]["sickness"] * 12
    assert with_sickness["annual_social_contributions"] > without_sickness["annual_social_contributions"]


def test_compute_health_contribution_uses_lump_sum_thresholds():
    config = config_manager.get_config()

    result = compute_health_contribution({
        "tax_form": "lump_sum_it",
    }, config, 120000, 0, 0)

    assert result == config["zus_2026"]["health_lump_sum_thresholds"][1]["contribution"] * 12


def test_compute_income_tax_splits_ip_box_qualified_income():
    config = config_manager.get_config()

    result = compute_income_tax(
        {"tax_form": "ip_box", "ip_box_qualified_share": 50, "ip_box_base_form": "flat_tax"},
        config,
        annual_invoice_amount=120000,
        annual_business_costs=0,
        annual_social_contributions=0,
        annual_health_contribution=0,
        progressive_tax=_calculate_progressive_tax,
        solidarity_tax=compute_solidarity_tax,
    )

    assert result["annual_tax"] == 14400
    assert result["annual_solidarity_tax"] == 0


def test_compute_benefits_value_sums_days_and_cash_benefits():
    config = config_manager.get_config()
    result = compute_benefits_value({
        "customBenefits": 1200,
        "companyBenefits": {
            "paidVacationDays": {"enabled": True, "days": 2},
            "paidSickDays": {"enabled": True, "days": 1},
            "medicalCare": {"enabled": True, "value": 1000},
            "sportCard": {"enabled": False, "value": 1000},
        },
    }, daily_rate=1000, config=config)

    assert result["annual_company_benefits_value"] == 3800
    assert result["annual_custom_benefits_value"] == 1200
