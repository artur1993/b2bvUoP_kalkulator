import unittest
from unittest.mock import patch
from src.app import app

class TestAnalysisEndpoints(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('src.app.calculate_b2b_results')
    @patch('src.app.calculate_uop_results')
    def test_break_even_analysis_endpoint_positive(self, mock_uop, mock_b2b):
        """Test the /api/calculate/break-even-analysis endpoint for correct structure."""
        # Mock the return values of the core calculation functions
        mock_b2b.return_value = {'calkowita_roczna_wartosc': 120000}
        mock_uop.return_value = {'calkowita_roczna_wartosc': 100000}

        request_data = {
            'b2b': {
                'monthly_invoice_amount': 10000,
                'monthly_business_costs': 1500,
                'zus_type': 'full',
                'tax_form': 'flat_tax',
                'sickness_insurance': True,
                'age': 30,
                'youth_relief': False,
                'vacation_days': 26,
                'stoppage_months': 1,
                'customBenefits': 500,
                'companyBenefits': {},
                'equalizePension': False
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

    @patch('src.app.calculate_b2b_results')
    @patch('src.app.calculate_uop_results')
    def test_sensitivity_analysis_endpoint_positive(self, mock_uop, mock_b2b):
        """Test the /api/calculate/sensitivity-analysis endpoint for correct structure."""
        mock_b2b.return_value = {'calkowita_roczna_wartosc': 120000}
        mock_uop.return_value = {'calkowita_roczna_wartosc': 100000}

        request_data = {
            'b2b': {
                'monthly_invoice_amount': 12000,
                'monthly_business_costs': 1000,
                'vacation_days': 20,
                'stoppage_months': 1,
                'zus_type': 'full',
                'tax_form': 'flat_tax',
                'sickness_insurance': True,
                'age': 30,
                'youth_relief': False,
                'customBenefits': 0,
                'companyBenefits': {},
                'equalizePension': False
            },
            'uop': {
                'monthly_gross_salary': 10000,
                'age': 30,
                'youth_relief': False,
                'deductible_cost_settings': {'type': 'standard'}
            }
        }

        response = self.app.post('/api/calculate/sensitivity-analysis', json=request_data)
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3) # We test 3 parameters

        # Check the structure of the first element
        self.assertIn('parameter', data[0])
        self.assertIn('impact', data[0])
        self.assertIn(data[0]['parameter'], ['monthly_business_costs', 'vacation_days', 'stoppage_months'])

if __name__ == '__main__':
    unittest.main()
