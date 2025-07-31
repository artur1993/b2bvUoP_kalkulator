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
            'b2b': {'faktura_miesieczna': 10000, 'zus_rodzaj': 'pelny', 'forma_opodatkowania': 'liniowy'},
            'uop': {'wynagrodzenie_brutto': 8000}
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
                'faktura_miesieczna': 12000,
                'koszty_firmowe_miesieczne': 1000,
                'urlop_dni': 20,
                'przestoje_miesiace': 1,
                'zus_rodzaj': 'pelny',
                'forma_opodatkowania': 'liniowy'
            },
            'uop': {'wynagrodzenie_brutto': 10000}
        }

        response = self.app.post('/api/calculate/sensitivity-analysis', json=request_data)
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3) # We test 3 parameters

        # Check the structure of the first element
        self.assertIn('parameter', data[0])
        self.assertIn('impact', data[0])
        self.assertIn(data[0]['parameter'], ['koszty_firmowe_miesieczne', 'urlop_dni', 'przestoje_miesiace'])

if __name__ == '__main__':
    unittest.main()
