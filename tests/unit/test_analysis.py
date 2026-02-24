import unittest
from unittest.mock import patch
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

    @patch('src.config.config_manager.get_config')
    def test_generate_executive_summary_b2b_better_positive(self, mock_get_config):
        mock_get_config.return_value = self.mock_data_content
        b2b_results = {"total_annual_value": 100000}
        uop_results = {"total_annual_value": 90000}
        summary = generate_executive_summary(b2b_results, uop_results, 0, 'en')
        self.assertEqual(summary["recommendation"], "B2B is better (EN)")

    @patch('src.config.config_manager.get_config')
    def test_generate_executive_summary_uop_better_positive(self, mock_get_config):
        mock_get_config.return_value = self.mock_data_content
        b2b_results = {"total_annual_value": 90000}
        uop_results = {"total_annual_value": 100000}
        summary = generate_executive_summary(b2b_results, uop_results, 0, 'en')
        self.assertEqual(summary["recommendation"], "UoP is better (EN)")

    @patch('src.config.config_manager.get_config')
    def test_get_risk_analysis_en_positive(self, mock_get_config):
        mock_get_config.return_value = self.mock_data_content
        risk_analysis = get_risk_analysis('en')
        self.assertEqual(risk_analysis["zdolnosc_kredytowa_uop"], "Banks prefer UoP (EN)")

    @patch('src.config.config_manager.get_config')
    def test_generate_executive_summary_missing_keys_negative(self, mock_get_config):
        mock_get_config.return_value = self.mock_data_content
        b2b_results = {}
        uop_results = {}
        summary = generate_executive_summary(b2b_results, uop_results, 0, 'en')
        self.assertEqual(summary["recommendation"], "Financially similar (EN)")
        self.assertEqual(summary["b2b_net_annual"], 0)
        self.assertEqual(summary["uop_net_annual"], 0)

if __name__ == '__main__':
    unittest.main()
