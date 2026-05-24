import unittest
from src.calculations import calculate_b2b_results, calculate_uop_results

class TestCalculations(unittest.TestCase):

    def test_calculate_b2b_results_english_keys(self):
        b2b_data = {
            'monthly_invoice_amount': 10000,
            'monthly_business_costs': 1000,
            'zus_type': 'full',
            'sickness_insurance': True,
            'tax_form': 'flat_tax',
            'vacation_days': 20,
            'sick_days': 10,
            'stoppage_months': 1,
            'customBenefits': 100,
            'companyBenefits': {}
        }
        results = calculate_b2b_results(b2b_data)
        self.assertIn('total_annual_value', results)
        self.assertNotIn('calkowita_roczna_wartosc', results)

    def test_calculate_uop_results_english_keys(self):
        uop_data = {
            'monthly_gross_salary': 10000,
            'deductible_cost_settings': {'type': 'standard', 'creative_work_percentage': 0},
            'youth_relief': False,
            'selected_benefits': []
        }
        results = calculate_uop_results(uop_data)
        self.assertIn('total_annual_value', results)
        self.assertNotIn('calkowita_roczna_wartosc', results)

    def _b2b_lump_sum_data(self, monthly_invoice_amount):
        return {
            'monthly_invoice_amount': monthly_invoice_amount,
            'monthly_business_costs': 0,
            'zus_type': 'full',
            'sickness_insurance': False,
            'tax_form': 'lump_sum_it',
            'vacation_days': 0,
            'sick_days': 0,
            'stoppage_months': 0,
            'customBenefits': 0,
            'companyBenefits': {}
        }

    def test_health_contribution_lump_sum_threshold_60k(self):
        results = calculate_b2b_results(self._b2b_lump_sum_data(5000))

        self.assertAlmostEqual(results['steps']['annual_health_contribution'] / 12, 498.35, places=2)

    def test_health_contribution_lump_sum_threshold_60k_plus_1(self):
        results = calculate_b2b_results(self._b2b_lump_sum_data(5001))

        self.assertAlmostEqual(results['steps']['annual_health_contribution'] / 12, 830.58, places=2)

    def test_health_contribution_lump_sum_threshold_300k(self):
        results = calculate_b2b_results(self._b2b_lump_sum_data(25000))

        self.assertAlmostEqual(results['steps']['annual_health_contribution'] / 12, 830.58, places=2)

    def test_health_contribution_lump_sum_threshold_300k_plus_1(self):
        results = calculate_b2b_results(self._b2b_lump_sum_data(25001))

        self.assertAlmostEqual(results['steps']['annual_health_contribution'] / 12, 1495.04, places=2)

    def test_minimum_health_annual_2026(self):
        data = self._b2b_lump_sum_data(0)
        data['tax_form'] = 'flat_tax'

        results = calculate_b2b_results(data)

        self.assertAlmostEqual(results['steps']['annual_health_contribution'], 5072.90, places=2)

    def test_pit_0_not_applied_to_b2b(self):
        data = self._b2b_lump_sum_data(12000)
        data.update({
            'tax_form': 'flat_tax',
            'age': 24,
            'youth_relief': True,
        })

        results = calculate_b2b_results(data)

        self.assertEqual(results['annual_tax'], 22142)

    def test_ip_box_100_percent_qualified(self):
        data = self._b2b_lump_sum_data(10000)
        data.update({
            'tax_form': 'ip_box',
            'ip_box_qualified_share': 100,
            'ip_box_base_form': 'flat_tax',
        })

        results = calculate_b2b_results(data)

        self.assertEqual(results['annual_tax'], 4928)

    def test_ip_box_60_percent_qualified_flat_base(self):
        data = self._b2b_lump_sum_data(10000)
        data.update({
            'tax_form': 'ip_box',
            'ip_box_qualified_share': 60,
            'ip_box_base_form': 'flat_tax',
        })

        results = calculate_b2b_results(data)

        self.assertEqual(results['annual_tax'], 10447)

    def test_ip_box_60_percent_qualified_scale_base(self):
        data = self._b2b_lump_sum_data(10000)
        data.update({
            'tax_form': 'ip_box',
            'ip_box_qualified_share': 60,
            'ip_box_base_form': 'tax_scale',
        })

        results = calculate_b2b_results(data)

        self.assertEqual(results['annual_tax'], 4087)

    def test_uop_total_value_without_double_vacation(self):
        results = calculate_uop_results({
            'monthly_gross_salary': 10000,
            'deductible_cost_settings': {'type': 'standard', 'creative_work_percentage': 0},
            'youth_relief': False,
            'selected_benefits': []
        })
        removed_key = 'annual_paid_days_off_' + 'value'
        former_paid_days_off_amount = 26 * (10000 / 21)

        self.assertAlmostEqual(results['total_annual_value'], results['annual_net_income'], delta=50)
        self.assertNotIn(removed_key, results)
        self.assertAlmostEqual(
            results['annual_net_income'] + former_paid_days_off_amount - results['total_annual_value'],
            former_paid_days_off_amount,
            places=2,
        )

    def test_ppk_employee_contribution_lowers_net(self):
        base_data = {
            'monthly_gross_salary': 10000,
            'deductible_cost_settings': {'type': 'standard', 'creative_work_percentage': 0},
            'youth_relief': False,
            'selected_benefits': []
        }
        without_ppk = calculate_uop_results(base_data)
        with_ppk = calculate_uop_results({**base_data, 'selected_benefits': ['ppk']})
        monthly_cash_difference = (without_ppk['annual_net_income'] - with_ppk['annual_net_income']) / 12

        self.assertGreater(without_ppk['annual_net_income'], with_ppk['annual_net_income'])
        self.assertGreater(monthly_cash_difference, 180)
        self.assertLess(monthly_cash_difference, 260)
        self.assertAlmostEqual(with_ppk['steps']['annual_ppk_employee_contribution'], 2400, places=2)

    def test_ppk_employer_contribution_is_taxed_benefit(self):
        results = calculate_uop_results({
            'monthly_gross_salary': 10000,
            'deductible_cost_settings': {'type': 'standard', 'creative_work_percentage': 0},
            'youth_relief': False,
            'selected_benefits': ['ppk']
        })

        self.assertAlmostEqual(results['steps']['annual_ppk_employer_contribution'], 1800, places=2)
        self.assertAlmostEqual(results['steps']['annual_ppk_employer_net'], 1584, delta=50)
        self.assertAlmostEqual(results['annual_benefits_value'], results['steps']['annual_ppk_employer_net'], places=2)
        self.assertAlmostEqual(
            results['total_annual_value'] - results['annual_net_income'],
            results['steps']['annual_ppk_employer_net'],
            places=2,
        )

    def test_ppk_disabled_no_changes(self):
        results = calculate_uop_results({
            'monthly_gross_salary': 10000,
            'deductible_cost_settings': {'type': 'standard', 'creative_work_percentage': 0},
            'youth_relief': False,
            'selected_benefits': []
        })

        self.assertEqual(results['annual_benefits_value'], 0)
        self.assertEqual(results['steps']['annual_ppk_employee_contribution'], 0)
        self.assertEqual(results['steps']['annual_ppk_employer_contribution'], 0)
        self.assertEqual(results['steps']['annual_ppk_employer_net'], 0)

if __name__ == '__main__':
    unittest.main()
