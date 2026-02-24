import pytest
from unittest.mock import patch, MagicMock
from src.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('src.app.calculate_break_even_analysis')
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
            'youth_relief': False,
            'vacation_days': 26,
            'stoppage_months': 1,
            'customBenefits': 500,
            'companyBenefits': {},
            'equalizePension': False
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

@patch('src.app.calculate_b2b_results')
@patch('src.app.calculate_uop_results')
@patch('src.app.calculate_break_even')
def test_calculate_endpoint_positive(mock_break_even, mock_uop, mock_b2b, client):
    mock_b2b.return_value = {'total_annual_value': 120000}
    mock_uop.return_value = {'total_annual_value': 100000}
    mock_break_even.return_value = 11000
    data = {
        'b2b': {
            'monthly_invoice_amount': 10000,
            'monthly_business_costs': 1500,
            'zus_type': 'full',
            'tax_form': 'flat_tax',
            'sickness_insurance': True,
            'age': 30,
            'youth_relief': False,
            'vacation_days': 26,
            'stoppage_months': 1,
            'customBenefits': 500,
            'companyBenefits': {},
            'equalizePension': False
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

@patch('src.app.Workbook')
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
