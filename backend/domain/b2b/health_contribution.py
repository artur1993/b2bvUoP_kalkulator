from typing import Any, cast


def compute_health_contribution(
    b2b_data: dict[str, Any],
    config: dict[str, Any],
    annual_invoice_amount: float,
    annual_business_costs: float,
    annual_social_contributions: float,
) -> float:
    tax_form = b2b_data.get("tax_form", "lump_sum_it")
    minimum_health_annual = cast(float, config["zus_2026"]["minimum_health_annual_2026"])
    regulatory_rates = config["regulatory_rates"]

    # IP Box to preferencja PIT, nie odrębny tytuł składkowy — zdrowotną liczy się
    # według formy opodatkowania, na której rozliczana jest reszta dochodu.
    if tax_form == "ip_box":
        tax_form = b2b_data.get("ip_box_base_form", "flat_tax")

    if tax_form == "tax_scale":
        income_for_health = max(
            0.0, annual_invoice_amount - annual_business_costs - annual_social_contributions
        )
        return float(
            max(
                minimum_health_annual,
                income_for_health * regulatory_rates["tax_scale_health_rate"],
            )
        )

    if tax_form == "flat_tax":
        income_for_health = max(
            0.0, annual_invoice_amount - annual_business_costs - annual_social_contributions
        )
        return float(
            max(
                minimum_health_annual,
                income_for_health * regulatory_rates["flat_tax_health_rate"],
            )
        )

    if tax_form == "lump_sum_it":
        thresholds = config["zus_2026"]["health_lump_sum_thresholds"]
        if annual_invoice_amount <= thresholds[0]["limit"]:
            monthly_health = thresholds[0]["contribution"]
        elif annual_invoice_amount <= thresholds[1]["limit"]:
            monthly_health = thresholds[1]["contribution"]
        else:
            monthly_health = thresholds[2]["contribution"]
        return float(monthly_health * 12)

    return float(minimum_health_annual)
