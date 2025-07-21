import unittest
import json
import sys
import os

# Add the 'src' directory to the Python path to allow importing 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from app import app, DANE

class CalculatorTestCase(unittest.TestCase):
    """Unit tests for the calculation logic."""

    def setUp(self):
        """Set up a test client and load test data."""
        self.app = app.test_client()
        self.app.testing = True
        
        # This is the sample request provided in the prompt
        self.sample_request = {
          "b2b": {
            "faktura_miesieczna": 21000,
            "forma_opodatkowania": "ryczalt_IT",
            "zus_rodzaj": "pelny",
            "zus_chorobowe": True,
            "vat": True,
            "koszty_firmowe_miesieczne": 600,
            "wybrane_benefity": ["opieka_medyczna", "karta_sportowa", "sprzet"],
            "przestoje_miesiace": 1.5,
            "urlop_dni": 24,
            "wiek": 32,
            "dzieci": 0,
            "ulga_dla_mlodych": False
          },
          "uop": {
            "wynagrodzenie_brutto": 16500,
            "koszty_uzyskania_przychodu": 250,
            "wybrane_benefity": ["opieka_medyczna", "ppk", "budzet_szkoleniowy"],
            "wiek": 32,
            "dzieci": 0,
            "ulga_dla_mlodych": False
          },
          "ogolne": {
            "scenariusz": "realistyczny",
            "analiza_zdolnosci_kredytowej": True
          }
        }

    def test_b2b_ryczalt_calculation(self):
        """Test B2B calculation for the ryczalt_IT tax form."""
        response = self.app.post('/calculate', 
                                 data=json.dumps(self.sample_request),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        b2b_res = data['b2b_results']
        # Ryczałt is calculated from revenue, so social contributions are not deducted from the base.
        # Netto = 244800 - 30115.56 - 30240 - 8200 - 55500 = 120744.44
        self.assertAlmostEqual(b2b_res['roczne_netto'], 120744.44, places=2)
        self.assertAlmostEqual(b2b_res['roczny_podatek'], 30240, places=2)

    def test_uop_calculation(self):
        """Test UoP calculation."""
        response = self.app.post('/calculate',
                                 data=json.dumps(self.sample_request),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        uop_res = data['uop_results']
        self.assertAlmostEqual(uop_res['roczne_netto'], 129364.04, places=2)
        self.assertAlmostEqual(uop_res['calkowita_roczna_wartosc'], 159152.61, places=2)

    def test_b2b_liniowy_calculation(self):
        """Test B2B calculation for the 'liniowy' tax form with correct 2025 rules."""
        request_data = self.sample_request.copy()
        request_data['b2b']['forma_opodatkowania'] = 'liniowy'
        response = self.app.post('/calculate',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        b2b_res = data['b2b_results']
        # Manual calculation based on new rules:
        # Dochód brutto: 252000 - 7200 = 244800
        # Składki społeczne: 25089.24
        # Składka zdrowotna: 5026.32, odliczenie: 5026.32 (poniżej limitu 12900)
        # Podstawa opodatkowania: 244800 - 25089.24 - 5026.32 = 214684.44 -> zaokr. 214684
        # Podatek: 214684 * 0.19 = 40790 -> zaokr. 40790
        # Netto: 244800 - 30115.56 - 40790 - 8200 - 55500 = 110194.44
        self.assertAlmostEqual(b2b_res['roczny_podatek'], 40790, places=0)
        self.assertAlmostEqual(b2b_res['roczne_netto'], 110194.44, places=2)

    def test_b2b_skala_calculation(self):
        """Test B2B calculation for the 'skala' tax form with correct 2025 rules."""
        request_data = self.sample_request.copy()
        request_data['b2b']['forma_opodatkowania'] = 'skala'
        response = self.app.post('/calculate',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        b2b_res = data['b2b_results']
        # Manual calculation based on new rules:
        # Dochód brutto: 244800
        # Składki społeczne: 25089.24
        # Brak odliczenia zdrowotnej
        # Podstawa opodatkowania: 244800 - 25089.24 = 219710.76 -> zaokr. 219711
        # Podatek: (120000-30000)*0.12 + (219711-120000)*0.32 = 10800 + 31907.52 = 42707.52 -> zaokr. 42708
        # Netto: 244800 - 30115.56 - 42708 - 8200 - 55500 = 108276.44
        self.assertAlmostEqual(b2b_res['roczny_podatek'], 42708, places=0)
        self.assertAlmostEqual(b2b_res['roczne_netto'], 108276.44, places=2)

    def test_ulga_dla_mlodych_uop(self):
        """Test UoP calculation with the youth relief."""
        request_data = self.sample_request.copy()
        request_data['uop']['ulga_dla_mlodych'] = True
        request_data['uop']['wynagrodzenie_brutto'] = 7000 # Below the limit
        response = self.app.post('/calculate',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        uop_res = data['uop_results']
        self.assertAlmostEqual(uop_res['roczny_podatek'], 0, places=2)
        self.assertAlmostEqual(uop_res['roczne_netto'], 65960.08, places=2)

if __name__ == '__main__':
    unittest.main()
