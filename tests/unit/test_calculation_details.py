import unittest
from src.calculations import calculate_b2b_results, calculate_uop_results

class TestCalculationDetails(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def test_b2b_skala_details_positive(self):
        """Test detailed B2B results for 'skala' tax form."""
        b2b_data = {
            'monthly_invoice_amount': 15000,
            'monthly_business_costs': 2000,
            'zus_type': 'full',
            'sickness_insurance': True,
            'tax_form': 'tax_scale'
        }
        results = calculate_b2b_results(b2b_data)
        steps = results['steps']

        self.assertIn('pension_insurance_contribution', steps)
        self.assertIn('tax_first_threshold', steps)
        self.assertIn('tax_second_threshold', steps)

        # Based on external calculations for this specific case
        self.assertAlmostEqual(steps['pension_insurance_contribution'], 14428.80, places=2)
        self.assertAlmostEqual(steps['annual_health_contribution'], 5026.32, places=2)
        self.assertAlmostEqual(steps['tax_first_threshold'], 10800, places=2)
        self.assertAlmostEqual(steps['tax_second_threshold'], 2444, places=2)
        self.assertAlmostEqual(results['annual_net_income'], 118720.80, places=2)

    def test_uop_details_positive(self):
        """Test detailed UoP results."""
        uop_data = {
            'monthly_gross_salary': 12000,
            'deductible_cost_settings': {'type': 'standard'}
        }
        results = calculate_uop_results(uop_data)
        steps = results['steps']

        self.assertIn('annual_pension_contribution', steps)
        self.assertIn('tax_first_threshold', steps)
        self.assertIn('tax_second_threshold', steps)

        # Based on external calculations for this specific case
        self.assertAlmostEqual(steps['annual_pension_contribution'], 14054.4, places=2)
        self.assertAlmostEqual(steps['annual_health_contribution'], 11183.18, places=2)
        self.assertAlmostEqual(steps['tax_first_threshold'], 10800, places=2)
        self.assertAlmostEqual(steps['tax_second_threshold'], 399.36, places=2)
        self.assertAlmostEqual(results['annual_net_income'], 105474.416, places=2)

if __name__ == '__main__':
    unittest.main()
