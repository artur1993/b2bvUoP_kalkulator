import math
from typing import Any, cast

from backend.config import config_manager
from backend.domain.b2b.aggregate import assemble_b2b_results


def _calculate_progressive_tax(taxable_base: float, config: dict[str, Any]) -> float:
    tax_threshold = cast(float, config["tax_thresholds"]["tax_scale"][0]["income"])
    tax_reducing = cast(float, config["tax_thresholds"]["tax_reducing_amount"])

    if taxable_base <= tax_threshold:
        return float(max(0, math.ceil(taxable_base * 0.12) - tax_reducing))

    return float(
        math.ceil((tax_threshold * 0.12) - tax_reducing + (taxable_base - tax_threshold) * 0.32)
    )


def compute_solidarity_tax(annual_taxable_base: float, config: dict[str, Any]) -> float:
    """Returns 4% of taxable base over 1M PLN, else 0."""
    solidarity_tax = config["tax_thresholds"]["solidarity_tax"]
    threshold = cast(float, solidarity_tax["threshold"])
    rate = cast(float, solidarity_tax["rate"])

    return float(max(0.0, annual_taxable_base - threshold) * rate)


def calculate_b2b_results(b2b_data: dict[str, Any]) -> dict[str, Any]:
    """Calculates all financial aspects for a B2B contract for 2026."""
    config = config_manager.get_config()
    return assemble_b2b_results(
        b2b_data,
        config,
        _calculate_progressive_tax,
        compute_solidarity_tax,
    )


