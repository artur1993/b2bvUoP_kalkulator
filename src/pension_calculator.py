# src/pension_calculator.py
import math

# Assumptions and constants (can be moved to a configuration file)
IKE_LIMIT_2025 = 26019
IKZE_LIMIT_2025 = 10408
YEARS_TO_RETIREMENT = 30
YEARS_IN_RETIREMENT = 20
ANNUAL_RETURN_RATE = 0.045 # 4.5%
B2B_NET_FACTOR = 0.70 # Net factor for B2B
UOP_PENSION_RATE = 0.1952 # ZUS pension contribution rate
B2B_MINIMAL_PENSION_CONTRIBUTION = 610.44
ZUS_DIVISOR = 264 # Average ZUS indicator for pension calculation
CAPITAL_MULTIPLIER = 1.2 # ZUS capital multiplier

def calculate_pension_details(uop_monthly_gross_salary):
    """
    Calculates projected pensions, the gap, and the amount required to equalize.
    """
    if not uop_monthly_gross_salary or uop_monthly_gross_salary <= 0:
        return {}

    # 1. Projected ZUS pensions
    uop_pension_capital = (uop_monthly_gross_salary * UOP_PENSION_RATE * 12 * YEARS_TO_RETIREMENT * CAPITAL_MULTIPLIER)
    uop_pension_monthly = uop_pension_capital / ZUS_DIVISOR
    
    b2b_pension_capital = (B2B_MINIMAL_PENSION_CONTRIBUTION * 12 * YEARS_TO_RETIREMENT * CAPITAL_MULTIPLIER)
    b2b_pension_monthly = b2b_pension_capital / ZUS_DIVISOR
    
    pension_gap_monthly = max(0, uop_pension_monthly - b2b_pension_monthly)

    # 2. Required private capital
    required_private_capital = pension_gap_monthly * YEARS_IN_RETIREMENT * 12
    
    # 3. Required monthly savings (simplified installment formula)
    if pension_gap_monthly > 0:
        q = 1 + (ANNUAL_RETURN_RATE / 12)
        n = YEARS_TO_RETIREMENT * 12
        required_monthly_savings = (required_private_capital * (q - 1)) / (q * (pow(q, n) - 1))
    else:
        required_monthly_savings = 0

    # 4. Optimal savings allocation (IKE -> IKZE -> Standard)
    monthly_savings = required_monthly_savings
    ike_monthly = min(monthly_savings, IKE_LIMIT_2025 / 12)
    monthly_savings -= ike_monthly
    ikze_monthly = min(monthly_savings, IKZE_LIMIT_2025 / 12)
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
