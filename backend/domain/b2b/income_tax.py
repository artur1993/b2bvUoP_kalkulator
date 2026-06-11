import math
from collections.abc import Callable
from typing import Any, cast


def compute_income_tax(
    b2b_data: dict[str, Any],
    config: dict[str, Any],
    annual_invoice_amount: float,
    annual_business_costs: float,
    annual_social_contributions: float,
    annual_health_contribution: float,
    progressive_tax: Callable[[float, dict[str, Any]], float],
    solidarity_tax: Callable[[float, dict[str, Any]], float],
) -> dict[str, float]:
    tax_form = b2b_data.get("tax_form", "lump_sum_it")
    annual_solidarity_tax = 0.0
    regulatory_rates = config["regulatory_rates"]

    if tax_form == "lump_sum_it":
        tax_base = max(
            0.0,
            annual_invoice_amount
            - (annual_health_contribution * regulatory_rates["lump_sum_health_deduction_share"])
            - annual_social_contributions,
        )
        annual_tax = float(round(tax_base * config["tax_thresholds"]["lump_sum_it"]))
        # Przychody opodatkowane ryczałtem nie wchodzą do podstawy daniny
        # solidarnościowej — art. 30h ust. 2 PIT wymienia wyłącznie dochody
        # z art. 27, 30b, 30c i 30f.
        return {
            "annual_tax": annual_tax,
            "annual_solidarity_tax": 0.0,
            "taxable_base": tax_base,
        }

    income = annual_invoice_amount - annual_business_costs - annual_social_contributions
    # Podstawa daniny solidarnościowej (art. 30h ust. 2): dochód pomniejszony
    # o składki społeczne, ale bez odliczenia składki zdrowotnej.
    solidarity_base = max(0.0, income)
    if tax_form == "flat_tax":
        health_deduction_limit = cast(
            float, config["tax_thresholds"]["health_contribution_deduction_limit_flat_tax"]
        )
        income -= min(annual_health_contribution, health_deduction_limit)

    taxable_base = income
    if tax_form == "flat_tax":
        annual_tax = float(math.ceil(max(0.0, taxable_base) * config["tax_thresholds"]["flat_tax"]))
    elif tax_form == "tax_scale":
        annual_tax = progressive_tax(taxable_base, config)
    elif tax_form == "ip_box":
        taxable_base = max(0.0, taxable_base)
        qualified_share = float(b2b_data.get("ip_box_qualified_share", 100)) / 100
        base_form = b2b_data.get("ip_box_base_form", "flat_tax")
        qualified_base = taxable_base * qualified_share
        other_base = taxable_base - qualified_base
        qualified_tax = math.ceil(qualified_base * config["tax_thresholds"]["ip_box"])
        other_tax = (
            progressive_tax(other_base, config)
            if base_form == "tax_scale"
            else math.ceil(other_base * config["tax_thresholds"]["flat_tax"])
        )
        annual_tax = float(qualified_tax + other_tax)
        # Dochód z kwalifikowanych IP (art. 30ca) nie wchodzi do podstawy daniny —
        # danina tylko od części opodatkowanej skalą/liniowo.
        solidarity_base = other_base
    else:
        annual_tax = 0.0

    annual_solidarity_tax = solidarity_tax(solidarity_base, config)
    return {
        "annual_tax": annual_tax + annual_solidarity_tax,
        "annual_solidarity_tax": annual_solidarity_tax,
        "taxable_base": taxable_base,
    }