def calculate_uop_results(uop_data: dict[str, Any]) -> dict[str, Any]:
    """Calculates all financial aspects for an Employment Contract (UoP) for 2026."""
    config = config_manager.get_config()
    monthly_gross_salary = float(uop_data.get("monthly_gross_salary", 0))
    deductible_cost_settings = uop_data.get("deductible_cost_settings", {})
    deductible_cost_type = deductible_cost_settings.get("type", "standard")
    creative_work_percentage = (
        float(deductible_cost_settings.get("creative_work_percentage", 0)) / 100
    )

    thirty_times_limit = float(config["zus_2026"]["thirty_times_limit_uop"])
    youth_relief_limit = float(config["tax_thresholds"]["youth_relief_limit"])
    author_costs_limit = float(config["tax_thresholds"]["author_tax_deductible_costs_limit"])

    annual_social_contributions = 0.0
    annual_health_contribution = 0.0
    annual_deductible_costs = 0.0
    annual_tax_base = 0.0
    annual_tax_base_without_ppk_employer = 0.0
    annual_ppk_employee_contribution = 0.0
    annual_ppk_employer_contribution = 0.0
    cumulative_gross = 0.0
    cumulative_author_costs = 0.0
    monthly_calculations = []
    selected_benefits = uop_data.get("selected_benefits", [])
    ppk_selected = "ppk" in selected_benefits
    ppk_rates = config.get("ppk", {})
    regulatory_rates = config["regulatory_rates"]

    for month in range(1, 13):
        if cumulative_gross >= thirty_times_limit:
            monthly_pension = 0.0
            monthly_disability = 0.0
        elif cumulative_gross + monthly_gross_salary > thirty_times_limit:
            base_for_pension = thirty_times_limit - cumulative_gross
            monthly_pension = base_for_pension * regulatory_rates["uop_pension_employee"]
            monthly_disability = base_for_pension * regulatory_rates["uop_disability_employee"]
        else:
            monthly_pension = monthly_gross_salary * regulatory_rates["uop_pension_employee"]
            monthly_disability = monthly_gross_salary * regulatory_rates["uop_disability_employee"]

        monthly_sickness = monthly_gross_salary * regulatory_rates["uop_sickness_employee"]
        monthly_social = monthly_pension + monthly_disability + monthly_sickness

        cumulative_gross += monthly_gross_salary
        annual_social_contributions += monthly_social

        health_base = monthly_gross_salary - monthly_social
        monthly_health_contribution = health_base * regulatory_rates["uop_health_employee"]
        annual_health_contribution += monthly_health_contribution

        monthly_costs = 0.0
        if deductible_cost_type == "standard":
            monthly_costs = float(config["tax_deductible_costs"]["standard"])
        elif deductible_cost_type == "elevated":
            monthly_costs = float(config["tax_deductible_costs"]["elevated"])
        elif deductible_cost_type == "author_50":
            if cumulative_author_costs < author_costs_limit:
                creative_income = monthly_gross_salary * creative_work_percentage
                author_costs_base = creative_income - (monthly_social * creative_work_percentage)
                potential_costs = (
                    author_costs_base * regulatory_rates["author_tax_deductible_cost_share"]
                )
                if cumulative_author_costs + potential_costs > author_costs_limit:
                    monthly_costs = author_costs_limit - cumulative_author_costs
                    cumulative_author_costs = author_costs_limit
                else:
                    monthly_costs = potential_costs
                    cumulative_author_costs += potential_costs
            else:
                monthly_costs = float(config["tax_deductible_costs"]["standard"])

        annual_deductible_costs += monthly_costs
        monthly_ppk_employee = (
            monthly_gross_salary * ppk_rates.get("employee_rate", 0) if ppk_selected else 0.0
        )
        monthly_ppk_employer = (
            monthly_gross_salary * ppk_rates.get("employer_rate", 0) if ppk_selected else 0.0
        )
        annual_ppk_employee_contribution += monthly_ppk_employee
        annual_ppk_employer_contribution += monthly_ppk_employer

        # Wpłata pracownika do PPK jest finansowana z wynagrodzenia po opodatkowaniu —
        # nie pomniejsza podstawy PIT (obniża wyłącznie netto).
        monthly_tax_base_without_ppk_employer = max(
            0.0, monthly_gross_salary - monthly_social - monthly_costs
        )
        monthly_tax_base = monthly_tax_base_without_ppk_employer + monthly_ppk_employer
        annual_tax_base += monthly_tax_base
        annual_tax_base_without_ppk_employer += monthly_tax_base_without_ppk_employer

        monthly_calculations.append(
            {
                "month": month,
                "deductible_costs": monthly_costs,
                "tax_base": monthly_tax_base,
                "ppk_employee_contribution": monthly_ppk_employee,
                "ppk_employer_contribution": monthly_ppk_employer,
            }
        )

    if uop_data.get("youth_relief", False):
        annual_tax_base = max(0.0, annual_tax_base - youth_relief_limit)
        annual_tax_base_without_ppk_employer = max(
            0.0, annual_tax_base_without_ppk_employer - youth_relief_limit
        )

    annual_tax = _calculate_progressive_tax(annual_tax_base, config)
    annual_tax_without_ppk_employer = _calculate_progressive_tax(
        annual_tax_base_without_ppk_employer, config
    )
    annual_solidarity_tax = compute_solidarity_tax(annual_tax_base, config)
    annual_solidarity_tax_without_ppk_employer = compute_solidarity_tax(
        annual_tax_base_without_ppk_employer, config
    )
    annual_tax += annual_solidarity_tax
    annual_tax_without_ppk_employer += annual_solidarity_tax_without_ppk_employer

    _tax_threshold = float(config["tax_thresholds"]["tax_scale"][0]["income"])
    _tax_reducing = float(config["tax_thresholds"]["tax_reducing_amount"])
    _base_first = min(annual_tax_base, _tax_threshold)
    _base_second = max(0.0, annual_tax_base - _tax_threshold)
    _tax_first_raw = math.ceil(_base_first * 0.12)
    _tax_second_raw = math.ceil(_base_second * 0.32)
    _tax_reducing_applied = min(float(_tax_first_raw), _tax_reducing)

    annual_net = (
        cumulative_gross
        - annual_social_contributions
        - annual_health_contribution
        - annual_tax
        - annual_ppk_employee_contribution
    )
    annual_bonus_pct = float(uop_data.get("annual_bonus_pct", 0))
    annual_bonus_gross = cumulative_gross * (annual_bonus_pct / 100.0)
    if annual_bonus_gross > 0:
        # Premia to przychód ze stosunku pracy — podlega pełnemu oskładkowaniu:
        # emerytalna i rentowa do limitu 30-krotności (łącznie z pensją zasadniczą),
        # chorobowa i zdrowotna bez limitu. PIT i danina liczone marginalnie.
        bonus_pension_base = min(
            annual_bonus_gross, max(0.0, thirty_times_limit - cumulative_gross)
        )
        bonus_social = bonus_pension_base * (
            regulatory_rates["uop_pension_employee"]
            + regulatory_rates["uop_disability_employee"]
        ) + annual_bonus_gross * regulatory_rates["uop_sickness_employee"]
        bonus_health = (annual_bonus_gross - bonus_social) * regulatory_rates[
            "uop_health_employee"
        ]
        bonus_taxable = max(0.0, annual_bonus_gross - bonus_social)
        bonus_tax = _calculate_progressive_tax(
            annual_tax_base + bonus_taxable, config
        ) - _calculate_progressive_tax(annual_tax_base, config)
        bonus_tax += (
            compute_solidarity_tax(annual_tax_base + bonus_taxable, config)
            - annual_solidarity_tax
        )
        annual_bonus_net = max(
            0.0, annual_bonus_gross - bonus_social - bonus_health - bonus_tax
        )
    else:
        annual_bonus_net = 0.0
        bonus_social = 0.0
        bonus_health = 0.0
        bonus_tax = 0.0
    annual_net += annual_bonus_net

    benefits_value = sum(
        float(config["benefits"][b]) for b in selected_benefits if b in config["benefits"]
    )
    annual_ppk_employer_net = 0.0
    annual_ppk_state_subsidy = 0.0
    annual_ppk_capital = 0.0
    if ppk_selected:
        # Uproszczenie: PIT od dopłaty pracodawcy to różnica podatku z/bez tej dopłaty.
        ppk_employer_tax = max(0.0, annual_tax - annual_tax_without_ppk_employer)
        annual_ppk_employer_net = max(0.0, annual_ppk_employer_contribution - ppk_employer_tax)
        # Dopłata roczna państwa (nieopodatkowana). Założenie: pełna eligibility —
        # roczne wpłaty podstawowe pracownika spełnione przez cały rok.
        annual_ppk_state_subsidy = float(ppk_rates.get("state_annual_subsidy", 0))
        # Kapitał PPK = środki realnie na koncie po podatku:
        # wpłata pracownika (2%) + wpłata pracodawcy netto po PIT (1,5% minus podatek)
        # + dopłata państwa (nieopodatkowana).
        annual_ppk_capital = (
            annual_ppk_employee_contribution
            + annual_ppk_employer_net
            + annual_ppk_state_subsidy
        )

    uop_custom_benefits = float(uop_data.get("custom_benefits_value", 0))
    benefits_value += uop_custom_benefits
    # Kapitał PPK nie jest "benefitem" jak karta/medyk (to oszczędność pracownika),
    # ale podnosi całkowitą wartość pakietu UoP — pokazywany w osobnej linii.
    total_uop_value = annual_net + benefits_value + annual_ppk_capital

    return {
        "annual_gross_salary": cumulative_gross,
        "annual_zus": annual_social_contributions + annual_health_contribution,
        "annual_tax": annual_tax,
        "annual_solidarity_tax": annual_solidarity_tax,
        "annual_benefits_value": benefits_value,
        "annual_bonus_gross": annual_bonus_gross,
        "annual_bonus_net": annual_bonus_net,
        "annual_custom_benefits_value": uop_custom_benefits,
        "annual_ppk_capital": annual_ppk_capital,
        "annual_net_income": annual_net,
        "total_annual_value": total_uop_value,
        "monthly_net_income": total_uop_value / 12,
        "steps": {
            "annual_deductible_costs": annual_deductible_costs,
            "annual_ppk_employee_contribution": annual_ppk_employee_contribution,
            "annual_ppk_employer_contribution": annual_ppk_employer_contribution,
            "annual_ppk_employer_net": annual_ppk_employer_net,
            "annual_ppk_state_subsidy": annual_ppk_state_subsidy,
            "annual_solidarity_tax": annual_solidarity_tax,
            "bonus_breakdown": {
                "gross": annual_bonus_gross,
                "social_contributions": bonus_social,
                "health_contribution": bonus_health,
                "tax": bonus_tax,
                "net": annual_bonus_net,
            },
            "monthly_calculations": monthly_calculations,
            "kup_breakdown": {
                "type": deductible_cost_type,
                "creative_work_percentage": round(creative_work_percentage * 100, 1),
                "annual_amount": annual_deductible_costs,
                "limit": author_costs_limit,
                "limit_reached": deductible_cost_type == "author_50"
                and cumulative_author_costs >= author_costs_limit,
            },
            "tax_breakdown": {
                "annual_taxable_base": annual_tax_base,
                "base_first_bracket": _base_first,
                "base_second_bracket": _base_second,
                "tax_first_bracket": float(_tax_first_raw),
                "tax_second_bracket": float(_tax_second_raw),
                "tax_reducing_applied": _tax_reducing_applied,
                "tax_free_amount": float(config["tax_thresholds"]["tax_free_amount"]),
                "annual_net_tax": max(0.0, annual_tax - annual_solidarity_tax),
            },
        },
    }


