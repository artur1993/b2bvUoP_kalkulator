import math
from typing import Dict, Any, List
from src.config import config_manager
from src.domain.b2b.aggregate import assemble_b2b_results

def _calculate_progressive_tax(taxable_base: float, config: Dict[str, Any]) -> float:
    tax_threshold = config['tax_thresholds']['tax_scale'][0]['income']
    tax_reducing = config['tax_thresholds']['tax_reducing_amount']

    if taxable_base <= tax_threshold:
        return max(0, math.ceil(taxable_base * 0.12) - tax_reducing)

    return math.ceil((tax_threshold * 0.12) - tax_reducing + (taxable_base - tax_threshold) * 0.32)

def compute_solidarity_tax(annual_taxable_base: float, config: Dict[str, Any]) -> float:
    """Returns 4% of taxable base over 1M PLN, else 0."""
    solidarity_tax = config['tax_thresholds']['solidarity_tax']
    threshold = solidarity_tax['threshold']
    rate = solidarity_tax['rate']

    return max(0, annual_taxable_base - threshold) * rate

def calculate_b2b_results(b2b_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculates all financial aspects for a B2B contract for 2026."""
    config = config_manager.get_config()
    return assemble_b2b_results(
        b2b_data,
        config,
        _calculate_progressive_tax,
        compute_solidarity_tax,
    )

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
    regulatory_rates = config['regulatory_rates']

    for month in range(1, 13):
        if cumulative_gross >= thirty_times_limit:
            monthly_pension = 0
            monthly_disability = 0
        elif cumulative_gross + monthly_gross_salary > thirty_times_limit:
            base_for_pension = thirty_times_limit - cumulative_gross
            monthly_pension = base_for_pension * regulatory_rates['uop_pension_employee']
            monthly_disability = base_for_pension * regulatory_rates['uop_disability_employee']
        else:
            monthly_pension = monthly_gross_salary * regulatory_rates['uop_pension_employee']
            monthly_disability = monthly_gross_salary * regulatory_rates['uop_disability_employee']
        
        monthly_sickness = monthly_gross_salary * regulatory_rates['uop_sickness_employee']
        monthly_social = monthly_pension + monthly_disability + monthly_sickness
        
        cumulative_gross += monthly_gross_salary
        annual_social_contributions += monthly_social

        health_base = monthly_gross_salary - monthly_social
        monthly_health_contribution = health_base * regulatory_rates['uop_health_employee']
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
                potential_costs = author_costs_base * regulatory_rates['author_tax_deductible_cost_share']
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
    annual_solidarity_tax = compute_solidarity_tax(annual_tax_base, config)
    annual_solidarity_tax_without_ppk_employer = compute_solidarity_tax(annual_tax_base_without_ppk_employer, config)
    annual_tax += annual_solidarity_tax
    annual_tax_without_ppk_employer += annual_solidarity_tax_without_ppk_employer

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
        "annual_solidarity_tax": annual_solidarity_tax,
        "annual_benefits_value": benefits_value,
        "annual_net_income": annual_net,
        "total_annual_value": total_uop_value,
        "monthly_net_income": total_uop_value / 12,
        "steps": {
            "annual_deductible_costs": annual_deductible_costs,
            "annual_ppk_employee_contribution": annual_ppk_employee_contribution,
            "annual_ppk_employer_contribution": annual_ppk_employer_contribution,
            "annual_ppk_employer_net": annual_ppk_employer_net,
            "annual_solidarity_tax": annual_solidarity_tax,
            "monthly_calculations": monthly_calculations
        }
    }

def calculate_break_even(uop_total_value: float, b2b_base_data: Dict[str, Any]) -> float:
    config = config_manager.get_config()
    start_multiplier = config['regulatory_rates']['break_even_start_multiplier']
    start_range = int(float(b2b_base_data.get('monthly_invoice_amount', 10000)) * start_multiplier)
    for test_invoice in range(start_range, 200000, 100):
        test_data = b2b_base_data.copy()
        test_data['monthly_invoice_amount'] = test_invoice
        if calculate_b2b_results(test_data)['total_annual_value'] >= uop_total_value:
            return float(test_invoice)
    return -1.0

def calculate_uop_break_even(b2b_total_value: float, uop_base_data: Dict[str, Any]) -> float:
    config = config_manager.get_config()
    start_multiplier = config['regulatory_rates']['break_even_start_multiplier']
    start_range = int(float(uop_base_data.get('monthly_gross_salary', 5000)) * start_multiplier)
    for test_gross in range(start_range, 100000, 100):
        test_data = uop_base_data.copy()
        test_data['monthly_gross_salary'] = test_gross
        if calculate_uop_results(test_data)['total_annual_value'] >= b2b_total_value:
            return float(test_gross)
    return -1.0

def calculate_break_even_analysis(uop_data: Dict[str, Any], b2b_base_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    config = config_manager.get_config()
    regulatory_rates = config['regulatory_rates']
    uop_results = calculate_uop_results(uop_data)
    analysis = []
    base_rate = float(uop_data.get('monthly_gross_salary', 0))
    min_rate = int(base_rate * regulatory_rates['break_even_analysis_min_multiplier'])
    max_rate = int(base_rate * regulatory_rates['break_even_analysis_max_multiplier'])
    for b2b_rate in range(min_rate, max_rate, 500):
        b2b_data = b2b_base_data.copy()
        b2b_data['monthly_invoice_amount'] = b2b_rate
        b2b_res = calculate_b2b_results(b2b_data)
        analysis.append({"b2b_rate": b2b_rate, "net_difference": b2b_res['total_annual_value'] - uop_results['total_annual_value']})
    return analysis
