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

    def _b2b_lump_sum_data(self, monthly_invoice_amount):
        return {
            'monthly_invoice_amount': monthly_invoice_amount,
            'monthly_business_costs': 0,
            'zus_type': 'full',
            'sickness_insurance': False,
            'tax_form': 'lump_sum_it',
            'youth_relief': False,
            'vacation_days': 0,
            'sick_days': 0,
            'stoppage_months': 0,
            'customBenefits': 0,
            'companyBenefits': {}
        }

    def test_health_contribution_lump_sum_threshold_60k(self):
        results = calculate_b2b_results(self._b2b_lump_sum_data(5000))

        self.assertAlmostEqual(results['steps']['annual_health_contribution'] / 12, 498.35, places=2)

    def test_health_contribution_lump_sum_threshold_60k_plus_1(self):
        results = calculate_b2b_results(self._b2b_lump_sum_data(5001))

        self.assertAlmostEqual(results['steps']['annual_health_contribution'] / 12, 830.58, places=2)

    def test_health_contribution_lump_sum_threshold_300k(self):
        results = calculate_b2b_results(self._b2b_lump_sum_data(25000))

        self.assertAlmostEqual(results['steps']['annual_health_contribution'] / 12, 830.58, places=2)

    def test_health_contribution_lump_sum_threshold_300k_plus_1(self):
        results = calculate_b2b_results(self._b2b_lump_sum_data(25001))

        self.assertAlmostEqual(results['steps']['annual_health_contribution'] / 12, 1495.04, places=2)

if __name__ == '__main__':
    unittest.main()
