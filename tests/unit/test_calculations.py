
import unittest
import json
import os
from unittest.mock import patch, mock_open

# Ensure the path is correct to import from the `src` directory
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from calculations import (
    _get_float,
    calculate_b2b_results,
    calculate_uop_results,
    calculate_break_even,
    calculate_uop_break_even
)

# Mock data for testing
MOCK_DANE = {
    "zus_2025": {
        "preferencyjny": {"emerytalna": 200, "rentowa": 80, "wypadkowa": 10, "fundusz_pracy": 20, "chorobowa": 50, "zdrowotna": 300},
        "pelny": {"emerytalna": 800, "rentowa": 320, "wypadkowa": 40, "fundusz_pracy": 80, "chorobowa": 100, "zdrowotna": 600}
    },
    "progi_podatkowe": {
        "ryczalt_IT": 0.12,
        "liniowy": 0.19,
        "ip_box": 0.05,
        "kwota_wolna": 30000,
        "limit_kup_autorskie": 120000,
        "skala": [
            {"dochod": 120000, "stawka": 0.12},
            {"dochod": 1000000, "stawka": 0.32}
        ],
        "kwota_zmniejszajaca_podatek": 3600
    },
    "dane_ogolne": {
        "dni_robocze_miesiecznie": 21
    },
    "koszty_uzyskania_przychodu": {
        "standardowe": 250,
        "podwyzszone": 300
    },
    "zus_uop_procentowe": {
        "emerytalna": 0.0976,
        "rentowa": 0.015,
        "chorobowa": 0.0245,
        "zdrowotna": 0.09
    },
    "ulga_dla_mlodych_limit": 85528,
    "benefity": {
        "karta_sportowa": 150,
        "opieka_medyczna": 400,
        "ppk": 0.015
    },
    "dni_wolne_uop": {
        "urlop_wypoczynkowy": {"dni": 26}
    }
}

class TestCalculations(unittest.TestCase):

    def setUp(self):
        # Patch the DANE constant in the calculations module
        self.patcher = patch('calculations.DANE', MOCK_DANE)
        self.mock_dane = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_get_float_positive(self):
        self.assertEqual(_get_float({"key": "123.45"}, "key"), 123.45)
        self.assertEqual(_get_float({"key": 123}, "key"), 123.0)
        self.assertEqual(_get_float({"key": "100"}, "key", default=1.0), 100.0)

    def test_get_float_negative(self):
        self.assertEqual(_get_float({"key": "abc"}, "key", default=5.0), 5.0)
        self.assertEqual(_get_float({"key": None}, "key", default=10.0), 10.0)
        self.assertEqual(_get_float({}, "missing_key", default=0.0), 0.0)

    def test_calculate_b2b_results_ryczalt_positive(self):
        b2b_data = {
            "faktura_miesieczna": 10000,
            "koszty_firmowe_miesieczne": 1000,
            "zus_rodzaj": "mala_firma",
            "forma_opodatkowania": "ryczalt_IT",
            "zus_chorobowe": True
        }
        results = calculate_b2b_results(b2b_data)
        self.assertIsInstance(results, dict)
        self.assertGreater(results['roczny_przychod'], 0)
        self.assertEqual(results['roczny_podatek'], 14400) # 120000 * 0.12

    def test_calculate_b2b_results_liniowy_positive(self):
        b2b_data = {
            "faktura_miesieczna": 15000,
            "koszty_firmowe_miesieczne": 2000,
            "zus_rodzaj": "duza_firma",
            "forma_opodatkowania": "liniowy",
            "zus_chorobowe": False
        }
        results = calculate_b2b_results(b2b_data)
        self.assertIsInstance(results, dict)
        self.assertGreater(results['roczny_podatek'], 0)

    def test_calculate_b2b_results_skala_positive(self):
        b2b_data = {
            "faktura_miesieczna": 8000,
            "koszty_firmowe_miesieczne": 500,
            "zus_rodzaj": "preferencyjny",
            "forma_opodatkowania": "skala",
            "zus_chorobowe": True
        }
        results = calculate_b2b_results(b2b_data)
        self.assertIsInstance(results, dict)
        self.assertGreaterEqual(results['roczny_podatek'], 0)

    def test_calculate_b2b_ulga_dla_mlodych_positive(self):
        b2b_data = {
            "faktura_miesieczna": 7000,
            "koszty_firmowe_miesieczne": 1000,
            "zus_rodzaj": "pelny",
            "forma_opodatkowania": "skala",
            "zus_chorobowe": True,
            "ulga_dla_mlodych": True
        }
        results = calculate_b2b_results(b2b_data)
        self.assertEqual(results['roczny_podatek'], 0)

    def test_calculate_uop_results_standard_kup_positive(self):
        uop_data = {
            "wynagrodzenie_brutto": 8000,
            "kup_settings": {"type": "standard"}
        }
        results = calculate_uop_results(uop_data)
        self.assertIsInstance(results, dict)
        self.assertGreater(results['roczne_brutto'], 0)
        self.assertGreater(results['roczny_podatek'], 0)

    def test_calculate_uop_results_autorskie_kup_positive(self):
        uop_data = {
            "wynagrodzenie_brutto": 12000,
            "kup_settings": {"type": "autorskie_50", "creative_work_percentage": 50}
        }
        results = calculate_uop_results(uop_data)
        self.assertIsInstance(results, dict)
        self.assertGreater(results['roczne_brutto'], 0)
        self.assertGreater(results['roczny_podatek'], 0)

    def test_calculate_uop_ulga_dla_mlodych_positive(self):
        uop_data = {
            "wynagrodzenie_brutto": 6000,
            "kup_settings": {"type": "standard"},
            "ulga_dla_mlodych": True
        }
        results = calculate_uop_results(uop_data)
        self.assertEqual(results['roczny_podatek'], 0)

    def test_calculate_break_even_positive(self):
        uop_total_value = 100000
        b2b_base_data = {
            "koszty_firmowe_miesieczne": 1500,
            "zus_rodzaj": "pelny",
            "forma_opodatkowania": "liniowy",
            "zus_chorobowe": True
        }
        break_even_point = calculate_break_even(uop_total_value, b2b_base_data)
        self.assertGreater(break_even_point, 0)
        self.assertNotEqual(break_even_point, -1)

    def test_calculate_break_even_not_found_negative(self):
        uop_total_value = 10000000 # Very high value that won't be reached
        b2b_base_data = {
            "faktura_miesieczna": 1000,
            "koszty_firmowe_miesieczne": 100,
            "zus_rodzaj": "preferencyjny",
            "forma_opodatkowania": "ryczalt_IT",
            "zus_chorobowe": False
        }
        break_even_point = calculate_break_even(uop_total_value, b2b_base_data)
        self.assertEqual(break_even_point, -1)

    def test_calculate_uop_break_even_positive(self):
        b2b_total_value = 120000
        uop_base_data = {
            "kup_settings": {"type": "standard"}
        }
        break_even_point = calculate_uop_break_even(b2b_total_value, uop_base_data)
        self.assertGreater(break_even_point, 0)
        self.assertNotEqual(break_even_point, -1)

    def test_calculate_uop_break_even_not_found_negative(self):
        b2b_total_value = 1500000 # High value
        uop_base_data = {
            "wynagrodzenie_brutto": 5000,
            "kup_settings": {"type": "standard"}
        }
        break_even_point = calculate_uop_break_even(b2b_total_value, uop_base_data)
        self.assertEqual(break_even_point, -1)

if __name__ == '__main__':
    unittest.main()
