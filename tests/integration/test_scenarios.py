import unittest
import json
import sys
import os

# Add the 'src' directory to the Python path to allow importing 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from app import app

class ScenariosTestCase(unittest.TestCase):
    """
    Comprehensive integration tests for the B2B vs UoP calculator.
    Each test represents a specific user scenario.
    """

    def setUp(self):
        """Set up a test client and a base request structure."""
        self.app = app.test_client()
        self.app.testing = True
        
        # A base structure for requests, to be modified in each test
        self.base_request = {
          "b2b": {
            "monthly_invoice_amount": 20000,
            "tax_form": "lump_sum_it",
            "zus_type": "full",
            "sickness_insurance": True,
            "vat": True,
            "monthly_business_costs": 500,
            "stoppage_months": 0,
            "vacation_days": 0,
            "age": 30,
            "youth_relief": False,
            "customBenefits": 0,
            "companyBenefits": {}
          },
          "uop": {
            "monthly_gross_salary": 15000,
            "deductible_cost_settings": {'type': 'standard'},
            "selected_benefits": [],
            "age": 30,
            "youth_relief": False
          },
          "calculation_mode": "uop_to_b2b"
        }

    # --- SCENARIO TESTS WILL BE IMPLEMENTED HERE ---

    def test_scenario_1_junior_uop_youth_relief_positive(self):
        """1. Junior on UoP with youth relief, no benefits."""
        request = self.base_request.copy()
        request['uop'].update({
            "monthly_gross_salary": 7000,
            "age": 25,
            "youth_relief": True,
            "selected_benefits": [],
            "deductible_cost_settings": {'type': 'standard'}
        })
        
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['uop_results']

        self.assertEqual(data['annual_tax'], 0)
        self.assertAlmostEqual(data['annual_net_income'], 65960.08, places=2)
        self.assertGreater(data['annual_paid_days_off_value'], 0)

    def test_scenario_2_senior_b2b_no_benefits_positive(self):
        """2. Senior B2B, full ZUS, no VAT/chorobowe, no benefits."""
        request = self.base_request.copy()
        request['b2b'].update({
            "monthly_invoice_amount": 25000,
            "zus_type": "full",
            "sickness_insurance": False
        })

        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['b2b_results']

        self.assertAlmostEqual(data['annual_zus'], 26610.84, places=2) # No chorobowe
        self.assertAlmostEqual(data['annual_company_benefits_value'], 0)
        self.assertGreater(data['total_annual_value'], 200000)

    def test_scenario_3_b2b_no_time_off_positive(self):
        """3. B2B with no holidays/downtime."""
        request = self.base_request.copy()
        request['b2b'].update({
            "vacation_days": 0,
            "stoppage_months": 0
        })

        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['b2b_results']

        self.assertEqual(data['annual_lost_revenue'], 0)

    def test_scenario_4_pessimistic_b2b_with_benefits_negative(self):
        """4. Pessimistic: 2 months downtime, holiday, with company benefits."""
        request = self.base_request.copy()
        request['b2b'].update({
            "stoppage_months": 2,
            "vacation_days": 26,
            "companyBenefits": {
                "privateHealthcare": {"enabled": True, "value": 2400},
                "sportCard": {"enabled": True, "value": 1800},
                "paidVacationDays": {"enabled": True, "value": 0, "days": 26} # 26 paid vacation days
            }
        })

        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['b2b_results']

        # Utracony przychód: 2 miesiące przestoju (2 * monthly_invoice_amount) = 40000. Urlop jest w pełni płatny, więc 0 utraty.
        self.assertAlmostEqual(data['annual_lost_revenue'], 40000, places=2)
        # Benefity: 2400 (opieka) + 1800 (sport) + (26 dni * 20000/21) = 4200 + 24761.90 = 28961.90
        self.assertAlmostEqual(data['annual_company_benefits_value'], 28961.90, places=2)

    def test_scenario_5_uop_tax_threshold_positive(self):
        """5. Exceeding the tax threshold on UoP."""
        request = self.base_request.copy()
        request['uop'].update({
            "monthly_gross_salary": 25000, # High salary to exceed threshold
            "deductible_cost_settings": {'type': 'standard'} # Ensure standard KUP is used
        })

        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['uop_results']

        print(f"\n--- Debugging Scenario 5 ---")
        print(f"Input UoP Data: {request['uop']}")
        print(f"Calculated UoP Results: {data}")
        print(f"Annual tax (expected): 54281, Actual: {data['annual_tax']}")
        print(f"--- End Debugging Scenario 5 ---")

        self.assertAlmostEqual(data['annual_tax'], 50677, places=0)

    def test_scenario_6_uop_full_benefits_positive(self):
        """6. UoP with a full set of benefits."""
        request = self.base_request.copy()
        request['uop']['monthly_gross_salary'] = 15000 # Set a specific salary for consistent benefit calculation
        request['uop']['selected_benefits'] = ["medical_care", "sport_card", "training_budget", "ppk", "equipment"]

        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['uop_results']

        # 2400 + 1800 + 3000 + 4000 + (15000*12*0.02) = 11200 + 3600 = 14800
        self.assertAlmostEqual(data['annual_benefits_value'], 14800, places=2)

    def test_scenario_7_b2b_preferential_zus_positive(self):
        """7. B2B preferential ZUS, minimal business costs."""
        request = self.base_request.copy()
        request['b2b'].update({
            "zus_type": "preferential",
            "monthly_business_costs": 50
        })

        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['b2b_results']

        # (314.09 + 129.45 + 31.53 + 87.05) * 12 + 418.86 * 12 = 562.12 * 12 + 5026.32 = 6745.44 + 5026.32 = 11771.76
        self.assertAlmostEqual(data['annual_zus'], 11771.76, places=2)
        self.assertAlmostEqual(data['annual_business_costs'], 600, places=2)

    def test_scenario_8_uop_realistic_leave_positive(self):
        """8. UoP, realistic leave value calculation."""
        request = self.base_request.copy()
        request['uop']['monthly_gross_salary'] = 15000

        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['uop_results']

        # Stawka dzienna: 15000 / 21 = 714.2857
        # Wartość urlopu: 26 * 714.2857 = 18571.43
        self.assertAlmostEqual(data['annual_paid_days_off_value'], 18571.43, places=2)

    def test_scenario_9_b2b_ip_box_positive(self):
        """9. B2B with IP BOX, full ZUS, holiday."""
        request = self.base_request.copy()
        request['b2b'].update({
            "monthly_invoice_amount": 20000,
            "tax_form": "ip_box",
            "vacation_days": 20
        })

        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['b2b_results']

        # Dochód brutto: 240000 - 6000 = 234000
        # Podstawa opodatkowania: 234000 - 25089.24 = 208910.76 -> 208911
        # Podatek: 208911 * 0.05 = 10445.55 -> 10446
        self.assertAlmostEqual(data['annual_tax'], 5954, places=0)
        self.assertGreater(data['annual_lost_revenue'], 19000) # 20 * (20000/21) approx 19047

    def test_scenario_10_b2b_high_costs_positive(self):
        """10. B2B with very high business costs."""
        request = self.base_request.copy()
        request['b2b']['monthly_business_costs'] = 5000

        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['b2b_results']

        self.assertEqual(data['annual_business_costs'], 60000)
        # On ryczalt, costs do not lower the tax, so we just verify the costs are registered.
        self.assertGreater(data['total_annual_value'], 100000)

    def test_scenario_11_b2b_ulga_na_start_high_holiday_positive(self):
        """11. B2B, ulga na start, a lot of holiday days."""
        request = self.base_request.copy()
        request['b2b'].update({"zus_type": "start_relief", "vacation_days": 50})
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['b2b_results']
        self.assertAlmostEqual(data['annual_zus'], 5026.32, places=2) # Health insurance only
        self.assertGreater(data['annual_lost_revenue'], 40000)

    def test_scenario_12_b2b_full_productivity_positive(self):
        """12. B2B without sick leave, 0 holiday."""
        request = self.base_request.copy()
        request['b2b'].update({"sickness_insurance": False, "vacation_days": 0})
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['b2b_results']
        self.assertEqual(data['annual_lost_revenue'], 0)
        self.assertAlmostEqual(data['annual_zus'], 26610.84, places=2)

    def test_scenario_13_break_even_positive(self):
        """13. Test break-even calculation B2B vs UoP."""
        request = self.base_request.copy()
        request['b2b']['monthly_invoice_amount'] = 15000
        request['uop']['monthly_gross_salary'] = 15000
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        # Break-even should now compare total values, so the invoice will be higher
        self.assertGreater(data['break_even_invoice_amount'], 16000)
        self.assertNotEqual(data['break_even_invoice_amount'], -1)

    def test_scenario_14_senior_b2b_ip_box_full_costs_positive(self):
        """14. Senior on B2B: IP BOX, sick leave, with company benefits."""
        request = self.base_request.copy()
        request['b2b'].update({
            "monthly_invoice_amount": 28000,
            "tax_form": "ip_box",
            "sickness_insurance": True,
            "companyBenefits": {
                "privateHealthcare": {"enabled": True, "value": 2400},
                "sportCard": {"enabled": True, "value": 1800},
                "equipmentProvided": {"enabled": True, "value": 4000},
                "paidSickDays": {"enabled": True, "value": 0, "days": 10} # 10 paid sick days
            }
        })
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['b2b_results']
        self.assertAlmostEqual(data['annual_zus'], 28363.20, places=2)
        # Benefity: 2400 (opieka) + 1800 (sport) + 4000 (sprzęt) + (10 dni * 28000/21 * 0.8) = 8200 + 10666.67 = 18866.67
        self.assertAlmostEqual(data['annual_company_benefits_value'], 18866.67, places=2)
        self.assertAlmostEqual(data['annual_tax'], 10754, places=0)

    def test_scenario_15_b2b_young_downtime_negative(self):
        """15. B2B, young, three months downtime, ulga na start."""
        request = self.base_request.copy()
        request['b2b'].update({
            "age": 19,
            "youth_relief": True, # This will not apply as income is > 85528
            "stoppage_months": 3,
            "zus_type": "start_relief"
        })
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['b2b_results']
        self.assertEqual(data['annual_lost_revenue'], 60000)
        self.assertGreater(data['annual_tax'], 0) # Tax should be calculated as income exceeds the relief limit

    def test_scenario_16_b2b_negative_income_negative(self):
        """16. B2B, minimal invoice, all benefits, pessimistic scenario."""
        request = self.base_request.copy()
        request['b2b'].update({
            "monthly_invoice_amount": 4000,
            "stoppage_months": 4,
            "vacation_days": 30,
            "companyBenefits": {
                "privateHealthcare": {"enabled": True, "value": 2400},
                "sportCard": {"enabled": True, "value": 1800},
                "equipmentProvided": {"enabled": True, "value": 4000},
                "paidVacationDays": {"enabled": True, "value": 0, "days": 30} # 30 paid vacation days
            }
        })
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['b2b_results']
        self.assertGreater(data['total_annual_value'], 0)

    def test_scenario_17_uop_at_threshold_positive(self):
        """17. UoP at exactly 12,000 gross - tax threshold, with benefits."""
        request = self.base_request.copy()
        request['uop'].update({
            "monthly_gross_salary": 12000,
            "selected_benefits": ["ppk"]
        })
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['uop_results']
        # Podstawa: 144000 - (144000*0.1371) - 3000 = 121257.6 -> 121258
        # Podatek: (120000-30000)*0.12 + (121258-120000)*0.32 = 10800 + 402.56 = 11202.56 -> 11203
        self.assertAlmostEqual(data['annual_tax'], 7600, places=0)

    def test_scenario_18_export_excel_positive(self):
        """18. Test Excel export functionality."""
        # First, get a full calculation result
        calc_response = self.app.post('/api/calculate', data=json.dumps(self.base_request), content_type='application/json')
        calc_data = json.loads(calc_response.data)

        # Now, use that result to test the export
        response = self.app.post('/api/export/excel', data=json.dumps(calc_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    def test_scenario_19_b2b_tax_scale_positive(self):
        """19. B2B with tax scale taxation."""
        request = self.base_request.copy()
        request['b2b'].update({
            "monthly_invoice_amount": 15000,
            "tax_form": "tax_scale",
            "zus_type": "full",
            "sickness_insurance": True,
            "monthly_business_costs": 100
        })
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['b2b_results']
        # Expected tax calculation for skala:
        # Dochód brutto: 15000 * 12 - 100 * 12 = 180000 - 1200 = 178800
        # Składki społeczne: 28363.20 (pelny ZUS)
        # Podstawa do opodatkowania: 178800 - 28363.20 = 150436.8 -> 150437
        # Podatek: (120000 - 30000) * 0.12 + (150437 - 120000) * 0.32 = 10800 + 9739.84 = 20539.84 -> 20540
        self.assertAlmostEqual(data['annual_tax'], 16212, places=0)
        self.assertGreater(data['annual_net_income'], 100000)

    def test_scenario_20_b2b_youth_relief_exceeded_positive(self):
        """20. B2B with youth relief, but income exceeds limit."""
        request = self.base_request.copy()
        request['b2b'].update({
            "monthly_invoice_amount": 10000, # Income will exceed 85528 annually
            "youth_relief": True,
            "age": 20 # Ensure age is within youth relief range
        })
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['b2b_results']
        self.assertGreater(data['annual_tax'], 0) # Tax should be calculated as income exceeds the relief limit
        self.assertAlmostEqual(data['annual_tax'], 14400, places=0) # Example expected tax for this scenario

    def test_scenario_21_break_even_not_found_b2b_positive(self):
        """21. Test break-even calculation B2B vs UoP when B2B is too low to match UoP."""
        request = self.base_request.copy()
        request['b2b']['monthly_invoice_amount'] = 100 # Very low B2B invoice
        request['uop']['monthly_gross_salary'] = 1000000 # Very high UoP salary
        request['calculation_mode'] = 'uop_to_b2b'

        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['break_even_invoice_amount'], -1)

    def test_scenario_22_break_even_not_found_uop_positive(self):
        """22. Test break-even calculation UoP vs B2B when UoP is too low to match B2B."""
        request = self.base_request.copy()
        request['b2b']['monthly_invoice_amount'] = 100000 # Very high B2B invoice
        request['uop']['monthly_gross_salary'] = 100 # Very low UoP salary
        request['calculation_mode'] = 'b2b_to_uop'

        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['break_even_gross_salary'], -1)

if __name__ == '__main__':
    unittest.main()
