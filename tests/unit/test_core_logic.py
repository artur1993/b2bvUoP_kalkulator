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
        
        # Updated sample request with new benefit structure
        self.sample_request = {
          "b2b": {
            "faktura_miesieczna": 21000,
            "forma_opodatkowania": "ryczalt_IT",
            "zus_rodzaj": "pelny",
            "zus_chorobowe": True,
            "vat": True,
            "koszty_firmowe_miesieczne": 600,
            "urlop_dni": 24,
            "przestoje_miesiace": 1.5,
            "wiek": 32,
            "ulga_dla_mlodych": False,
            "customBenefits": 0, # New field
            "companyBenefits": { # New structure
                "paidVacationDays": {"enabled": False, "value": 0, "days": 20},
                "privateHealthcare": {"enabled": False, "value": 2400},
                "sportCard": {"enabled": False, "value": 1200}
            }
          },
          "uop": {
            "wynagrodzenie_brutto": 16500,
            "koszty_uzyskania_przychodu": 250,
            "wybrane_benefity": ["opieka_medyczna", "ppk", "budzet_szkoleniowy"],
            "wiek": 32,
            "ulga_dla_mlodych": False
          }
        }

    def test_b2b_ryczalt_calculation(self):
        """Test B2B calculation for the ryczalt_IT tax form (no new benefits)."""
        response = self.app.post('/calculate', 
                                 data=json.dumps(self.sample_request),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        b2b_res = json.loads(response.data)['b2b_results']
        
        # Corrected assertions based on the new logic
        self.assertAlmostEqual(b2b_res['roczny_podatek'], 30240, places=2)
        self.assertAlmostEqual(b2b_res['roczne_netto_na_reke'], 128944.44, places=2)
        self.assertAlmostEqual(b2b_res['calkowita_roczna_wartosc'], 128944.44, places=2)

    def test_uop_calculation(self):
        """Test UoP calculation."""
        response = self.app.post('/calculate',
                                 data=json.dumps(self.sample_request),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        uop_res = json.loads(response.data)['uop_results']
        self.assertAlmostEqual(uop_res['roczne_netto_na_reke'], 129364.04, places=2)
        self.assertAlmostEqual(uop_res['calkowita_roczna_wartosc'], 159152.61, places=2)

    def test_b2b_with_custom_and_company_benefits(self):
        """Test B2B calculation with custom and company-provided benefits."""
        request_data = self.sample_request.copy()
        request_data['b2b']['customBenefits'] = 5000
        request_data['b2b']['companyBenefits']['privateHealthcare']['enabled'] = True
        request_data['b2b']['companyBenefits']['paidVacationDays']['enabled'] = True

        response = self.app.post('/calculate',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        b2b_res = json.loads(response.data)['b2b_results']

        # Wartość benefitów od firmy: 2400 (opieka) + (20 dni * 1000/dzień) = 22400
        self.assertAlmostEqual(b2b_res['roczna_wartosc_benefitow_od_firmy'], 22400, places=2)
        self.assertAlmostEqual(b2b_res['roczna_wartosc_wlasnych_korzysci'], 5000, places=2)

        # Utracony przychód:
        # Płatny urlop od firmy: 20 dni. Całkowity urlop: 24 dni.
        # Niezapłacony urlop: 24 - 20 = 4 dni.
        # Utrata z urlopu: 4 * (21000/21) = 4000
        # Utrata z przestoju: 1.5 * 21000 = 31500
        # Całkowita utrata: 4000 + 31500 = 35500
        self.assertAlmostEqual(b2b_res['roczny_utracony_przychod'], 35500, places=2)

        # Netto na rękę (takie samo jak w pierwszym teście, ale z mniejszą utratą przychodu):
        # 129744.44 (stare netto) + (55500 - 35500) (różnica w utracie) = 149744.44
        self.assertAlmostEqual(b2b_res['roczne_netto_na_reke'], 148944.44, places=2)

        # Całkowita wartość = Netto na rękę + benefity od firmy + własne korzyści
        # 149744.44 + 22400 + 5000 = 157144.44
        self.assertAlmostEqual(b2b_res['calkowita_roczna_wartosc'], 176344.44, places=2)

    def test_b2b_liniowy_calculation(self):
        """Test B2B calculation for the 'liniowy' tax form with correct 2025 rules."""
        request_data = self.sample_request.copy()
        request_data['b2b']['forma_opodatkowania'] = 'liniowy'
        response = self.app.post('/calculate',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        b2b_res = json.loads(response.data)['b2b_results']
        self.assertAlmostEqual(b2b_res['roczny_podatek'], 40790, places=0)
        self.assertAlmostEqual(b2b_res['roczne_netto_na_reke'], 118394.44, places=2)

    def test_b2b_skala_calculation(self):
        """Test B2B calculation for the 'skala' tax form with correct 2025 rules."""
        request_data = self.sample_request.copy()
        request_data['b2b']['forma_opodatkowania'] = 'skala'
        response = self.app.post('/calculate',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        b2b_res = json.loads(response.data)['b2b_results']
        self.assertAlmostEqual(b2b_res['roczny_podatek'], 42708, places=0)
        self.assertAlmostEqual(b2b_res['roczne_netto_na_reke'], 116476.44, places=2)

    def test_ulga_dla_mlodych_uop(self):
        """Test UoP calculation with the youth relief."""
        request_data = self.sample_request.copy()
        request_data['uop']['ulga_dla_mlodych'] = True
        request_data['uop']['wynagrodzenie_brutto'] = 7000 # Below the limit
        response = self.app.post('/calculate',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        uop_res = json.loads(response.data)['uop_results']
        self.assertAlmostEqual(uop_res['roczny_podatek'], 0, places=2)
        self.assertAlmostEqual(uop_res['roczne_netto_na_reke'], 65960.08, places=2)

if __name__ == '__main__':
    unittest.main()
