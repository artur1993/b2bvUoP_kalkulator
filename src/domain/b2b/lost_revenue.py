from typing import Any, Dict


def compute_lost_revenue(b2b_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, float]:
    monthly_invoice_amount = float(b2b_data.get('monthly_invoice_amount', 0))
    company_benefits = b2b_data.get('companyBenefits') or {}
    daily_rate = monthly_invoice_amount / config['general_data']['working_days_monthly']

    paid_vacation_days = (
        float(company_benefits.get('paidVacationDays', {}).get('days', 0))
        if company_benefits.get('paidVacationDays', {}).get('enabled')
        else 0
    )
    paid_sick_days = (
        float(company_benefits.get('paidSickDays', {}).get('days', 0))
        if company_benefits.get('paidSickDays', {}).get('enabled')
        else 0
    )

    unpaid_vacation_days = max(0, int(b2b_data.get('vacation_days', 0)) - paid_vacation_days)
    unpaid_sick_days = max(0, int(b2b_data.get('sick_days', 0)) - paid_sick_days)

    lost_revenue_vacation = unpaid_vacation_days * daily_rate
    lost_revenue_sickness = unpaid_sick_days * daily_rate * 0.8
    lost_revenue_stoppage = float(b2b_data.get('stoppage_months', 0)) * monthly_invoice_amount
    total_lost_revenue = lost_revenue_vacation + lost_revenue_sickness + lost_revenue_stoppage

    return {
        "daily_rate": daily_rate,
        "total_lost_revenue": total_lost_revenue,
        "annual_invoice_amount": (monthly_invoice_amount * 12) - total_lost_revenue,
    }
