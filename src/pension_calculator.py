# src/pension_calculator.py
import math
import json
import os

# Base path for data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE_PATH = os.path.join(BASE_DIR, 'dane_wejsciowe_kalkulator.json')

with open(DATA_FILE_PATH, 'r', encoding='utf-8') as f:
    CALCULATION_DATA = json.load(f)

# Simulation assumptions
YEARS_TO_RETIREMENT = 30
YEARS_IN_RETIREMENT = 20
ANNUAL_RETURN_RATE = 0.045
B2B_NET_FACTOR = 0.70 
UOP_PENSION_RATE = 0.1952 
ZUS_DIVISOR = 264 
CAPITAL_MULTIPLIER = 1.2 

def calculate_pension_details(uop_monthly_gross_salary):
    """
    Calculates projected pensions for 2026 based on dynamic configuration.
    """
    if not uop_monthly_gross_salary or uop_monthly_gross_salary <= 0:
        return {}

    pension_limits = CALCULATION_DATA['pension_limits_2026']
    # Dynamic pension contribution for B2B from ZUS 2026 'full' config
    b2b_min_pension = CALCULATION_DATA['zus_2026']['full']['pension']

    # 1. Projected ZUS pensions
    uop_pension_capital = (uop_monthly_gross_salary * UOP_PENSION_RATE * 12 * YEARS_TO_RETIREMENT * CAPITAL_MULTIPLIER)
    uop_pension_monthly = uop_pension_capital / ZUS_DIVISOR
    
    b2b_pension_capital = (b2b_min_pension * 12 * YEARS_TO_RETIREMENT * CAPITAL_MULTIPLIER)
    b2b_pension_monthly = b2b_pension_capital / ZUS_DIVISOR
    
    pension_gap_monthly = max(0, uop_pension_monthly - b2b_pension_monthly)

    # 2. Required private capital
    required_private_capital = pension_gap_monthly * YEARS_IN_RETIREMENT * 12
    
    # 3. Required monthly savings
    if pension_gap_monthly > 0:
        q = 1 + (ANNUAL_RETURN_RATE / 12)
        n = YEARS_TO_RETIREMENT * 12
        required_monthly_savings = (required_private_capital * (q - 1)) / (q * (pow(q, n) - 1))
    else:
        required_monthly_savings = 0

    # 4. Optimal savings allocation (IKE -> IKZE -> Standard)
    # Using specific IKZE limit for B2B
    ike_limit = pension_limits['ike']
    ikze_limit = pension_limits['ikze_b2b']

    monthly_savings = required_monthly_savings
    ike_monthly = min(monthly_savings, ike_limit / 12)
    monthly_savings -= ike_monthly
    ikze_monthly = min(monthly_savings, ikze_limit / 12)
    monthly_savings -= ikze_monthly
    standard_monthly = monthly_savings

    # 5. B2B invoice increase
    invoice_increase = required_monthly_savings / B2B_NET_FACTOR

    return {
        "uop_pension_monthly": uop_pension_monthly,
        "b2b_pension_monthly": b2b_pension_monthly,
        "pension_gap_monthly": pension_gap_monthly,
        "required_monthly_savings": required_monthly_savings,
        "invoice_increase": invoice_increase,
        "savings_allocation": {
            "ike": ike_monthly,
            "ikze": ikze_monthly,
            "standard": standard_monthly
        }
    }
