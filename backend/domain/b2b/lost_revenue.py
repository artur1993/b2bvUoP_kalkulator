from typing import Any


def compute_lost_revenue(b2b_data: dict[str, Any], config: dict[str, Any]) -> dict[str, float]:
    monthly_invoice_amount = float(b2b_data.get("monthly_invoice_amount", 0))
    company_benefits = b2b_data.get("companyBenefits") or {}
    daily_rate = monthly_invoice_amount / config["general_data"]["working_days_monthly"]
    sick_leave_payment = config["regulatory_rates"]["sick_leave_payment"]

    paid_vacation_days = (
        float(company_benefits.get("paidVacationDays", {}).get("days", 0))
        if company_benefits.get("paidVacationDays", {}).get("enabled")
        else 0
    )
    paid_sick_days = (
        float(company_benefits.get("paidSickDays", {}).get("days", 0))
        if company_benefits.get("paidSickDays", {}).get("enabled")
        else 0
    )

    unpaid_vacation_days = max(0, int(b2b_data.get("vacation_days", 0)) - paid_vacation_days)
    unpaid_sick_days = max(0, int(b2b_data.get("sick_days", 0)) - paid_sick_days)

    lost_revenue_vacation = unpaid_vacation_days * daily_rate
    # Chory dzień bez zlecenia to utrata pełnej stawki dziennej. Dobrowolne
    # chorobowe daje zasiłek 80% podstawy zasiłkowej ZUS (podstawa wymiaru
    # składek pomniejszona o 13,71%, dzielona na 30 dni) — zasiłek liczy się
    # od podstawy ZUS, nie od stawki z faktury.
    lost_revenue_sickness = unpaid_sick_days * daily_rate
    if b2b_data.get("sickness_insurance"):
        rates = config["regulatory_rates"]
        employee_rate_total = (
            rates["uop_pension_employee"]
            + rates["uop_disability_employee"]
            + rates["uop_sickness_employee"]
        )
        zus_base = float(
            config["zus_2026"].get(b2b_data.get("zus_type", "full"), {}).get("base", 0)
        )
        daily_sick_benefit = sick_leave_payment * zus_base * (1 - employee_rate_total) / 30
        lost_revenue_sickness = max(
            0.0, lost_revenue_sickness - unpaid_sick_days * daily_sick_benefit
        )
    lost_revenue_stoppage = float(b2b_data.get("stoppage_months", 0)) * monthly_invoice_amount
    annual_lost_holidays = 0.0
    if not b2b_data.get("public_holidays_paid", True):
        holidays = config["general_data"]["public_holidays_per_year"]
        annual_lost_holidays = holidays * daily_rate

    total_lost_revenue = (
        lost_revenue_vacation
        + lost_revenue_sickness
        + lost_revenue_stoppage
        + annual_lost_holidays
    )

    return {
        "daily_rate": daily_rate,
        "total_lost_revenue": total_lost_revenue,
        "annual_lost_holidays": annual_lost_holidays,
        "annual_invoice_amount": (monthly_invoice_amount * 12) - total_lost_revenue,
    }
