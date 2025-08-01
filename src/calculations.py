import math
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE_PATH = os.path.join(BASE_DIR, 'dane_wejsciowe_kalkulator.json')

with open(DATA_FILE_PATH, 'r', encoding='utf-8') as f:
    CALCULATION_DATA = json.load(f)

CALCULATION_DATA['uop_zus_rates'] = {
    "pension": 0.0976, "disability": 0.0150, "sickness": 0.0245, "health": 0.09
}
CALCULATION_DATA['youth_relief_limit'] = 85528
CALCULATION_DATA['tax_thresholds']['tax_reducing_amount'] = 3600

def _get_float(data, key, default=0.0):
    """Safely gets a float value from a dictionary, returning a default if conversion fails."""
    try:
        return float(data.get(key, default))
    except (ValueError, TypeError):
        return default

def calculate_b2b_results(b2b_data):
    """
    Calculates all financial aspects for a B2B contract.

    Args:
        b2b_data (dict): A dictionary containing all B2B input parameters.

    Returns:
        dict: A dictionary with detailed B2B calculation results.
    """
    monthly_invoice_amount = _get_float(b2b_data, 'monthly_invoice_amount')
    annual_invoice_amount = monthly_invoice_amount * 12
    monthly_business_costs = _get_float(b2b_data, 'monthly_business_costs')
    annual_business_costs = monthly_business_costs * 12

    # ZUS
    zus_type = b2b_data.get('zus_type', 'full')
    zus_details = CALCULATION_DATA['zus_2025'][zus_type]
    
    # pension = pension, disability = disability, accident = accident, sickness = sickness, health = health, labor_fund = labor_fund
    pension_insurance_contribution = zus_details.get('pension', 0) * 12
    disability_insurance_contribution = zus_details.get('disability', 0) * 12
    accident_insurance_contribution = zus_details.get('accident', 0) * 12
    labor_fund_contribution = zus_details.get('labor_fund', 0) * 12
    sickness_insurance_contribution = zus_details.get('sickness', 0) * 12 if b2b_data.get('sickness_insurance') else 0
    
    annual_social_contributions = pension_insurance_contribution + disability_insurance_contribution + accident_insurance_contribution + labor_fund_contribution + sickness_insurance_contribution
    annual_health_contribution = zus_details['health'] * 12
    total_zus_contributions = annual_social_contributions + annual_health_contribution

    gross_income = annual_invoice_amount - annual_business_costs

    # Tax
    tax_form = b2b_data.get('tax_form', 'flat_tax')
    annual_tax = 0
    
    if tax_form == 'lump_sum_it':
        tax_base = annual_invoice_amount
        annual_tax = round(tax_base * CALCULATION_DATA['tax_thresholds']['lump_sum_it'])
    else:
        taxable_base = gross_income - annual_social_contributions
        
        if tax_form == 'flat_tax':
            health_contribution_deductible = min(annual_health_contribution, 12900)
            taxable_base -= health_contribution_deductible
        elif tax_form == 'tax_scale':
            taxable_base -= annual_health_contribution
        elif tax_form == 'ip_box':
            taxable_base -= annual_health_contribution

        rounded_taxable_base = round(taxable_base)
        
        tax_free_amount = CALCULATION_DATA['tax_thresholds']['tax_free_amount']
        tax_threshold = CALCULATION_DATA['tax_thresholds']['tax_scale'][0]['income']
        tax_first_threshold = 0
        tax_second_threshold = 0

        if tax_form == 'flat_tax':
            annual_tax = math.ceil(rounded_taxable_base * CALCULATION_DATA['tax_thresholds']['flat_tax'])
        elif tax_form == 'tax_scale':
            if rounded_taxable_base <= tax_free_amount:
                annual_tax = 0
            elif rounded_taxable_base <= tax_threshold:
                tax_first_threshold = math.ceil((rounded_taxable_base - tax_free_amount) * CALCULATION_DATA['tax_thresholds']['tax_scale'][0]['rate'])
                annual_tax = tax_first_threshold
            else:
                tax_first_threshold = math.ceil((tax_threshold - tax_free_amount) * CALCULATION_DATA['tax_thresholds']['tax_scale'][0]['rate'])
                tax_second_threshold = math.ceil((rounded_taxable_base - tax_threshold) * CALCULATION_DATA['tax_thresholds']['tax_scale'][1]['rate'])
                annual_tax = tax_first_threshold + tax_second_threshold
            
            tax_deductible_amount = annual_health_contribution * (7.75 / 9)
            annual_tax = math.ceil(max(0, annual_tax - tax_deductible_amount))
        elif tax_form == 'ip_box':
            annual_tax = math.ceil(rounded_taxable_base * CALCULATION_DATA['tax_thresholds']['ip_box'])
            tax_deductible_amount = annual_health_contribution * (7.75 / 9)
            annual_tax = math.ceil(max(0, annual_tax - tax_deductible_amount))

    if b2b_data.get('youth_relief', False) and annual_invoice_amount <= CALCULATION_DATA['youth_relief_limit']:
        annual_tax = 0

    daily_rate = monthly_invoice_amount / CALCULATION_DATA['general_data']['working_days_monthly']
    
    annual_custom_benefits = float(b2b_data.get('customBenefits', 0))

    company_benefits = b2b_data.get('companyBenefits', {})
    annual_company_benefits_value = 0
    for key, benefit in company_benefits.items():
        if benefit.get('enabled', False):
            if key == 'paidVacationDays':
                annual_company_benefits_value += float(benefit.get('days', 0)) * daily_rate
            elif key == 'paidSickDays':
                annual_company_benefits_value += float(benefit.get('days', 0)) * daily_rate * 0.8
            else:
                annual_company_benefits_value += float(benefit.get('value', 0))

    paid_vacation_days = float(company_benefits.get('paidVacationDays', {}).get('days', 0)) if company_benefits.get('paidVacationDays', {}).get('enabled') else 0
    paid_sick_days = float(company_benefits.get('paidSickDays', {}).get('days', 0)) if company_benefits.get('paidSickDays', {}).get('enabled') else 0
    
    unpaid_vacation_days = max(0, int(_get_float(b2b_data, 'vacation_days')) - paid_vacation_days)
    unpaid_sick_days = max(0, int(_get_float(b2b_data, 'sick_days', 0)) - paid_sick_days) 

    lost_revenue_vacation = unpaid_vacation_days * daily_rate
    lost_revenue_sickness = unpaid_sick_days * daily_rate * 0.8
    lost_revenue_stoppage = _get_float(b2b_data, 'stoppage_months') * monthly_invoice_amount
    
    total_lost_revenue = lost_revenue_vacation + lost_revenue_sickness + lost_revenue_stoppage

    annual_net_income = gross_income - total_zus_contributions - annual_tax - total_lost_revenue
    
    total_b2b_value = annual_net_income + annual_company_benefits_value + annual_custom_benefits

    calculation_steps = {
        'annual_revenue': annual_invoice_amount,
        'annual_business_costs': annual_business_costs,
        'gross_income': gross_income,
        'pension_insurance_contribution': pension_insurance_contribution,
        'disability_insurance_contribution': disability_insurance_contribution,
        'sickness_insurance_contribution': sickness_insurance_contribution,
        'accident_insurance_contribution': accident_insurance_contribution,
        'labor_fund_contribution': labor_fund_contribution,
        'annual_health_contribution': annual_health_contribution,
        'taxable_base': taxable_base if 'taxable_base' in locals() else tax_base,
        'tax_first_threshold': tax_first_threshold if 'tax_first_threshold' in locals() else (annual_tax if tax_form != 'tax_scale' else 0),
        'tax_second_threshold': tax_second_threshold if 'tax_second_threshold' in locals() else 0,
        'tax_deductible_amount': tax_deductible_amount if 'tax_deductible_amount' in locals() else 0,
        'annual_tax': annual_tax,
        'total_lost_revenue': total_lost_revenue
    }

    results = {
        "annual_revenue": annual_invoice_amount,
        "annual_business_costs": annual_business_costs,
        "annual_zus": total_zus_contributions,
        "annual_tax": annual_tax,
        "annual_lost_revenue": total_lost_revenue,
        "annual_net_income": annual_net_income,
        "annual_company_benefits_value": annual_company_benefits_value,
        "annual_custom_benefits_value": annual_custom_benefits,
        "total_annual_value": total_b2b_value,
        "monthly_net_income": total_b2b_value / 12
    }
    results['steps'] = calculation_steps
    return results

