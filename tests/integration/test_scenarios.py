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
            "faktura_miesieczna": 20000,
            "forma_opodatkowania": "ryczalt_IT",
            "zus_rodzaj": "pelny",
            "zus_chorobowe": True,
            "vat": True,
            "koszty_firmowe_miesieczne": 500,
            "przestoje_miesiace": 0,
            "urlop_dni": 0,
            "wiek": 30,
            "ulga_dla_mlodych": False,
            "customBenefits": 0,
            "companyBenefits": {}
          },
          "uop": {
            "wynagrodzenie_brutto": 15000,
            "koszty_uzyskania_przychodu": 250,
            "wybrane_benefity": [],
            "wiek": 30,
            "ulga_dla_mlodych": False
          }
        }

    # --- SCENARIO TESTS WILL BE IMPLEMENTED HERE ---

    def test_scenario_1_junior_uop_youth_relief(self):
        """1. Junior on UoP with youth relief, no benefits."""
        request = self.base_request.copy()
        request['uop'].update({
            "wynagrodzenie_brutto": 7000,
            "wiek": 25,
            "ulga_dla_mlodych": True,
            "wybrane_benefity": []
        })
        
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['uop_results']

        self.assertEqual(data['roczny_podatek'], 0)
        self.assertAlmostEqual(data['roczne_netto_na_reke'], 65960.08, places=2)
        self.assertGreater(data['roczna_wartosc_platnych_dni_wolnych'], 0)

    def test_scenario_2_senior_b2b_no_benefits(self):
        """2. Senior B2B, full ZUS, no VAT/chorobowe, no benefits."""
        request = self.base_request.copy()
        request['b2b'].update({
            "faktura_miesieczna": 25000,
            "zus_rodzaj": "pelny",
            "zus_chorobowe": False
        })

        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['b2b_results']

        self.assertAlmostEqual(data['roczny_zus'], 28363.20, places=2) # No chorobowe
        self.assertAlmostEqual(data['roczna_wartosc_benefitow_od_firmy'], 0)
        self.assertGreater(data['calkowita_roczna_wartosc'], 200000)

    def test_scenario_3_b2b_no_time_off(self):
        """3. B2B with no holidays/downtime."""
        request = self.base_request.copy()
        request['b2b'].update({
            "urlop_dni": 0,
            "przestoje_miesiace": 0
        })

        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['b2b_results']

        self.assertEqual(data['roczny_utracony_przychod'], 0)

    def test_scenario_4_pessimistic_b2b_with_benefits(self):
        """4. Pessimistic: 2 months downtime, holiday, with company benefits."""
        request = self.base_request.copy()
        request['b2b'].update({
            "przestoje_miesiace": 2,
            "urlop_dni": 26,
            "companyBenefits": {
                "privateHealthcare": {"enabled": True, "value": 2400},
                "sportCard": {"enabled": True, "value": 1800},
                "paidVacationDays": {"enabled": True, "value": 0, "days": 26} # 26 paid vacation days
            }
        })

        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['b2b_results']

        # Utracony przychód: 2 miesiące przestoju (2 * 20000) = 40000. Urlop jest w pełni płatny, więc 0 utraty.
        self.assertAlmostEqual(data['roczny_utracony_przychod'], 40000, places=2)
        # Benefity: 2400 (opieka) + 1800 (sport) + (26 dni * 20000/21) = 4200 + 24761.90 = 28961.90
        self.assertAlmostEqual(data['roczna_wartosc_benefitow_od_firmy'], 28961.90, places=2)

    def test_scenario_5_uop_tax_threshold(self):
        """5. Exceeding the tax threshold on UoP."""
        request = self.base_request.copy()
        request['uop']['wynagrodzenie_brutto'] = 25000 # High salary to exceed threshold

        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['uop_results']

        self.assertAlmostEqual(data['roczny_podatek'], 54278, places=0)

    def test_scenario_6_uop_full_benefits(self):
        """6. UoP with a full set of benefits."""
        request = self.base_request.copy()
        request['uop']['wynagrodzenie_brutto'] = 15000 # Set a specific salary for consistent benefit calculation
        request['uop']['wybrane_benefity'] = ["opieka_medyczna", "karta_sportowa", "budzet_szkoleniowy", "ppk", "sprzet"]

        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['uop_results']

        # 2400 + 1800 + 3000 + 4000 + (15000*12*0.02) = 11200 + 3600 = 14800
        self.assertAlmostEqual(data['roczna_wartosc_benefitow'], 14800, places=2)

    def test_scenario_7_b2b_preferential_zus(self):
        """7. B2B preferential ZUS, minimal business costs."""
        request = self.base_request.copy()
        request['b2b'].update({
            "zus_rodzaj": "preferencyjny",
            "koszty_firmowe_miesieczne": 50
        })

        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['b2b_results']

        # (314.09 + 129.45 + 31.53 + 87.05) * 12 + 418.86 * 12 = 562.12 * 12 + 5026.32 = 6745.44 + 5026.32 = 11771.76
        self.assertAlmostEqual(data['roczny_zus'], 11771.76, places=2)
        self.assertAlmostEqual(data['roczne_koszty_firmowe'], 600, places=2)

    def test_scenario_8_uop_realistic_leave(self):
        """8. UoP, realistic leave value calculation."""
        request = self.base_request.copy()
        request['uop']['wynagrodzenie_brutto'] = 15000

        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['uop_results']

        # Stawka dzienna: 15000 / 21 = 714.2857
        # Wartość urlopu: 26 * 714.2857 = 18571.43
        self.assertAlmostEqual(data['roczna_wartosc_platnych_dni_wolnych'], 18571.43, places=2)

    def test_scenario_9_b2b_ip_box(self):
        """9. B2B with IP BOX, full ZUS, holiday."""
        request = self.base_request.copy()
        request['b2b'].update({
            "faktura_miesieczna": 20000,
            "forma_opodatkowania": "ip_box",
            "urlop_dni": 20
        })

        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['b2b_results']

        # Dochód brutto: 240000 - 6000 = 234000
        # Podstawa opodatkowania: 234000 - 25089.24 = 208910.76 -> 208911
        # Podatek: 208911 * 0.05 = 10445.55 -> 10446
        self.assertAlmostEqual(data['roczny_podatek'], 10446, places=0)
        self.assertGreater(data['roczny_utracony_przychod'], 19000) # 20 * (20000/21) approx 19047

    def test_scenario_10_b2b_high_costs(self):
        """10. B2B with very high business costs."""
        request = self.base_request.copy()
        request['b2b']['koszty_firmowe_miesieczne'] = 5000

        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['b2b_results']

        self.assertEqual(data['roczne_koszty_firmowe'], 60000)
        # On ryczalt, costs do not lower the tax, so we just verify the costs are registered.
        self.assertGreater(data['calkowita_roczna_wartosc'], 100000)

    def test_scenario_11_b2b_ulga_na_start_high_holiday(self):
        """11. B2B, ulga na start, a lot of holiday days."""
        request = self.base_request.copy()
        request['b2b'].update({"zus_rodzaj": "ulga_na_start", "urlop_dni": 50})
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['b2b_results']
        self.assertAlmostEqual(data['roczny_zus'], 5026.32, places=2) # Health insurance only
        self.assertGreater(data['roczny_utracony_przychod'], 40000)

    def test_scenario_12_b2b_full_productivity(self):
        """12. B2B without sick leave, 0 holiday."""
        request = self.base_request.copy()
        request['b2b'].update({"zus_chorobowe": False, "urlop_dni": 0})
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['b2b_results']
        self.assertEqual(data['roczny_utracony_przychod'], 0)
        self.assertAlmostEqual(data['roczny_zus'], 28363.20, places=2)

    def test_scenario_13_break_even(self):
        """13. Test break-even calculation B2B vs UoP."""
        request = self.base_request.copy()
        request['b2b']['faktura_miesieczna'] = 15000
        request['uop']['wynagrodzenie_brutto'] = 15000
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        # Break-even should now compare total values, so the invoice will be higher
        self.assertGreater(data['break_even_faktura'], 16000)
        self.assertNotEqual(data['break_even_faktura'], -1)

    def test_scenario_14_senior_b2b_ip_box_full_costs(self):
        """14. Senior on B2B: IP BOX, sick leave, with company benefits."""
        request = self.base_request.copy()
        request['b2b'].update({
            "faktura_miesieczna": 28000,
            "forma_opodatkowania": "ip_box",
            "zus_chorobowe": True,
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
        self.assertAlmostEqual(data['roczny_zus'], 30115.56, places=2)
        # Benefity: 2400 (opieka) + 1800 (sport) + 4000 (sprzęt) + (10 dni * 28000/21 * 0.8) = 8200 + 10666.67 = 18866.67
        self.assertAlmostEqual(data['roczna_wartosc_benefitow_od_firmy'], 18866.67, places=2)
        self.assertAlmostEqual(data['roczny_podatek'], 15246, places=0)

    def test_scenario_15_b2b_young_downtime(self):
        """15. B2B, young, three months downtime, ulga na start."""
        request = self.base_request.copy()
        request['b2b'].update({
            "wiek": 19,
            "ulga_dla_mlodych": True, # This will not apply as income is > 85528
            "przestoje_miesiace": 3,
            "zus_rodzaj": "ulga_na_start"
        })
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['b2b_results']
        self.assertEqual(data['roczny_utracony_przychod'], 60000)
        self.assertGreater(data['roczny_podatek'], 0) # Tax should be calculated as income exceeds the relief limit

    def test_scenario_16_b2b_negative_income(self):
        """16. B2B, minimal invoice, all benefits, pessimistic scenario."""
        request = self.base_request.copy()
        request['b2b'].update({
            "faktura_miesieczna": 4000,
            "przestoje_miesiace": 4,
            "urlop_dni": 30,
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
        self.assertGreater(data['calkowita_roczna_wartosc'], 0)

    def test_scenario_17_uop_at_threshold(self):
        """17. UoP at exactly 12,000 gross - tax threshold, with benefits."""
        request = self.base_request.copy()
        request['uop'].update({
            "wynagrodzenie_brutto": 12000,
            "wybrane_benefity": ["ppk"]
        })
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['uop_results']
        # Podstawa: 144000 - (144000*0.1371) - 3000 = 121257.6 -> 121258
        # Podatek: (120000-30000)*0.12 + (121258-120000)*0.32 = 10800 + 402.56 = 11202.56 -> 11203
        self.assertAlmostEqual(data['roczny_podatek'], 11203, places=0)

    def test_scenario_18_export_excel(self):
        """18. Test Excel export functionality."""
        # First, get a full calculation result
        calc_response = self.app.post('/api/calculate', data=json.dumps(self.base_request), content_type='application/json')
        calc_data = json.loads(calc_response.data)

        # Now, use that result to test the export
        response = self.app.post('/api/export/excel', data=json.dumps(calc_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


if __name__ == '__main__':
    unittest.main()
