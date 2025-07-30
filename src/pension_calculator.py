# Nowy plik: src/pension_calculator.py
import math

# Założenia i stałe (mogą być przeniesione do pliku konfiguracyjnego)
IKE_LIMIT_2025 = 26019
IKZE_LIMIT_2025 = 10408
YEARS_TO_RETIREMENT = 30
YEARS_IN_RETIREMENT = 20
ANNUAL_RETURN_RATE = 0.045 # 4.5%
B2B_NET_FACTOR = 0.70 # Współczynnik netto dla B2B
UOP_PENSION_RATE = 0.1952 # Składka emerytalna ZUS
B2B_MINIMAL_PENSION_CONTRIBUTION = 610.44
ZUS_DIVISOR = 264 # Średni wskaźnik ZUS do obliczania emerytury
CAPITAL_MULTIPLIER = 1.2 # Mnożnik kapitału ZUS

def calculate_pension_details(uop_gross_salary):
    """
    Oblicza prognozowane emerytury, lukę i wymaganą kwotę do zrównania.
    """
    if not uop_gross_salary or uop_gross_salary <= 0:
        return {}

    # 1. Prognozowane emerytury z ZUS
    uop_pension_capital = (uop_gross_salary * UOP_PENSION_RATE * 12 * YEARS_TO_RETIREMENT * CAPITAL_MULTIPLIER)
    uop_pension_monthly = uop_pension_capital / ZUS_DIVISOR
    
    b2b_pension_capital = (B2B_MINIMAL_PENSION_CONTRIBUTION * 12 * YEARS_TO_RETIREMENT * CAPITAL_MULTIPLIER)
    b2b_pension_monthly = b2b_pension_capital / ZUS_DIVISOR
    
    pension_gap_monthly = max(0, uop_pension_monthly - b2b_pension_monthly)

    # 2. Wymagany kapitał prywatny
    required_private_capital = pension_gap_monthly * YEARS_IN_RETIREMENT * 12
    
    # 3. Wymagane miesięczne oszczędności (uproszczony wzór na ratę)
    if pension_gap_monthly > 0:
        q = 1 + (ANNUAL_RETURN_RATE / 12)
        n = YEARS_TO_RETIREMENT * 12
        required_monthly_savings = (required_private_capital * (q - 1)) / (q * (pow(q, n) - 1))
    else:
        required_monthly_savings = 0

    # 4. Optymalna alokacja oszczędności (IKE -> IKZE -> Standard)
    monthly_savings = required_monthly_savings
    ike_monthly = min(monthly_savings, IKE_LIMIT_2025 / 12)
    monthly_savings -= ike_monthly
    ikze_monthly = min(monthly_savings, IKZE_LIMIT_2025 / 12)
    monthly_savings -= ikze_monthly
    standard_monthly = monthly_savings

    # 5. Zwiększenie faktury B2B
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