def calculate_break_even(uop_total_value: float, b2b_base_data: dict[str, Any]) -> float:
    config = config_manager.get_config()
    start_multiplier = float(config["regulatory_rates"]["break_even_start_multiplier"])
    start_range = int(float(b2b_base_data.get("monthly_invoice_amount", 10000)) * start_multiplier)
    for test_invoice in range(start_range, 200000, 100):
        test_data = b2b_base_data.copy()
        test_data["monthly_invoice_amount"] = test_invoice
        if calculate_b2b_results(test_data)["total_annual_value"] >= uop_total_value:
            return float(test_invoice)
    return -1.0


def calculate_uop_break_even(b2b_total_value: float, uop_base_data: dict[str, Any]) -> float:
    config = config_manager.get_config()
    start_multiplier = float(config["regulatory_rates"]["break_even_start_multiplier"])
    start_range = int(float(uop_base_data.get("monthly_gross_salary", 5000)) * start_multiplier)
    for test_gross in range(start_range, 100000, 100):
        test_data = uop_base_data.copy()
        test_data["monthly_gross_salary"] = test_gross
        if calculate_uop_results(test_data)["total_annual_value"] >= b2b_total_value:
            return float(test_gross)
    return -1.0


def calculate_break_even_analysis(
    uop_data: dict[str, Any], b2b_base_data: dict[str, Any]
) -> list[dict[str, Any]]:
    config = config_manager.get_config()
    regulatory_rates = config["regulatory_rates"]
    uop_results = calculate_uop_results(uop_data)
    analysis = []
    base_rate = float(uop_data.get("monthly_gross_salary", 0))
    min_rate = int(base_rate * regulatory_rates["break_even_analysis_min_multiplier"])
    max_rate = int(base_rate * regulatory_rates["break_even_analysis_max_multiplier"])
    for b2b_rate in range(min_rate, max_rate, 500):
        b2b_data = b2b_base_data.copy()
        b2b_data["monthly_invoice_amount"] = b2b_rate
        b2b_res = calculate_b2b_results(b2b_data)
        analysis.append(
            {
                "b2b_rate": b2b_rate,
                "net_difference": b2b_res["total_annual_value"] - uop_results["total_annual_value"],
            }
        )
    return analysis
