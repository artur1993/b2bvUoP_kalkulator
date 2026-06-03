from collections.abc import Callable
from typing import Any

from backend.domain.b2b.benefits import compute_benefits_value
from backend.domain.b2b.health_contribution import compute_health_contribution
from backend.domain.b2b.income_tax import compute_income_tax
from backend.domain.b2b.lost_revenue import compute_lost_revenue
from backend.domain.b2b.social_contributions import compute_social_contributions


def assemble_b2b_results(
    b2b_data: dict[str, Any],
    config: dict[str, Any],
    progressive_tax: Callable[[float, dict[str, Any]], float],
    solidarity_tax: Callable[[float, dict[str, Any]], float],
) -> dict[str, Any]:
    monthly_business_costs = float(b2b_data.get("monthly_business_costs", 0))
    annual_business_costs = monthly_business_costs * 12
    lost_revenue = compute_lost_revenue(b2b_data, config)
    social = compute_social_contributions(b2b_data, config)
    annual_health_contribution = compute_health_contribution(
        b2b_data,
        config,
        lost_revenue["annual_invoice_amount"],
        annual_business_costs,
        social["annual_social_contributions"],
    )
    total_zus_contributions = social["annual_social_contributions"] + annual_health_contribution
    tax = compute_income_tax(
        b2b_data,
        config,
        lost_revenue["annual_invoice_amount"],
        annual_business_costs,
        social["annual_social_contributions"],
        annual_health_contribution,
        progressive_tax,
        solidarity_tax,
    )
    benefits = compute_benefits_value(b2b_data, lost_revenue["daily_rate"], config)
    annual_net_income = (
        lost_revenue["annual_invoice_amount"]
        - annual_business_costs
        - total_zus_contributions
        - tax["annual_tax"]
    )
    total_b2b_value = (
        annual_net_income
        + benefits["annual_company_benefits_value"]
        + benefits["annual_custom_benefits_value"]
    )

    return {
        "annual_revenue": (
            lost_revenue["annual_invoice_amount"] + lost_revenue["total_lost_revenue"]
        ),
        "annual_business_costs": annual_business_costs,
        "annual_zus": total_zus_contributions,
        "annual_tax": tax["annual_tax"],
        "annual_solidarity_tax": tax["annual_solidarity_tax"],
        "annual_lost_revenue": lost_revenue["total_lost_revenue"],
        "annual_lost_holidays": lost_revenue["annual_lost_holidays"],
        "annual_net_income": annual_net_income,
        "annual_company_benefits_value": benefits["annual_company_benefits_value"],
        "annual_custom_benefits_value": benefits["annual_custom_benefits_value"],
        "total_annual_value": total_b2b_value,
        "monthly_net_income": total_b2b_value / 12,
        "steps": {
            "annual_social_contributions": social["annual_social_contributions"],
            "annual_health_contribution": annual_health_contribution,
            "annual_tax": tax["annual_tax"],
            "annual_solidarity_tax": tax["annual_solidarity_tax"],
        },
    }
