from typing import Any, Dict


def compute_social_contributions(b2b_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, float]:
    zus_type = b2b_data.get('zus_type', 'full')
    zus_details = config['zus_2026'][zus_type]

    pension = zus_details.get('pension', 0) * 12
    disability = zus_details.get('disability', 0) * 12
    accident = zus_details.get('accident', 0) * 12
    labor_fund = zus_details.get('labor_fund', 0) * 12
    sickness = zus_details.get('sickness', 0) * 12 if b2b_data.get('sickness_insurance') else 0
    annual_social_contributions = pension + disability + accident + labor_fund + sickness

    return {
        "pension_insurance_contribution": pension,
        "disability_insurance_contribution": disability,
        "accident_insurance_contribution": accident,
        "labor_fund_contribution": labor_fund,
        "sickness_insurance_contribution": sickness,
        "annual_social_contributions": annual_social_contributions,
    }
