
import unittest
from backend.calculations import calculate_uop_results

class TestUopKupLogic(unittest.TestCase):

    def test_kup_standard_positive(self):
        """Test standard KUP (250 PLN/month) calculation for 2026."""
        uop_data = {
            'monthly_gross_salary': 10000,
            'deductible_cost_settings': {'type': 'standard'},
            'age': 30
        }
        results = calculate_uop_results(uop_data)
        # 250 * 12 = 3000
        self.assertAlmostEqual(results['steps']['annual_deductible_costs'], 3000, places=2)
        # 120000 - 16452 (zus) - 9319.32 (zdrow) - 8466 (tax) = 85762.68
        self.assertAlmostEqual(results['annual_net_income'], 85762.68, places=2)

    def test_kup_elevated_positive(self):
        """Test elevated KUP (300 PLN/month) calculation for 2026."""
        uop_data = {
            'monthly_gross_salary': 10000,
            'deductible_cost_settings': {'type': 'elevated'},
            'age': 30
        }
        results = calculate_uop_results(uop_data)
        # 300 * 12 = 3600
        self.assertAlmostEqual(results['steps']['annual_deductible_costs'], 3600, places=2)
        # Podstawa: 120000 - 16452 - 3600 = 99948. Tax: 99948*0.12 - 3600 = 8393.76 -> 8394
        # Netto: 120000 - 16452 - 9319.32 - 8394 = 85834.68
        self.assertAlmostEqual(results['annual_net_income'], 85834.68, places=2)

    def test_kup_creative_below_limit_positive(self):
        """Test 50% creative KUP below the annual limit for 2026."""
        uop_data = {
            'monthly_gross_salary': 20000,
            'deductible_cost_settings': {'type': 'author_50', 'creative_work_percentage': 80},
            'age': 30
        }
        results = calculate_uop_results(uop_data)
        # KUP: 82838.4
        self.assertAlmostEqual(results['steps']['annual_deductible_costs'], 82838.4, places=2)
        # Netto: 240000 - 32904 (zus) - 18638.64 (zdrow) - 12163 (tax) = 176294.36
        self.assertAlmostEqual(results['annual_net_income'], 176294.36, places=2)

    def test_kup_creative_exceeding_limit_positive(self):
        """Test 50% creative KUP when exceeding the annual limit for 2026."""
        uop_data = {
            'monthly_gross_salary': 30000,
            'deductible_cost_settings': {'type': 'author_50', 'creative_work_percentage': 80},
            'age': 30
        }
        results = calculate_uop_results(uop_data)
        # Author costs capped at 120000
        self.assertAlmostEqual(results['steps']['annual_deductible_costs'], 120000, places=2)

    def test_kup_none_positive(self):
        """Test calculation with no KUP for 2026."""
        uop_data = {
            'monthly_gross_salary': 10000,
            'deductible_cost_settings': {'type': 'none'},
            'age': 30
        }
        results = calculate_uop_results(uop_data)
        # Tax: (120000-16452)*0.12 - 3600 = 12425.76 - 3600 = 8825.76 -> 8826
        # Netto: 120000 - 16452 - 9319.32 - 8826 = 85402.68
        self.assertAlmostEqual(results['annual_net_income'], 85402.68, places=2)

if __name__ == '__main__':
    unittest.main()
