import unittest
from src.calculations import calculate_b2b_results, calculate_uop_results

class TestCalculationDetails(unittest.TestCase):

    def test_b2b_skala_details_positive(self):
        """Test detailed B2B results for 'skala' tax form (2026)."""
        b2b_data = {
            'monthly_invoice_amount': 15000,
            'monthly_business_costs': 2000,
            'zus_type': 'full',
            'sickness_insurance': True,
            'tax_form': 'tax_scale',
            'age': 30
        }
        results = calculate_b2b_results(b2b_data)
        steps = results['steps']

        # Verify existence of core calculation steps
        self.assertIn('annual_social_contributions', steps)
        self.assertIn('annual_health_contribution', steps)
        self.assertIn('annual_tax', steps)

        # Basic range checks for 2026
        self.assertGreater(steps['annual_social_contributions'], 20000)
        self.assertGreater(results['annual_net_income'], 100000)

    def test_uop_details_positive(self):
        """Test detailed UoP results (2026)."""
        uop_data = {
            'monthly_gross_salary': 12000,
            'deductible_cost_settings': {'type': 'standard'},
            'age': 30
        }
        results = calculate_uop_results(uop_data)
        steps = results['steps']

        self.assertIn('annual_deductible_costs', steps)
        self.assertIn('monthly_calculations', steps)

        # Check total value for 12k gross
        self.assertGreater(results['annual_net_income'], 100000)

if __name__ == '__main__':
    unittest.main()
