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

    break_even_point = -1.0
    break_even_key = "break_even_invoice_amount"
    if calculation_mode == "uop_to_b2b":
        break_even_point = calculate_break_even(uop_results["total_annual_value"], b2b_data)
    elif calculation_mode == "b2b_to_uop":
        break_even_point = calculate_uop_break_even(b2b_results["total_annual_value"], uop_data)
        break_even_key = "break_even_gross_salary"

    return {
        "b2b_results": b2b_results,
        "uop_results": uop_results,
        break_even_key: break_even_point,
        "pension_limits_2026": config_manager.get_config()["pension_limits_2026"],
        "analysis": {
            "summary": generate_executive_summary(b2b_results, uop_results, break_even_point, lang),
            "risk": get_risk_analysis(lang),
            "methodology": get_methodology(lang),
            "checklist": get_checklist(lang),
        },
        "comments": "Comparison and full analysis generated successfully.",
    }