def calculate_uop_results(uop_data):
    """
    Calculates all financial aspects for an Employment Contract (UoP).

    Args:
        uop_data (dict): A dictionary containing all UoP input parameters.

    Returns:
        dict: A dictionary with detailed UoP calculation results.
    """
    monthly_gross_salary = _get_float(uop_data, 'monthly_gross_salary')
    deductible_cost_settings = uop_data.get('deductible_cost_settings', {'type': 'standard', 'creative_work_percentage': 0})
    deductible_cost_type = deductible_cost_settings.get('type', 'standard')
    creative_work_percentage = _get_float(deductible_cost_settings, 'creative_work_percentage', 0) / 100

    annual_gross_salary = monthly_gross_salary * 12
    uop_zus_rates = CALCULATION_DATA['uop_zus_rates']
    author_costs_limit = CALCULATION_DATA['tax_thresholds']['author_tax_deductible_costs_limit']

    annual_social_contributions = 0
    annual_health_contribution = 0
    annual_deductible_costs = 0
    annual_tax_base = 0
    annual_tax = 0
    
    annual_pension_contribution = 0
    annual_disability_contribution = 0
    annual_sickness_contribution = 0

    steps = {'monthly_calculations': []}
    cumulative_author_costs = 0

    for month in range(1, 13):
        monthly_pension_contribution = monthly_gross_salary * uop_zus_rates['pension']
        monthly_disability_contribution = monthly_gross_salary * uop_zus_rates['disability']
        monthly_sickness_contribution = monthly_gross_salary * uop_zus_rates['sickness']
        monthly_social_contributions = monthly_pension_contribution + monthly_disability_contribution + monthly_sickness_contribution
        
        annual_pension_contribution += monthly_pension_contribution
        annual_disability_contribution += monthly_disability_contribution
        annual_sickness_contribution += monthly_sickness_contribution

        health_contribution_base = monthly_gross_salary - monthly_social_contributions
        monthly_health_contribution = health_contribution_base * uop_zus_rates['health']

        monthly_deductible_costs = 0
        if deductible_cost_type == 'standard':
            monthly_deductible_costs = CALCULATION_DATA['tax_deductible_costs']['standard']
        elif deductible_cost_type == 'elevated':
            monthly_deductible_costs = CALCULATION_DATA['tax_deductible_costs']['elevated']
        elif deductible_cost_type == 'author_50':
            if cumulative_author_costs < author_costs_limit:
                creative_income = monthly_gross_salary * creative_work_percentage
                contributions_from_creative = creative_income * (uop_zus_rates['pension'] + uop_zus_rates['disability'] + uop_zus_rates['sickness'])
                author_costs_base = creative_income - contributions_from_creative
                
                potential_author_costs = author_costs_base * 0.5
                
                if cumulative_author_costs + potential_author_costs > author_costs_limit:
                    author_costs = author_costs_limit - cumulative_author_costs
                    standard_costs = CALCULATION_DATA['tax_deductible_costs']['standard']
                    monthly_deductible_costs = author_costs + standard_costs
                    cumulative_author_costs = author_costs_limit
                else:
                    monthly_deductible_costs = potential_author_costs
                    cumulative_author_costs += potential_author_costs
            else:
                monthly_deductible_costs = CALCULATION_DATA['tax_deductible_costs']['standard']
        
        if deductible_cost_type in ['standard', 'elevated']:
             annual_limit = CALCULATION_DATA['tax_deductible_costs'][f"{deductible_cost_type}_annual_limit"]
             if annual_deductible_costs + monthly_deductible_costs > annual_limit:
                 monthly_deductible_costs = max(0, annual_limit - annual_deductible_costs)
        elif deductible_cost_type == 'none': # none
            monthly_deductible_costs = 0

        monthly_tax_base = max(0, math.floor(monthly_gross_salary - monthly_social_contributions - monthly_deductible_costs))
        
        annual_social_contributions += monthly_social_contributions
        annual_health_contribution += monthly_health_contribution
        annual_deductible_costs += monthly_deductible_costs
        annual_tax_base += monthly_tax_base
        
        steps['monthly_calculations'].append({
            'month': month,
            'gross_salary': monthly_gross_salary,
            'social_contributions': monthly_social_contributions,
            'health_contribution': monthly_health_contribution,
            'deductible_costs': monthly_deductible_costs,
            'tax_base': monthly_tax_base
        })

    tax_free_amount = CALCULATION_DATA['tax_thresholds']['tax_free_amount']
    tax_threshold = CALCULATION_DATA['tax_thresholds']['tax_scale'][0]['income']
    tax_first_threshold = 0
    tax_second_threshold = 0
    
    if annual_tax_base > tax_free_amount:
        if annual_tax_base <= tax_threshold:
            tax_first_threshold = (annual_tax_base - tax_free_amount) * CALCULATION_DATA['tax_thresholds']['tax_scale'][0]['rate']
            annual_tax = tax_first_threshold
        else:
            tax_first_threshold = (tax_threshold - tax_free_amount) * CALCULATION_DATA['tax_thresholds']['tax_scale'][0]['rate']
            tax_second_threshold = (annual_tax_base - tax_threshold) * CALCULATION_DATA['tax_thresholds']['tax_scale'][1]['rate']
            annual_tax = tax_first_threshold + tax_second_threshold
    
    tax_deductible_amount = CALCULATION_DATA['tax_thresholds']['tax_reducing_amount']
    annual_tax -= tax_deductible_amount
    annual_tax = math.ceil(max(0, annual_tax))

    if uop_data.get('youth_relief', False) and annual_gross_salary <= CALCULATION_DATA['youth_relief_limit']:
        annual_tax = 0

    annual_net_income_on_hand = annual_gross_salary - annual_social_contributions - annual_health_contribution - annual_tax
    
    benefits_value = sum(CALCULATION_DATA['benefits'][b] for b in uop_data.get('selected_benefits', []) if b in CALCULATION_DATA['benefits'] and b != 'ppk')
    if 'ppk' in uop_data.get('selected_benefits', []):
        benefits_value += annual_gross_salary * CALCULATION_DATA['benefits']['ppk']
        
    daily_rate = monthly_gross_salary / CALCULATION_DATA['general_data']['working_days_monthly']
    paid_days_off_value = CALCULATION_DATA['uop_days_off']['vacation']['days'] * daily_rate
    
    total_uop_value = annual_net_income_on_hand + benefits_value + paid_days_off_value

    steps.update({
        'annual_gross_salary': annual_gross_salary,
        'annual_pension_contribution': annual_pension_contribution,
        'annual_disability_contribution': annual_disability_contribution,
        'annual_sickness_contribution': annual_sickness_contribution,
        'annual_health_contribution': annual_health_contribution,
        'annual_deductible_costs': annual_deductible_costs,
        'annual_tax_base': annual_tax_base,
        'tax_first_threshold': tax_first_threshold,
        'tax_second_threshold': tax_second_threshold,
        'tax_deductible_amount': tax_deductible_amount,
        'annual_tax': annual_tax,
        'benefits_value': benefits_value,
        'paid_days_off_value': paid_days_off_value
    })

    results = {
        "annual_gross_salary": annual_gross_salary,
        "annual_zus": annual_social_contributions + annual_health_contribution,
        "annual_tax": annual_tax,
        "annual_benefits_value": benefits_value,
        "annual_paid_days_off_value": paid_days_off_value,
        "annual_net_income": annual_net_income_on_hand,
        "total_annual_value": total_uop_value,
        "monthly_net_income": total_uop_value / 12,
    }
    results['steps'] = steps
    return results

