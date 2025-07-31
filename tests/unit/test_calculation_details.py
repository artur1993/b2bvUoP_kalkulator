import unittest
import json
import os
from src.calculations import calculate_b2b_results, calculate_uop_results, DANE

class TestCalculationDetails(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        global DANE
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        DATA_FILE_PATH = os.path.join(BASE_DIR, 'dane_wejsciowe_kalkulator.json')
        with open(DATA_FILE_PATH, 'r', encoding='utf-8') as f:
            DANE_loaded = json.load(f)
        
        DANE.update(DANE_loaded)
        DANE['zus_uop_procentowe'] = {
            "emerytalna": 0.0976, "rentowa": 0.0150, "chorobowa": 0.0245, "zdrowotna": 0.09
        }
        DANE['ulga_dla_mlodych_limit'] = 85528
        DANE['progi_podatkowe']['kwota_zmniejszajaca_podatek'] = 3600

    def test_b2b_skala_details_positive(self):
        """Test detailed B2B results for 'skala' tax form."""
        b2b_data = {
            'faktura_miesieczna': 15000,
            'koszty_firmowe_miesieczne': 2000,
            'zus_rodzaj': 'duza_firma',
            'zus_chorobowe': True,
            'forma_opodatkowania': 'skala'
        }
        results = calculate_b2b_results(b2b_data)
        steps = results['steps']

        self.assertIn('skladki_zus_emerytalna', steps)
        self.assertIn('podatek_prog_1', steps)
        self.assertIn('podatek_prog_2', steps)

        # Based on external calculations for this specific case
        self.assertAlmostEqual(steps['skladki_zus_emerytalna'], 14428.80, places=2)
        self.assertAlmostEqual(steps['skladka_zdrowotna'], 5026.32, places=2)
        self.assertAlmostEqual(steps['podatek_prog_1'], 10800, places=2)
        self.assertAlmostEqual(steps['podatek_prog_2'], 1883, places=2)
        self.assertAlmostEqual(results['roczne_netto_na_reke'], 117529.44, places=2)

    def test_uop_details_positive(self):
        """Test detailed UoP results."""
        uop_data = {
            'wynagrodzenie_brutto': 12000,
            'kup_settings': {'type': 'standard'}
        }
        results = calculate_uop_results(uop_data)
        steps = results['steps']

        self.assertIn('skladki_zus_emerytalna', steps)
        self.assertIn('podatek_prog_1', steps)
        self.assertIn('podatek_prog_2', steps)

        # Based on external calculations for this specific case
        self.assertAlmostEqual(steps['skladki_zus_emerytalna'], 14054.4, places=2)
        self.assertAlmostEqual(steps['skladka_zdrowotna'], 11183.18, places=2)
        self.assertAlmostEqual(steps['podatek_prog_1'], 10800, places=2)
        self.assertAlmostEqual(steps['podatek_prog_2'], 399.36, places=2)
        self.assertAlmostEqual(results['roczne_netto_na_reke'], 105474.416, places=2)

if __name__ == '__main__':
    unittest.main()
