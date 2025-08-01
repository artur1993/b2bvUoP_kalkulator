import unittest
from src.calculations import calculate_b2b_results, calculate_uop_results

class TestCalculations(unittest.TestCase):

    def test_calculate_b2b_results_english_keys(self):
        b2b_data = {
            'monthly_invoice_amount': 10000,
            'monthly_business_costs': 1000,
            'zus_type': 'full',
            'sickness_insurance': True,
            'tax_form': 'flat_tax',
            'youth_relief': False,
            'vacation_days': 20,
            'sick_days': 10,
            'stoppage_months': 1,
            'customBenefits': 100,
            'companyBenefits': {}
        }
        results = calculate_b2b_results(b2b_data)
        self.assertIn('total_annual_value', results)
        self.assertNotIn('calkowita_roczna_wartosc', results)

    def test_calculate_uop_results_english_keys(self):
        uop_data = {
            'monthly_gross_salary': 10000,
            'deductible_cost_settings': {'type': 'standard', 'creative_work_percentage': 0},
            'youth_relief': False,
            'selected_benefits': []
        }
        results = calculate_uop_results(uop_data)
        self.assertIn('total_annual_value', results)
        self.assertNotIn('calkowita_roczna_wartosc', results)

if __name__ == '__main__':
    unittest.main()