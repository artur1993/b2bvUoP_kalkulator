import math
from typing import Any, Callable, Dict


def compute_income_tax(
    b2b_data: Dict[str, Any],
    config: Dict[str, Any],
    annual_invoice_amount: float,
    annual_business_costs: float,
    annual_social_contributions: float,
    annual_health_contribution: float,
    progressive_tax: Callable[[float, Dict[str, Any]], float],
    solidarity_tax: Callable[[float, Dict[str, Any]], float],
) -> Dict[str, float]:
    tax_form = b2b_data.get('tax_form', 'lump_sum_it')
    annual_solidarity_tax = 0

    if tax_form == 'lump_sum_it':
        tax_base = max(0, annual_invoice_amount - (annual_health_contribution * 0.5) - annual_social_contributions)
        annual_tax = round(tax_base * config['tax_thresholds']['lump_sum_it'])
        annual_solidarity_tax = solidarity_tax(tax_base, config)
        return {
            "annual_tax": annual_tax + annual_solidarity_tax,
            "annual_solidarity_tax": annual_solidarity_tax,
            "taxable_base": tax_base,
        }

    income = annual_invoice_amount - annual_business_costs - annual_social_contributions
    if tax_form == 'flat_tax':
        health_deduction_limit = config['tax_thresholds']['health_contribution_deduction_limit_flat_tax']
        income -= min(annual_health_contribution, health_deduction_limit)

    taxable_base = income
    if tax_form == 'flat_tax':
        annual_tax = math.ceil(max(0, taxable_base) * config['tax_thresholds']['flat_tax'])
    elif tax_form == 'tax_scale':
        annual_tax = progressive_tax(taxable_base, config)
    elif tax_form == 'ip_box':
        taxable_base = max(0, taxable_base)
        qualified_share = float(b2b_data.get('ip_box_qualified_share', 100)) / 100
        base_form = b2b_data.get('ip_box_base_form', 'flat_tax')
        qualified_base = taxable_base * qualified_share
        other_base = taxable_base - qualified_base
        qualified_tax = math.ceil(qualified_base * config['tax_thresholds']['ip_box'])
        other_tax = (
            progressive_tax(other_base, config)
            if base_form == 'tax_scale'
            else math.ceil(other_base * config['tax_thresholds']['flat_tax'])
        )
        annual_tax = qualified_tax + other_tax
    else:
        annual_tax = 0

    annual_solidarity_tax = solidarity_tax(max(0, taxable_base), config)
    return {
        "annual_tax": annual_tax + annual_solidarity_tax,
        "annual_solidarity_tax": annual_solidarity_tax,
        "taxable_base": taxable_base,
    }
