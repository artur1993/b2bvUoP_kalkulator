import unittest
from src.app import app

class TestAnalysisEndpoints(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_break_even_analysis_endpoint_positive(self):
        """Test the /api/calculate/break-even-analysis endpoint for correct structure."""
        request_data = {
            'b2b': {
                'monthly_invoice_amount': 10000,
                'monthly_business_costs': 1500,
                'zus_type': 'full',
                'tax_form': 'flat_tax',
                'sickness_insurance': True,
                'age': 30,
                'vacation_days': 26,
                'stoppage_months': 1,
                'customBenefits': 500,
                'companyBenefits': {}
            },
            'uop': {
                'monthly_gross_salary': 8000,
                'age': 30,
                'youth_relief': False,
                'deductible_cost_settings': {'type': 'standard'}
            }
        }

        response = self.app.post('/api/calculate/break-even-analysis', json=request_data)
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        
        # Check the structure of the first element
        self.assertIn('b2b_rate', data[0])
        self.assertIn('net_difference', data[0])

if __name__ == '__main__':
    unittest.main()
