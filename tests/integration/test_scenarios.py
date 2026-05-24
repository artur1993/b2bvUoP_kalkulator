import unittest
import json
import pytest
from src.app import app

class ScenariosTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.base_request = {
          "b2b": {
            "monthly_invoice_amount": 20000, "tax_form": "lump_sum_it", "zus_type": "full",
            "sickness_insurance": True, "monthly_business_costs": 500, "stoppage_months": 0,
            "vacation_days": 0, "age": 30, "customBenefits": 0, "companyBenefits": {}
          },
          "uop": {
            "monthly_gross_salary": 15000, "deductible_cost_settings": {'type': 'standard'},
            "selected_benefits": [], "age": 30, "youth_relief": False
          },
          "calculation_mode": "uop_to_b2b"
        }

    def test_scenario_1_junior_uop_youth_relief_positive(self):
        request = self.base_request.copy()
        request['uop'].update({"monthly_gross_salary": 7000, "age": 25, "youth_relief": True})
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        data = json.loads(response.data)['uop_results']
        assert data['annual_tax'] == 0
        assert data['annual_net_income'] > 60000

    def test_scenario_2_senior_b2b_no_benefits_positive(self):
        request = self.base_request.copy()
        request['b2b'].update({"monthly_invoice_amount": 25000, "zus_type": "full", "sickness_insurance": False})
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        data = json.loads(response.data)['b2b_results']
        # Full ZUS 2026 without sickness: (1103.27+452.16+94.39+138.47)*12 = 1788.29*12 = 21459.48 + Zdrowotna
        assert data['annual_zus'] > 30000 

    def test_scenario_3_b2b_no_time_off_positive(self):
        request = self.base_request.copy()
        request['b2b'].update({"vacation_days": 0, "stoppage_months": 0})
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        data = json.loads(response.data)['b2b_results']
        assert data['annual_lost_revenue'] == 0

    def test_scenario_4_pessimistic_b2b_with_benefits_negative(self):
        request = self.base_request.copy()
        request['b2b'].update({
            "stoppage_months": 2, "vacation_days": 26,
            "companyBenefits": {
                "paidVacationDays": {"enabled": True, "value": 0, "days": 26}
            }
        })
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        data = json.loads(response.data)['b2b_results']
        assert data['annual_lost_revenue'] == 40000

    def test_scenario_5_uop_tax_threshold_positive(self):
        request = self.base_request.copy()
        request['uop'].update({"monthly_gross_salary": 25000})
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        data = json.loads(response.data)['uop_results']
        assert data['annual_tax'] > 40000

    def test_scenario_6_uop_full_benefits_positive(self):
        request = self.base_request.copy()
        request['uop'].update({"monthly_gross_salary": 15000, "selected_benefits": ["medical_care", "sport_card", "training_budget", "ppk"]})
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        data = json.loads(response.data)['uop_results']
        assert data['annual_benefits_value'] > 10000

    def test_scenario_7_b2b_preferential_zus_positive(self):
        request = self.base_request.copy()
        request['b2b'].update({"zus_type": "preferential", "monthly_business_costs": 50})
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        data = json.loads(response.data)['b2b_results']
        assert data['annual_zus'] > 10000

    def test_scenario_8_uop_realistic_leave_positive(self):
        request = self.base_request.copy()
        request['uop']['monthly_gross_salary'] = 15000
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        data = json.loads(response.data)['uop_results']
        assert pytest.approx(data['annual_paid_days_off_value'], 1.0) == 18571.43

    def test_scenario_9_b2b_ip_box_positive(self):
        request = self.base_request.copy()
        request['b2b'].update({"monthly_invoice_amount": 20000, "tax_form": "ip_box", "vacation_days": 20})
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        data = json.loads(response.data)['b2b_results']
        assert data['annual_tax'] < 15000

    def test_scenario_10_b2b_high_costs_positive(self):
        request = self.base_request.copy()
        request['b2b']['monthly_business_costs'] = 5000
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        data = json.loads(response.data)['b2b_results']
        assert data['annual_business_costs'] == 60000

    def test_scenario_11_b2b_ulga_na_start_high_holiday_positive(self):
        request = self.base_request.copy()
        request['b2b'].update({"zus_type": "start_relief", "vacation_days": 50})
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        data = json.loads(response.data)['b2b_results']
        assert data['annual_zus'] > 5000

    def test_scenario_12_b2b_full_productivity_positive(self):
        request = self.base_request.copy()
        request['b2b'].update({"sickness_insurance": False, "vacation_days": 0})
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        data = json.loads(response.data)['b2b_results']
        assert data['annual_lost_revenue'] == 0

    def test_scenario_13_break_even_positive(self):
        request = self.base_request.copy()
        request['b2b']['monthly_invoice_amount'] = 15000
        request['uop']['monthly_gross_salary'] = 15000
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        data = json.loads(response.data)
        assert data['break_even_invoice_amount'] > 15000

    def test_scenario_14_senior_b2b_ip_box_full_costs_positive(self):
        request = self.base_request.copy()
        request['b2b'].update({
            "monthly_invoice_amount": 28000, "tax_form": "ip_box", "sickness_insurance": True,
            "companyBenefits": {"paidSickDays": {"enabled": True, "days": 10}}
        })
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        data = json.loads(response.data)['b2b_results']
        assert data['annual_tax'] < 20000

    def test_scenario_15_b2b_young_downtime_negative(self):
        request = self.base_request.copy()
        request['b2b'].update({"age": 19, "stoppage_months": 3, "zus_type": "start_relief"})
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        data = json.loads(response.data)['b2b_results']
        assert data['annual_lost_revenue'] == 60000

    def test_scenario_16_b2b_negative_income_negative(self):
        request = self.base_request.copy()
        request['b2b'].update({"monthly_invoice_amount": 4000, "stoppage_months": 4, "vacation_days": 30})
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        data = json.loads(response.data)['b2b_results']
        assert "total_annual_value" in data

    def test_scenario_17_uop_at_threshold_positive(self):
        request = self.base_request.copy()
        request['uop'].update({"monthly_gross_salary": 12000})
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        data = json.loads(response.data)['uop_results']
        assert data['annual_tax'] > 5000

    def test_scenario_18_export_excel_positive(self):
        calc_response = self.app.post('/api/calculate', data=json.dumps(self.base_request), content_type='application/json')
        calc_data = json.loads(calc_response.data)
        response = self.app.post('/api/export/excel', data=json.dumps(calc_data), content_type='application/json')
        assert response.status_code == 200

    def test_scenario_19_b2b_tax_scale_positive(self):
        request = self.base_request.copy()
        request['b2b'].update({"monthly_invoice_amount": 15000, "tax_form": "tax_scale", "zus_type": "full"})
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        data = json.loads(response.data)['b2b_results']
        assert data['annual_tax'] > 15000

    def test_scenario_20_b2b_young_tax_positive(self):
        request = self.base_request.copy()
        request['b2b'].update({"monthly_invoice_amount": 10000, "age": 20})
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        data = json.loads(response.data)['b2b_results']
        assert data['annual_tax'] > 0

    def test_scenario_21_break_even_not_found_b2b_positive(self):
        request = self.base_request.copy()
        request['b2b']['monthly_invoice_amount'] = 100
        request['uop']['monthly_gross_salary'] = 1000000
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        data = json.loads(response.data)
        assert data['break_even_invoice_amount'] == -1

    def test_scenario_22_break_even_not_found_uop_positive(self):
        request = self.base_request.copy()
        request['b2b']['monthly_invoice_amount'] = 100000
        request['uop']['monthly_gross_salary'] = 100
        request['calculation_mode'] = 'b2b_to_uop'
        response = self.app.post('/api/calculate', data=json.dumps(request), content_type='application/json')
        data = json.loads(response.data)
        assert data['break_even_gross_salary'] == -1

import pytest
if __name__ == '__main__':
    unittest.main()