def calculate_break_even(uop_total_value, b2b_base_data):
    """
    Iteratively finds the B2B invoice amount to match UoP total value.

    Args:
        uop_total_value (float): The total annual value of the UoP contract.
        b2b_base_data (dict): The base B2B input data.

    Returns:
        float: The monthly B2B invoice amount needed to break even, or -1 if not found.
    """
    start_range = int(_get_float(b2b_base_data, 'monthly_invoice_amount', 10000) * 0.5)
    end_range = 100000
    
    for test_monthly_invoice in range(start_range, end_range, 100):
        test_data = b2b_base_data.copy()
        test_data['monthly_invoice_amount'] = test_monthly_invoice
        b2b_results = calculate_b2b_results(test_data)
        if b2b_results['total_annual_value'] >= uop_total_value:
            return test_monthly_invoice
    return -1

def calculate_uop_break_even(b2b_total_value, uop_base_data):
    """
    Iteratively finds the UoP gross salary to match B2B total value.

    Args:
        b2b_total_value (float): The total annual value of the B2B contract.
        uop_base_data (dict): The base UoP input data.

    Returns:
        float: The monthly UoP gross salary needed to break even, or -1 if not found.
    """
    start_range = int(_get_float(uop_base_data, 'monthly_gross_salary', 5000) * 0.5)
    end_range = 50000

    for test_gross_salary in range(start_range, end_range, 100):
        test_data = uop_base_data.copy()
        test_data['monthly_gross_salary'] = test_gross_salary
        uop_results = calculate_uop_results(test_data)
        if uop_results['total_annual_value'] >= b2b_total_value:
            return test_gross_salary
    return -1

