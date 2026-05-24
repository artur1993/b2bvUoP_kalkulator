from typing import Any, Dict


def compute_benefits_value(b2b_data: Dict[str, Any], daily_rate: float, config: Dict[str, Any]) -> Dict[str, float]:
    company_benefits = b2b_data.get('companyBenefits') or {}
    annual_company_benefits_value = 0
    sick_leave_payment = config['regulatory_rates']['sick_leave_payment']

    for key, benefit in company_benefits.items():
        if benefit.get('enabled', False):
            if key == 'paidVacationDays':
                annual_company_benefits_value += float(benefit.get('days', 0)) * daily_rate
            elif key == 'paidSickDays':
                annual_company_benefits_value += float(benefit.get('days', 0)) * daily_rate * sick_leave_payment
            else:
                annual_company_benefits_value += float(benefit.get('value', 0))

    return {
        "annual_company_benefits_value": annual_company_benefits_value,
        "annual_custom_benefits_value": float(b2b_data.get('customBenefits', 0)),
    }
