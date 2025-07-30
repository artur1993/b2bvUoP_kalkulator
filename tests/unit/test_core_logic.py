
import unittest
import json
import os
from src.app import DANE, calculate_uop_results
from src.calculations import _get_float

class TestGetFloat(unittest.TestCase):

    def test_get_float_valid_float(self):
        data = {"key": 123.45}
        self.assertEqual(_get_float(data, "key"), 123.45)

    def test_get_float_valid_int(self):
        data = {"key": 123}
        self.assertEqual(_get_float(data, "key"), 123.0)

    def test_get_float_valid_string_float(self):
        data = {"key": "123.45"}
        self.assertEqual(_get_float(data, "key"), 123.45)

    def test_get_float_valid_string_int(self):
        data = {"key": "123"}
        self.assertEqual(_get_float(data, "key"), 123.0)

    def test_get_float_missing_key(self):
        data = {}
        self.assertEqual(_get_float(data, "key"), 0.0)

    def test_get_float_missing_key_with_default(self):
        data = {}
        self.assertEqual(_get_float(data, "key", default=99.9), 99.9)

    def test_get_float_invalid_string(self):
        data = {"key": "abc"}
        self.assertEqual(_get_float(data, "key"), 0.0)

    def test_get_float_none_value(self):
        data = {"key": None}
        self.assertEqual(_get_float(data, "key"), 0.0)

class TestUopKupLogic(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the main data file to ensure consistency with the app
        global DANE
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        DATA_FILE_PATH = os.path.join(BASE_DIR, 'dane_wejsciowe_kalkulator.json')
        with open(DATA_FILE_PATH, 'r', encoding='utf-8') as f:
            DANE_loaded = json.load(f)
        
        # Manually add data that is normally added at app startup
        DANE.update(DANE_loaded)
        DANE['zus_uop_procentowe'] = {
            "emerytalna": 0.0976, "rentowa": 0.0150, "chorobowa": 0.0245, "zdrowotna": 0.09
        }
        DANE['ulga_dla_mlodych_limit'] = 85528
        DANE['progi_podatkowe']['kwota_zmniejszajaca_podatek'] = 3600


    def test_kup_standard_positive(self):
        """Test standard KUP (250 PLN/month) calculation."""
        uop_data = {
            'wynagrodzenie_brutto': 10000,
            'kup_settings': {'type': 'standard'}
        }
        results = calculate_uop_results(uop_data)
        # 250 * 12 = 3000
        self.assertAlmostEqual(results['steps']['Koszty uzyskania przychodu'], 3000, places=2)
        # Based on external calculation for this specific case
        self.assertAlmostEqual(results['roczne_netto_na_reke'], 89362.68, places=2)
        self.assertAlmostEqual(results['roczny_podatek'], 4866.00, places=2)

    def test_kup_elevated_positive(self):
        """Test elevated KUP (300 PLN/month) calculation."""
        uop_data = {
            'wynagrodzenie_brutto': 10000,
            'kup_settings': {'type': 'elevated'}
        }
        results = calculate_uop_results(uop_data)
        # 300 * 12 = 3600
        self.assertAlmostEqual(results['steps']['Koszty uzyskania przychodu'], 3600, places=2)
        # Based on external calculation for this specific case
        self.assertAlmostEqual(results['roczne_netto_na_reke'], 89434.68, places=2)
        self.assertAlmostEqual(results['roczny_podatek'], 4794.00, places=2)

    def test_kup_creative_below_limit_positive(self):
        """Test 50% creative KUP below the annual limit."""
        uop_data = {
            'wynagrodzenie_brutto': 20000,
            'kup_settings': {'type': 'autorskie_50', 'creative_work_percentage': 80}
        }
        results = calculate_uop_results(uop_data)

        # Expected KUP calculation for one month:
        # Gross creative part: 20000 * 0.8 = 16000
        # ZUS from creative part: 16000 * (0.0976 + 0.0150 + 0.0245) = 16000 * 0.1371 = 2193.6
        # Base for KUP: 16000 - 2193.6 = 13806.4
        # Monthly KUP: 13806.4 * 0.5 = 6903.2
        # Annual KUP: 6903.2 * 12 = 82838.4 (below 120000 limit)
        self.assertAlmostEqual(results['steps']['Koszty uzyskania przychodu'], 82838.4, places=2)
        self.assertAlmostEqual(results['roczne_netto_na_reke'], 179897.36, places=2)
        self.assertAlmostEqual(results['roczny_podatek'], 8560.00, places=2)

    def test_kup_creative_exceeding_limit_positive(self):
        """Test 50% creative KUP when exceeding the annual limit."""
        uop_data = {
            'wynagrodzenie_brutto': 30000,
            'kup_settings': {'type': 'autorskie_50', 'creative_work_percentage': 80}
        }
        results = calculate_uop_results(uop_data)

        # Expected KUP calculation:
        # Monthly potential creative KUP: 10354.8
        # Cumulative KUP after 11 months: 10354.8 * 11 = 113902.8
        # Remaining creative KUP limit for 12th month: 120000 - 113902.8 = 6097.2
        # KUP for 12th month = remaining creative KUP + standard KUP (250) = 6097.2 + 250 = 6347.2
        # Total annual KUP = (10354.8 * 11) + 6347.2 = 113902.8 + 6347.2 = 120250

        self.assertAlmostEqual(results['steps']['Koszty uzyskania przychodu'], 120250, places=2)
        self.assertAlmostEqual(results['roczne_netto_na_reke'], 252960.04, places=2)
        self.assertAlmostEqual(results['roczny_podatek'], 29726.00, places=2)

        # Verify monthly KUP values
        monthly_calculations = results['steps']['monthly_calculations']
        self.assertAlmostEqual(monthly_calculations[0]['kup'], 10354.8, places=2)
        self.assertAlmostEqual(monthly_calculations[10]['kup'], 10354.8, places=2)
        self.assertAlmostEqual(monthly_calculations[11]['kup'], 6347.2, places=2)

    def test_kup_none_positive(self):
        """Test calculation with no KUP."""
        uop_data = {
            'wynagrodzenie_brutto': 10000,
            'kup_settings': {'type': 'brak'}
        }
        results = calculate_uop_results(uop_data)
        self.assertAlmostEqual(results['steps']['Koszty uzyskania przychodu'], 0, places=2)
        self.assertAlmostEqual(results['roczne_netto_na_reke'], 89002.68, places=2)
        self.assertAlmostEqual(results['roczny_podatek'], 5226.00, places=2)

if __name__ == '__main__':
    unittest.main()
