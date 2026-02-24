import math
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE_PATH = os.path.join(BASE_DIR, 'dane_wejsciowe_kalkulator.json')

with open(DATA_FILE_PATH, 'r', encoding='utf-8') as f:
    CALCULATION_DATA = json.load(f)

# Helper rates for UoP (employee side)
UOP_ZUS_RATES = {
    "pension": 0.0976, 
    "disability": 0.0150, 
    "sickness": 0.0245, 
    "health": 0.09
}

def _get_float(data, key, default=0.0):
    """Safely gets a float value from a dictionary, returning a default if conversion fails."""
    try:
        return float(data.get(key, default))
    except (ValueError, TypeError):
        return default

def calculate_b2b_results(b2b_data):
    """
    Calculates all financial aspects for a B2B contract for 2026.
    """
    monthly_invoice_amount = _get_float(b2b_data, 'monthly_invoice_amount')
    monthly_business_costs = _get_float(b2b_data, 'monthly_business_costs')
    annual_business_costs = monthly_business_costs * 12
    
    # 1. Lost Revenue Calculation (First)
    daily_rate = monthly_invoice_amount / CALCULATION_DATA['general_data']['working_days_monthly']
    company_benefits = b2b_data.get('companyBenefits', {})
    
    paid_vacation_days = float(company_benefits.get('paidVacationDays', {}).get('days', 0)) if company_benefits.get('paidVacationDays', {}).get('enabled') else 0
    paid_sick_days = float(company_benefits.get('paidSickDays', {}).get('days', 0)) if company_benefits.get('paidSickDays', {}).get('enabled') else 0
    
    unpaid_vacation_days = max(0, int(_get_float(b2b_data, 'vacation_days')) - paid_vacation_days)
    unpaid_sick_days = max(0, int(_get_float(b2b_data, 'sick_days', 0)) - paid_sick_days) 

    lost_revenue_vacation = unpaid_vacation_days * daily_rate
    lost_revenue_sickness = unpaid_sick_days * daily_rate * 0.8
    lost_revenue_stoppage = _get_float(b2b_data, 'stoppage_months') * monthly_invoice_amount
    total_lost_revenue = lost_revenue_vacation + lost_revenue_sickness + lost_revenue_stoppage

    # Corrected Annual Revenue
    annual_invoice_amount = (monthly_invoice_amount * 12) - total_lost_revenue

    # 2. ZUS Social Contributions
    zus_type = b2b_data.get('zus_type', 'full')
    zus_details = CALCULATION_DATA['zus_2026'][zus_type]
    
    pension_insurance_contribution = zus_details.get('pension', 0) * 12
    disability_insurance_contribution = zus_details.get('disability', 0) * 12
    accident_insurance_contribution = zus_details.get('accident', 0) * 12
    labor_fund_contribution = zus_details.get('labor_fund', 0) * 12
    sickness_insurance_contribution = zus_details.get('sickness', 0) * 12 if b2b_data.get('sickness_insurance') else 0
    
    annual_social_contributions = pension_insurance_contribution + disability_insurance_contribution + accident_insurance_contribution + labor_fund_contribution + sickness_insurance_contribution

    # 3. Health Contribution (Polski Ład 2026)
    tax_form = b2b_data.get('tax_form', 'lump_sum_it')
    min_health = CALCULATION_DATA['zus_2026']['minimum_health_contribution']
    
    if tax_form == 'tax_scale':
        income_for_health = max(0, annual_invoice_amount - annual_business_costs - annual_social_contributions)
        annual_health_contribution = max(min_health * 12, income_for_health * 0.09)
    elif tax_form == 'flat_tax':
        income_for_health = max(0, annual_invoice_amount - annual_business_costs - annual_social_contributions)
        annual_health_contribution = max(min_health * 12, income_for_health * 0.049)
    elif tax_form == 'lump_sum_it':
        revenue = annual_invoice_amount
        thresholds = CALCULATION_DATA['zus_2026']['health_lump_sum_thresholds']
        if revenue <= thresholds[0]['limit']:
            monthly_health = thresholds[0]['contribution']
        elif revenue <= thresholds[1]['limit']:
            monthly_health = thresholds[1]['contribution']
        else:
            monthly_health = thresholds[2]['contribution']
        annual_health_contribution = monthly_health * 12
    else: # ip_box or other
        annual_health_contribution = min_health * 12

    total_zus_contributions = annual_social_contributions + annual_health_contribution

    # 4. Taxes
    annual_tax = 0
    youth_relief_limit = CALCULATION_DATA['tax_thresholds']['youth_relief_limit']
    
    if tax_form == 'lump_sum_it':
        # Deduction: 50% health + 100% social
        tax_base = max(0, annual_invoice_amount - (annual_health_contribution * 0.5) - annual_social_contributions)
        if b2b_data.get('youth_relief', False):
            taxable_above_relief = max(0, tax_base - youth_relief_limit)
            tax_base = taxable_above_relief
        annual_tax = round(tax_base * CALCULATION_DATA['tax_thresholds']['lump_sum_it'])
    else:
        # Scale or Flat
        income = annual_invoice_amount - annual_business_costs - annual_social_contributions
        if tax_form == 'flat_tax':
            health_deduction_limit = CALCULATION_DATA['tax_thresholds']['health_contribution_deduction_limit_flat_tax']
            income -= min(annual_health_contribution, health_deduction_limit)
        
        if b2b_data.get('youth_relief', False):
            taxable_base = max(0, income - youth_relief_limit)
        else:
            taxable_base = income

        if tax_form == 'flat_tax':
            annual_tax = math.ceil(max(0, taxable_base) * CALCULATION_DATA['tax_thresholds']['flat_tax'])
        elif tax_form == 'tax_scale':
            tax_free_amount = CALCULATION_DATA['tax_thresholds']['tax_free_amount']
            tax_threshold = CALCULATION_DATA['tax_thresholds']['tax_scale'][0]['income']
            
            # Note: tax_scale calculation uses tax_reducing_amount from config
            if taxable_base <= tax_threshold:
                annual_tax = max(0, math.ceil(taxable_base * 0.12) - CALCULATION_DATA['tax_thresholds']['tax_reducing_amount'])
            else:
                first_part = (tax_threshold * 0.12) - CALCULATION_DATA['tax_thresholds']['tax_reducing_amount']
                second_part = (taxable_base - tax_threshold) * 0.32
                annual_tax = math.ceil(first_part + second_part)
        elif tax_form == 'ip_box':
            annual_tax = math.ceil(max(0, taxable_base) * CALCULATION_DATA['tax_thresholds']['ip_box'])

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
        "steps": {} # Simplified for brevity, can be expanded if needed
    }

