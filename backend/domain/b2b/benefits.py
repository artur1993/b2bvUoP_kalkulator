from typing import Any


def compute_benefits_value(
    b2b_data: dict[str, Any], daily_rate: float, config: dict[str, Any]
) -> dict[str, float]:
    company_benefits = b2b_data.get("companyBenefits") or {}
    annual_company_benefits_value = 0.0

    for key, benefit in company_benefits.items():
        if benefit.get("enabled", False):
            if key == "paidVacationDays":
                annual_company_benefits_value += float(benefit.get("days", 0)) * daily_rate
            elif key == "paidSickDays":
                # Chory dzień opłacony przez kontrahenta = brak utraty przychodu,
                # więc wartość benefitu to pełna stawka dzienna (spójnie z modelem
                # utraconego przychodu, gdzie niepłatny chory dzień kosztuje 100%).
                annual_company_benefits_value += float(benefit.get("days", 0)) * daily_rate
            else:
                annual_company_benefits_value += float(benefit.get("value", 0))

    return {
        "annual_company_benefits_value": float(annual_company_benefits_value),
        "annual_custom_benefits_value": float(b2b_data.get("customBenefits", 0)),
    }
