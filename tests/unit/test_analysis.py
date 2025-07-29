import unittest
import json
import os
from unittest.mock import patch, mock_open
from src.analysis import generate_executive_summary, get_risk_analysis

class TestAnalysis(unittest.TestCase):

    def setUp(self):
        self.mock_data_content = {
            "rekomendacje": {
                "pl": {
                    "b2b_lepsze": "B2B jest lepsze (PL)",
                    "uop_lepsze": "UoP jest lepsze (PL)",
                    "zblizone": "Finansowo zbliżone (PL)"
                },
                "en": {
                    "b2b_lepsze": "B2B is better (EN)",
                    "uop_lepsze": "UoP is better (EN)",
                    "zblizone": "Financially similar (EN)"
                }
            },
            "analiza_ryzyka": {
                "pl": {
                    "zdolnosc_kredytowa_uop": "Banki preferują UoP (PL)"
                },
                "en": {
                    "zdolnosc_kredytowa_uop": "Banks prefer UoP (EN)"
                }
            }
        }

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_generate_executive_summary_b2b_better(self, mock_json_load, mock_file_open):
        mock_json_load.return_value = self.mock_data_content
        b2b_results = {"net_annual_income": 100000}
        uop_results = {"net_annual_income": 90000}
        summary = generate_executive_summary(b2b_results, uop_results, 0, 'en')
        self.assertEqual(summary["recommendation"], "B2B is better (EN)")

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_generate_executive_summary_uop_better(self, mock_json_load, mock_file_open):
        mock_json_load.return_value = self.mock_data_content
        b2b_results = {"net_annual_income": 90000}
        uop_results = {"net_annual_income": 100000}
        summary = generate_executive_summary(b2b_results, uop_results, 0, 'en')
        self.assertEqual(summary["recommendation"], "UoP is better (EN)")

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_generate_executive_summary_similar(self, mock_json_load, mock_file_open):
        mock_json_load.return_value = self.mock_data_content
        b2b_results = {"net_annual_income": 95000}
        uop_results = {"net_annual_income": 96000}
        summary = generate_executive_summary(b2b_results, uop_results, 0, 'en')
        self.assertEqual(summary["recommendation"], "Financially similar (EN)")

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_get_risk_analysis_en(self, mock_json_load, mock_file_open):
        mock_json_load.return_value = self.mock_data_content
        risk_analysis = get_risk_analysis('en')
        self.assertEqual(risk_analysis["zdolnosc_kredytowa_uop"], "Banks prefer UoP (EN)")

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_get_risk_analysis_pl(self, mock_json_load, mock_file_open):
        mock_json_load.return_value = self.mock_data_content
        risk_analysis = get_risk_analysis('pl')
        self.assertEqual(risk_analysis["zdolnosc_kredytowa_uop"], "Banki preferują UoP (PL)")

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_generate_executive_summary_missing_keys(self, mock_json_load, mock_file_open):
        mock_json_load.return_value = self.mock_data_content
        b2b_results = {}
        uop_results = {}
        summary = generate_executive_summary(b2b_results, uop_results, 0, 'en')
        self.assertEqual(summary["recommendation"], "Financially similar (EN)")
        self.assertEqual(summary["b2b_net_annual"], 0)
        self.assertEqual(summary["uop_net_annual"], 0)

if __name__ == '__main__':
    unittest.main()