def get_calculation_data():
    """Returns the loaded calculation data."""
    return CALCULATION_DATA

def calculate_break_even_analysis(uop_data, b2b_base_data):
    """
    Performs a break-even analysis over a range of B2B invoice values.

    Args:
        uop_data (dict): UoP input data.
        b2b_base_data (dict): B2B input data.

    Returns:
        list: A list of dictionaries with B2B rates and net differences.
    """
    uop_gross_salary = _get_float(uop_data, 'monthly_gross_salary')
    uop_results = calculate_uop_results(uop_data)

    analysis_results = []
    start_b2b_rate = uop_gross_salary - 5000
    end_b2b_rate = uop_gross_salary + 15000

    for b2b_rate in range(int(start_b2b_rate), int(end_b2b_rate), 500):
        b2b_data = b2b_base_data.copy()
        b2b_data['monthly_invoice_amount'] = b2b_rate
        
        b2b_results = calculate_b2b_results(b2b_data)
        
        net_difference = b2b_results['total_annual_value'] - uop_results['total_annual_value']
        analysis_results.append({
            "b2b_rate": b2b_rate,
            "net_difference": net_difference
        })
        
    return analysis_results

def calculate_sensitivity_analysis(base_b2b_data, base_uop_data):
    """
    Performs a sensitivity analysis on B2B results based on key parameters.

    Args:
        base_b2b_data (dict): Base B2B input data.
        base_uop_data (dict): Base UoP input data.

    Returns:
        list: A list of dictionaries with parameters and their impact.
    """
    base_b2b_results = calculate_b2b_results(base_b2b_data)
    base_uop_results = calculate_uop_results(base_uop_data)

    sensitivity_params = {
        'monthly_business_costs': 0.20,
        'vacation_days': 5,
        'stoppage_months': 1
    }

    analysis_results = []

    for param, change in sensitivity_params.items():
        min_data = base_b2b_data.copy()
        if isinstance(change, float):
            min_data[param] = _get_float(min_data, param) * (1 - change)
        else:
            min_data[param] = _get_float(min_data, param) - change

        min_b2b_results = calculate_b2b_results(min_data)
        min_net_difference = min_b2b_results['total_annual_value'] - base_uop_results['total_annual_value']

        max_data = base_b2b_data.copy()
        if isinstance(change, float):
            max_data[param] = _get_float(max_data, param) * (1 + change)
        else:
            max_data[param] = _get_float(max_data, param) + change

        max_b2b_results = calculate_b2b_results(max_data)
        max_net_difference = max_b2b_results['total_annual_value'] - base_uop_results['total_annual_value']
        
        impact = max_net_difference - min_net_difference

        analysis_results.append({
            "parameter": param,
            "impact": impact
        })

    return analysis_results
