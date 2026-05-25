from unittest.mock import MagicMock, patch

import pytest

from backend.app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('backend.app.calculate_break_even_analysis')
def test_break_even_analysis_endpoint_positive(mock_calculate, client):
    mock_calculate.return_value = {"some": "data"}
    response = client.post('/api/calculate/break-even-analysis', json={
        'b2b': {
            'monthly_invoice_amount': 10000,
            'monthly_business_costs': 1500,
            'zus_type': 'full',
            'tax_form': 'flat_tax',
            'sickness_insurance': True,
            'age': 30,
            'vacation_days': 26,
            'stoppage_months': 1,
            'customBenefits': 500,
            'companyBenefits': {}
        },
        'uop': {
            'monthly_gross_salary': 8000,
            'age': 30,
            'youth_relief': False,
            'deductible_cost_settings': {'type': 'standard'}
        }
    })
    assert response.status_code == 200
    assert response.json == {"some": "data"}

@patch('backend.app.run_full_calculation')
def test_calculate_endpoint_positive(mock_run_full_calculation, client):
    mock_run_full_calculation.return_value = {
        'b2b_results': {'total_annual_value': 120000},
        'uop_results': {'total_annual_value': 100000},
        'break_even_invoice_amount': 11000,
        'pension_limits_2026': {'ike': 28260},
        'analysis': {},
        'comments': 'Comparison and full analysis generated successfully.',
    }
    data = {
        'b2b': {
            'monthly_invoice_amount': 10000,
            'monthly_business_costs': 1500,
            'zus_type': 'full',
            'tax_form': 'flat_tax',
            'sickness_insurance': True,
            'age': 30,
            'vacation_days': 26,
            'stoppage_months': 1,
            'customBenefits': 500,
            'companyBenefits': {}
        },
        'uop': {
            'monthly_gross_salary': 8000,
            'age': 30,
            'youth_relief': False,
            'deductible_cost_settings': {'type': 'standard'}
        },
        'calculation_mode': 'uop_to_b2b'
    }
    response = client.post('/api/calculate', json=data)
    assert response.status_code == 200
    assert response.json['break_even_invoice_amount'] == 11000
    assert response.json['pension_limits_2026']['ike'] == 28260

def test_calculate_endpoint_rejects_removed_pension_field(client):
    removed_pension_field = 'equalize' + 'Pension'
    data = {
        'b2b': {
            'monthly_invoice_amount': 10000,
            'monthly_business_costs': 1500,
            'zus_type': 'full',
            'tax_form': 'flat_tax',
            'sickness_insurance': True,
            'age': 30,
            'vacation_days': 26,
            'stoppage_months': 1,
            'customBenefits': 500,
            'companyBenefits': {},
            removed_pension_field: True
        },
        'uop': {
            'monthly_gross_salary': 8000,
            'age': 30,
            'youth_relief': False,
            'deductible_cost_settings': {'type': 'standard'}
        },
        'calculation_mode': 'uop_to_b2b'
    }
    response = client.post('/api/calculate', json=data)
    assert response.status_code == 400
    assert response.json['error'] == 'Validation failed'

@patch('backend.app.Workbook')
def test_export_to_excel_endpoint_positive(mock_workbook, client):
    mock_wb_instance = MagicMock()
    mock_workbook.return_value = mock_wb_instance
    data = {
        'b2b_results': {'total_annual_value': 120000},
        'uop_results': {'total_annual_value': 100000}
    }
    response = client.post('/api/export/excel', json=data)
    assert response.status_code == 200
    assert response.mimetype == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