def calculate_uop_results(uop_data):
    """
    Calculates all financial aspects for an Employment Contract (UoP) for 2026.
    """
    monthly_gross_salary = _get_float(uop_data, 'monthly_gross_salary')
    deductible_cost_settings = uop_data.get('deductible_cost_settings', {'type': 'standard', 'creative_work_percentage': 0})
    deductible_cost_type = deductible_cost_settings.get('type', 'standard')
    creative_work_percentage = _get_float(deductible_cost_settings, 'creative_work_percentage', 0) / 100

    thirty_times_limit = CALCULATION_DATA['zus_2026']['thirty_times_limit_uop']
    youth_relief_limit = CALCULATION_DATA['tax_thresholds']['youth_relief_limit']
    author_costs_limit = CALCULATION_DATA['tax_thresholds']['author_tax_deductible_costs_limit']

    annual_social_contributions = 0
    annual_health_contribution = 0
    annual_deductible_costs = 0
    annual_tax_base = 0
    cumulative_gross = 0
    cumulative_author_costs = 0

    for month in range(1, 13):
        # 30-times limit check
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
        annual_health_contribution += health_base * UOP_ZUS_RATES['health']

        # Costs
        monthly_costs = 0
        if deductible_cost_type == 'standard':
            monthly_costs = CALCULATION_DATA['tax_deductible_costs']['standard']
        elif deductible_cost_type == 'elevated':
            monthly_costs = CALCULATION_DATA['tax_deductible_costs']['elevated']
        elif deductible_cost_type == 'author_50':
            if cumulative_author_costs < author_costs_limit:
                creative_income = monthly_gross_salary * creative_work_percentage
                # Simplified: social contributions proportional to creative income
                author_costs_base = creative_income - (monthly_social * (creative_income / monthly_gross_salary))
                potential_costs = author_costs_base * 0.5
                if cumulative_author_costs + potential_costs > author_costs_limit:
                    monthly_costs = author_costs_limit - cumulative_author_costs
                    cumulative_author_costs = author_costs_limit
                else:
                    monthly_costs = potential_costs
                    cumulative_author_costs += potential_costs
            else:
                monthly_costs = CALCULATION_DATA['tax_deductible_costs']['standard']
        
        annual_deductible_costs += monthly_costs
        annual_tax_base += max(0, monthly_gross_salary - monthly_social - monthly_costs)

    # Tax Calculation
    if uop_data.get('youth_relief', False):
        annual_tax_base = max(0, annual_tax_base - (youth_relief_limit))

    tax_threshold = CALCULATION_DATA['tax_thresholds']['tax_scale'][0]['income']
    tax_reducing = CALCULATION_DATA['tax_thresholds']['tax_reducing_amount']
    
    if annual_tax_base <= tax_threshold:
        annual_tax = max(0, math.ceil(annual_tax_base * 0.12) - tax_reducing)
    else:
        annual_tax = math.ceil((tax_threshold * 0.12) - tax_reducing + (annual_tax_base - tax_threshold) * 0.32)

    annual_net = cumulative_gross - annual_social_contributions - annual_health_contribution - annual_tax
    
    # Benefits & Vacation
    benefits_value = sum(CALCULATION_DATA['benefits'][b] for b in uop_data.get('selected_benefits', []) if b in CALCULATION_DATA['benefits'] and b != 'ppk')
    if 'ppk' in uop_data.get('selected_benefits', []):
        benefits_value += cumulative_gross * CALCULATION_DATA['benefits']['ppk']
        
    daily_rate = monthly_gross_salary / CALCULATION_DATA['general_data']['working_days_monthly']
    paid_days_off_value = CALCULATION_DATA['uop_days_off']['vacation']['days'] * daily_rate
    
    total_uop_value = annual_net + benefits_value + paid_days_off_value

    return {
        "annual_gross_salary": cumulative_gross,
        "annual_zus": annual_social_contributions + annual_health_contribution,
        "annual_tax": annual_tax,
        "annual_benefits_value": benefits_value,
        "annual_paid_days_off_value": paid_days_off_value,
        "annual_net_income": annual_net,
        "total_annual_value": total_uop_value,
        "monthly_net_income": total_uop_value / 12,
        "steps": {}
    }

