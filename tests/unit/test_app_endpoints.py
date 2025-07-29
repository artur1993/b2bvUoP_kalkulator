import unittest
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from app import app, calculate_b2b_results, calculate_uop_results

class AppEndpointsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
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

    def test_calculate_missing_data_negative(self):
        response = self.app.post('/api/calculate', data=json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], "Missing 'b2b' or 'uop' data in request.")

    def test_calculate_invalid_calculation_mode_negative(self):
        request = self.base_request.copy()
        request['calculation_mode'] = 'invalid_mode'
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], "Invalid calculation_mode provided.")

    def test_export_excel_empty_data_negative(self):
        response = self.app.post('/api/export/excel', data=json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    def test_export_pdf_empty_data_negative(self):
        response = self.app.post('/api/export/pdf', data=json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], "Invalid request body")

    def test_export_advanced_pdf_empty_data_negative(self):
        response = self.app.post('/api/export/pdf/advanced', data=json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], "Invalid request body")

    def test_serve_static_file_positive(self):
        # This test requires a file in the static folder
        # Let's assume index.html exists
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'text/html')

    def test_serve_nonexistent_file_negative(self):
        response = self.app.get('/nonexistent-file.html')
        self.assertEqual(response.status_code, 200) # Should serve index.html
        self.assertEqual(response.mimetype, 'text/html')

    def test_calculate_b2b_liniowy_positive(self):
        b2b_data = self.base_request['b2b'].copy()
        b2b_data['forma_opodatkowania'] = 'liniowy'
        results = calculate_b2b_results(b2b_data)
        self.assertGreater(results['roczny_podatek'], 0)

    def test_calculate_b2b_skala_positive(self):
        b2b_data = self.base_request['b2b'].copy()
        b2b_data['forma_opodatkowania'] = 'skala'
        results = calculate_b2b_results(b2b_data)
        self.assertGreater(results['roczny_podatek'], 0)

    def test_calculate_b2b_ip_box_positive(self):
        b2b_data = self.base_request['b2b'].copy()
        b2b_data['forma_opodatkowania'] = 'ip_box'
        results = calculate_b2b_results(b2b_data)
        self.assertGreater(results['roczny_podatek'], 0)

    def test_calculate_uop_elevated_kup_positive(self):
        uop_data = self.base_request['uop'].copy()
        uop_data['kup_settings'] = {'type': 'elevated'}
        results = calculate_uop_results(uop_data)
        self.assertGreater(results['roczny_podatek'], 0)

    def test_calculate_uop_autorskie_50_kup_positive(self):
        uop_data = self.base_request['uop'].copy()
        uop_data['kup_settings'] = {'type': 'autorskie_50', 'creative_work_percentage': 50}
        results = calculate_uop_results(uop_data)
        self.assertGreater(results['roczny_podatek'], 0)

if __name__ == '__main__':
    unittest.main()