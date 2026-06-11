from typing import Any

from backend.analysis import (
    generate_executive_summary,
    get_checklist,
    get_methodology,
    get_risk_analysis,
)
from backend.calculations import (
    calculate_b2b_results,
    calculate_break_even,
    calculate_uop_break_even,
    calculate_uop_results,
)
from backend.config import config_manager


def run_full_calculation(request_data: dict[str, Any]) -> dict[str, Any]:
    lang = request_data.get("language", "pl")
    b2b_data = request_data.get("b2b", {})
    uop_data = request_data.get("uop", {})
    calculation_mode = request_data.get("calculation_mode", "uop_to_b2b")

    b2b_results = calculate_b2b_results(b2b_data)
    uop_results = calculate_uop_results(uop_data)

    break_even_point: float | None = -1.0
    break_even_key = "break_even_invoice_amount"
    if calculation_mode == "employer_budget":
        # In employer budget mode both sides are derived from a fixed total cost,
        # so a break-even point is not meaningful.
        break_even_point = None
    elif calculation_mode == "uop_to_b2b":
        break_even_point = calculate_break_even(uop_results["total_annual_value"], b2b_data)
    elif calculation_mode == "b2b_to_uop":
        break_even_point = calculate_uop_break_even(b2b_results["total_annual_value"], uop_data)
        break_even_key = "break_even_gross_salary"

    config = config_manager.get_config()
    regulatory_rates = config["regulatory_rates"]
    return {
        "b2b_results": b2b_results,
        "uop_results": uop_results,
        break_even_key: break_even_point,
        "pension_limits_2026": config["pension_limits_2026"],
        # Stawki potrzebne frontendowi (m.in. konwersja super-brutto → brutto
        # w trybie employer_budget) — jedynym źródłem stałych jest config JSON.
        "config_rates": {
            "uop_employer_overhead": (
                regulatory_rates["uop_pension_employer"]
                + regulatory_rates["uop_disability_employer"]
                + regulatory_rates["uop_accident_employer"]
                + regulatory_rates["uop_fp_fs_employer"]
                + regulatory_rates["uop_fgsp_employer"]
            ),
            "ppk_employer_rate": config["ppk"]["employer_rate"],
        },
        "analysis": {
            "summary": generate_executive_summary(b2b_results, uop_results, break_even_point, lang),
            "risk": get_risk_analysis(lang),
            "methodology": get_methodology(lang),
            "checklist": get_checklist(lang),
        },
        "comments": "Comparison and full analysis generated successfully.",
    }