def calculate_break_even(uop_total_value, b2b_base_data):
    start_range = int(_get_float(b2b_base_data, 'monthly_invoice_amount', 10000) * 0.5)
    for test_invoice in range(start_range, 200000, 100):
        test_data = b2b_base_data.copy()
        test_data['monthly_invoice_amount'] = test_invoice
        if calculate_b2b_results(test_data)['total_annual_value'] >= uop_total_value:
            return test_invoice
    return -1

def calculate_uop_break_even(b2b_total_value, uop_base_data):
    start_range = int(_get_float(uop_base_data, 'monthly_gross_salary', 5000) * 0.5)
    for test_gross in range(start_range, 100000, 100):
        test_data = uop_base_data.copy()
        test_data['monthly_gross_salary'] = test_gross
        if calculate_uop_results(test_data)['total_annual_value'] >= b2b_total_value:
            return test_gross
    return -1

def get_calculation_data():
    return CALCULATION_DATA

def calculate_break_even_analysis(uop_data, b2b_base_data):
    uop_results = calculate_uop_results(uop_data)
    analysis = []
    base_rate = _get_float(uop_data, 'monthly_gross_salary')
    for b2b_rate in range(int(base_rate * 0.8), int(base_rate * 2.5), 500):
        b2b_data = b2b_base_data.copy()
        b2b_data['monthly_invoice_amount'] = b2b_rate
        b2b_res = calculate_b2b_results(b2b_data)
        analysis.append({"b2b_rate": b2b_rate, "net_difference": b2b_res['total_annual_value'] - uop_results['total_annual_value']})
    return analysis

def calculate_sensitivity_analysis(base_b2b_data, base_uop_data):
    uop_total = calculate_uop_results(base_uop_data)['total_annual_value']
    params = {'monthly_business_costs': 500, 'vacation_days': 5, 'stoppage_months': 1}
    analysis = []
    for param, change in params.items():
        d = base_b2b_data.copy()
        d[param] = _get_float(d, param) + change
        res = calculate_b2b_results(d)
        analysis.append({"parameter": param, "impact": res['total_annual_value'] - calculate_b2b_results(base_b2b_data)['total_annual_value']})
    return analysis
