import math
from typing import Dict, Any, List
from src.config import config_manager

# Helper rates for UoP (employee side)
UOP_ZUS_RATES = {
    "pension": 0.0976, 
    "disability": 0.0150, 
    "sickness": 0.0245, 
    "health": 0.09
}

def _calculate_progressive_tax(taxable_base: float, config: Dict[str, Any]) -> float:
    tax_threshold = config['tax_thresholds']['tax_scale'][0]['income']
    tax_reducing = config['tax_thresholds']['tax_reducing_amount']

    if taxable_base <= tax_threshold:
        return max(0, math.ceil(taxable_base * 0.12) - tax_reducing)

    return math.ceil((tax_threshold * 0.12) - tax_reducing + (taxable_base - tax_threshold) * 0.32)

def calculate_b2b_results(b2b_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculates all financial aspects for a B2B contract for 2026."""
    config = config_manager.get_config()
    monthly_invoice_amount = float(b2b_data.get('monthly_invoice_amount', 0))
    monthly_business_costs = float(b2b_data.get('monthly_business_costs', 0))
    annual_business_costs = monthly_business_costs * 12
    
    # 1. Lost Revenue Calculation
    daily_rate = monthly_invoice_amount / config['general_data']['working_days_monthly']
    company_benefits = b2b_data.get('companyBenefits') or {}
    
    paid_vacation_days = float(company_benefits.get('paidVacationDays', {}).get('days', 0)) if company_benefits.get('paidVacationDays', {}).get('enabled') else 0
    paid_sick_days = float(company_benefits.get('paidSickDays', {}).get('days', 0)) if company_benefits.get('paidSickDays', {}).get('enabled') else 0
    
    unpaid_vacation_days = max(0, int(b2b_data.get('vacation_days', 0)) - paid_vacation_days)
    unpaid_sick_days = max(0, int(b2b_data.get('sick_days', 0)) - paid_sick_days) 

    lost_revenue_vacation = unpaid_vacation_days * daily_rate
    lost_revenue_sickness = unpaid_sick_days * daily_rate * 0.8
    lost_revenue_stoppage = float(b2b_data.get('stoppage_months', 0)) * monthly_invoice_amount
    total_lost_revenue = lost_revenue_vacation + lost_revenue_sickness + lost_revenue_stoppage

    # Corrected Annual Revenue
    annual_invoice_amount = (monthly_invoice_amount * 12) - total_lost_revenue

    # 2. ZUS Social Contributions
    zus_type = b2b_data.get('zus_type', 'full')
    zus_details = config['zus_2026'][zus_type]
    
    pension_insurance_contribution = zus_details.get('pension', 0) * 12
    disability_insurance_contribution = zus_details.get('disability', 0) * 12
    accident_insurance_contribution = zus_details.get('accident', 0) * 12
    labor_fund_contribution = zus_details.get('labor_fund', 0) * 12
    sickness_insurance_contribution = zus_details.get('sickness', 0) * 12 if b2b_data.get('sickness_insurance') else 0
    
    annual_social_contributions = pension_insurance_contribution + disability_insurance_contribution + accident_insurance_contribution + labor_fund_contribution + sickness_insurance_contribution

    # 3. Health Contribution
    tax_form = b2b_data.get('tax_form', 'lump_sum_it')
    minimum_health_annual = config['zus_2026']['minimum_health_annual_2026']
    
    if tax_form == 'tax_scale':
        income_for_health = max(0, annual_invoice_amount - annual_business_costs - annual_social_contributions)
        annual_health_contribution = max(minimum_health_annual, income_for_health * 0.09)
    elif tax_form == 'flat_tax':
        income_for_health = max(0, annual_invoice_amount - annual_business_costs - annual_social_contributions)
        annual_health_contribution = max(minimum_health_annual, income_for_health * 0.049)
    elif tax_form == 'lump_sum_it':
        revenue = annual_invoice_amount
        thresholds = config['zus_2026']['health_lump_sum_thresholds']
        if revenue <= thresholds[0]['limit']:
            monthly_health = thresholds[0]['contribution']
        elif revenue <= thresholds[1]['limit']:
            monthly_health = thresholds[1]['contribution']
        else:
            monthly_health = thresholds[2]['contribution']
        annual_health_contribution = monthly_health * 12
    else:
        annual_health_contribution = minimum_health_annual

    total_zus_contributions = annual_social_contributions + annual_health_contribution

    # 4. Taxes
    annual_tax = 0
    if tax_form == 'lump_sum_it':
        tax_base = max(0, annual_invoice_amount - (annual_health_contribution * 0.5) - annual_social_contributions)
        annual_tax = round(tax_base * config['tax_thresholds']['lump_sum_it'])
    else:
        income = annual_invoice_amount - annual_business_costs - annual_social_contributions
        if tax_form == 'flat_tax':
            health_deduction_limit = config['tax_thresholds']['health_contribution_deduction_limit_flat_tax']
            income -= min(annual_health_contribution, health_deduction_limit)
        
        taxable_base = income

        if tax_form == 'flat_tax':
            annual_tax = math.ceil(max(0, taxable_base) * config['tax_thresholds']['flat_tax'])
        elif tax_form == 'tax_scale':
            annual_tax = _calculate_progressive_tax(taxable_base, config)
        elif tax_form == 'ip_box':
            annual_tax = math.ceil(max(0, taxable_base) * config['tax_thresholds']['ip_box'])

    annual_net_income = annual_invoice_amount - annual_business_costs - total_zus_contributions - annual_tax
    
    # Benefits
    annual_custom_benefits = float(b2b_data.get('customBenefits', 0))
    annual_company_benefits_value = 0
    for key, benefit in company_benefits.items():
        if benefit.get('enabled', False):
            if key == 'paidVacationDays':
                annual_company_benefits_value += float(benefit.get('days', 0)) * daily_rate
            elif key == 'paidSickDays':
                annual_company_benefits_value += float(benefit.get('days', 0)) * daily_rate * 0.8
            else:
                annual_company_benefits_value += float(benefit.get('value', 0))

    total_b2b_value = annual_net_income + annual_company_benefits_value + annual_custom_benefits

    return {
        "annual_revenue": annual_invoice_amount + total_lost_revenue,
        "annual_business_costs": annual_business_costs,
        "annual_zus": total_zus_contributions,
        "annual_tax": annual_tax,
        "annual_lost_revenue": total_lost_revenue,
        "annual_net_income": annual_net_income,
        "annual_company_benefits_value": annual_company_benefits_value,
        "annual_custom_benefits_value": annual_custom_benefits,
        "total_annual_value": total_b2b_value,
        "monthly_net_income": total_b2b_value / 12,
        "steps": {
            "annual_social_contributions": annual_social_contributions,
            "annual_health_contribution": annual_health_contribution,
            "annual_tax": annual_tax
        }
    }

def calculate_uop_results(uop_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculates all financial aspects for an Employment Contract (UoP) for 2026."""
    config = config_manager.get_config()
    monthly_gross_salary = float(uop_data.get('monthly_gross_salary', 0))
    deductible_cost_settings = uop_data.get('deductible_cost_settings', {})
    deductible_cost_type = deductible_cost_settings.get('type', 'standard')
    creative_work_percentage = float(deductible_cost_settings.get('creative_work_percentage', 0)) / 100

    thirty_times_limit = config['zus_2026']['thirty_times_limit_uop']
    youth_relief_limit = config['tax_thresholds']['youth_relief_limit']
    author_costs_limit = config['tax_thresholds']['author_tax_deductible_costs_limit']

    annual_social_contributions = 0
    annual_health_contribution = 0
    annual_deductible_costs = 0
    annual_tax_base = 0
    annual_tax_base_without_ppk_employer = 0
    annual_ppk_employee_contribution = 0
    annual_ppk_employer_contribution = 0
    cumulative_gross = 0
    cumulative_author_costs = 0
    monthly_calculations = []
    selected_benefits = uop_data.get('selected_benefits', [])
    ppk_selected = 'ppk' in selected_benefits
    ppk_rates = config.get('ppk', {})

    for month in range(1, 13):
        if cumulative_gross >= thirty_times_limit:
            monthly_pension = 0
            monthly_disability = 0
        elif cumulative_gross + monthly_gross_salary > thirty_times_limit:
            base_for_pension = thirty_times_limit - cumulative_gross
            monthly_pension = base_for_pension * UOP_ZUS_RATES['pension']
            monthly_disability = base_for_pension * UOP_ZUS_RATES['disability']
        else:
            monthly_pension = monthly_gross_salary * UOP_ZUS_RATES['pension']
            monthly_disability = monthly_gross_salary * UOP_ZUS_RATES['disability']
        
        monthly_sickness = monthly_gross_salary * UOP_ZUS_RATES['sickness']
        monthly_social = monthly_pension + monthly_disability + monthly_sickness
        
        cumulative_gross += monthly_gross_salary
        annual_social_contributions += monthly_social

        health_base = monthly_gross_salary - monthly_social
        monthly_health_contribution = health_base * UOP_ZUS_RATES['health']
        annual_health_contribution += monthly_health_contribution

        monthly_costs = 0
        if deductible_cost_type == 'standard':
            monthly_costs = config['tax_deductible_costs']['standard']
        elif deductible_cost_type == 'elevated':
            monthly_costs = config['tax_deductible_costs']['elevated']
        elif deductible_cost_type == 'author_50':
            if cumulative_author_costs < author_costs_limit:
                creative_income = monthly_gross_salary * creative_work_percentage
                author_costs_base = creative_income - (monthly_social * creative_work_percentage)
                potential_costs = author_costs_base * 0.5
                if cumulative_author_costs + potential_costs > author_costs_limit:
                    monthly_costs = author_costs_limit - cumulative_author_costs
                    cumulative_author_costs = author_costs_limit
                else:
                    monthly_costs = potential_costs
                    cumulative_author_costs += potential_costs
            else:
                monthly_costs = config['tax_deductible_costs']['standard']
        
        annual_deductible_costs += monthly_costs
        monthly_ppk_employee = monthly_gross_salary * ppk_rates.get('employee_rate', 0) if ppk_selected else 0
        monthly_ppk_employer = monthly_gross_salary * ppk_rates.get('employer_rate', 0) if ppk_selected else 0
        annual_ppk_employee_contribution += monthly_ppk_employee
        annual_ppk_employer_contribution += monthly_ppk_employer

        monthly_tax_base_without_ppk_employer = max(0, monthly_gross_salary - monthly_social - monthly_costs - monthly_ppk_employee)
        monthly_tax_base = monthly_tax_base_without_ppk_employer + monthly_ppk_employer
        annual_tax_base += monthly_tax_base
        annual_tax_base_without_ppk_employer += monthly_tax_base_without_ppk_employer
        
        monthly_calculations.append({
            "month": month,
            "deductible_costs": monthly_costs,
            "tax_base": monthly_tax_base,
            "ppk_employee_contribution": monthly_ppk_employee,
            "ppk_employer_contribution": monthly_ppk_employer
        })

    if uop_data.get('youth_relief', False):
        annual_tax_base = max(0, annual_tax_base - youth_relief_limit)
        annual_tax_base_without_ppk_employer = max(0, annual_tax_base_without_ppk_employer - youth_relief_limit)

    annual_tax = _calculate_progressive_tax(annual_tax_base, config)
    annual_tax_without_ppk_employer = _calculate_progressive_tax(annual_tax_base_without_ppk_employer, config)

    annual_net = cumulative_gross - annual_social_contributions - annual_health_contribution - annual_tax - annual_ppk_employee_contribution
    
    benefits_value = sum(config['benefits'][b] for b in selected_benefits if b in config['benefits'])
    annual_ppk_employer_net = 0
    if ppk_selected:
        # Uproszczenie: PIT od dopłaty pracodawcy to różnica podatku z/bez tej dopłaty.
        ppk_employer_tax = max(0, annual_tax - annual_tax_without_ppk_employer)
        annual_ppk_employer_net = max(0, annual_ppk_employer_contribution - ppk_employer_tax)
        benefits_value += annual_ppk_employer_net
        
    total_uop_value = annual_net + benefits_value

    return {
        "annual_gross_salary": cumulative_gross,
        "annual_zus": annual_social_contributions + annual_health_contribution,
        "annual_tax": annual_tax,
        "annual_benefits_value": benefits_value,
        "annual_net_income": annual_net,
        "total_annual_value": total_uop_value,
        "monthly_net_income": total_uop_value / 12,
        "steps": {
            "annual_deductible_costs": annual_deductible_costs,
            "annual_ppk_employee_contribution": annual_ppk_employee_contribution,
            "annual_ppk_employer_contribution": annual_ppk_employer_contribution,
            "annual_ppk_employer_net": annual_ppk_employer_net,
            "monthly_calculations": monthly_calculations
        }
    }

def calculate_break_even(uop_total_value: float, b2b_base_data: Dict[str, Any]) -> float:
    start_range = int(float(b2b_base_data.get('monthly_invoice_amount', 10000)) * 0.5)
    for test_invoice in range(start_range, 200000, 100):
        test_data = b2b_base_data.copy()
        test_data['monthly_invoice_amount'] = test_invoice
        if calculate_b2b_results(test_data)['total_annual_value'] >= uop_total_value:
            return float(test_invoice)
    return -1.0

def calculate_uop_break_even(b2b_total_value: float, uop_base_data: Dict[str, Any]) -> float:
    start_range = int(float(uop_base_data.get('monthly_gross_salary', 5000)) * 0.5)
    for test_gross in range(start_range, 100000, 100):
        test_data = uop_base_data.copy()
        test_data['monthly_gross_salary'] = test_gross
        if calculate_uop_results(test_data)['total_annual_value'] >= b2b_total_value:
            return float(test_gross)
    return -1.0

def calculate_break_even_analysis(uop_data: Dict[str, Any], b2b_base_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    uop_results = calculate_uop_results(uop_data)
    analysis = []
    base_rate = float(uop_data.get('monthly_gross_salary', 0))
    for b2b_rate in range(int(base_rate * 0.8), int(base_rate * 2.5), 500):
        b2b_data = b2b_base_data.copy()
        b2b_data['monthly_invoice_amount'] = b2b_rate
        b2b_res = calculate_b2b_results(b2b_data)
        analysis.append({"b2b_rate": b2b_rate, "net_difference": b2b_res['total_annual_value'] - uop_results['total_annual_value']})
    return analysis
