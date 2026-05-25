import pytest
from unittest.mock import patch
import os

def test_calculate_endpoint_positive(client):
    """Test successful calculation request."""
    data = {
        'b2b': {
            'monthly_invoice_amount': 10000, 
            'monthly_business_costs': 500, 
            'age': 30, 
            'vacation_days': 20, 
            'sick_days': 5,
            'stoppage_months': 0, 
            'customBenefits': 0, 
            'sickness_insurance': True, 
            'zus_type': 'preferential', 
            'tax_form': 'lump_sum_it'
        },
        'uop': {
            'monthly_gross_salary': 8000, 
            'age': 30, 
            'youth_relief': False, 
            'deductible_cost_settings': {'type': 'standard'}
        },
        'calculation_mode': 'uop_to_b2b',
        'language': 'pl'
    }
    response = client.post('/api/calculate', json=data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert 'b2b_results' in json_data
    assert 'uop_results' in json_data
    assert 'analysis' in json_data
    assert json_data['pension_limits_2026'] == {
        'ike': 28260,
        'ikze_standard': 11304,
        'ikze_b2b': 16956,
    }

def test_calculate_endpoint_rejects_removed_pension_field(client):
    """Unknown removed pension input should be rejected."""
    removed_pension_field = 'equalize' + 'Pension'
    data = {
        'b2b': {
            'monthly_invoice_amount': 10000,
            'monthly_business_costs': 500,
            'age': 30,
            'vacation_days': 20,
            'sick_days': 5,
            'stoppage_months': 0,
            'customBenefits': 0,
            'sickness_insurance': True,
            'zus_type': 'preferential',
            'tax_form': 'lump_sum_it',
            removed_pension_field: True
        },
        'uop': {
            'monthly_gross_salary': 8000,
            'age': 30,
            'youth_relief': False,
            'deductible_cost_settings': {'type': 'standard'}
        },
        'calculation_mode': 'uop_to_b2b',
        'language': 'pl'
    }
    response = client.post('/api/calculate', json=data)
    assert response.status_code == 400

def test_calculate_endpoint_invalid_mode_negative(client):
    """Test calculation with invalid mode."""
    data = {
        'b2b': {
            'monthly_invoice_amount': 10000, 'monthly_business_costs': 500, 'age': 30, 'zus_type': 'full', 'tax_form': 'flat_tax'
        },
        'uop': {
            'monthly_gross_salary': 8000, 'age': 30, 'deductible_cost_settings': {'type': 'standard'}
        },
        'calculation_mode': 'invalid_mode'
    }
    response = client.post('/api/calculate', json=data)
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'details' in json_data # Pydantic format

def test_calculate_endpoint_missing_data_negative(client):
    """Test calculation with missing required fields."""
    data = {'calculation_mode': 'uop_to_b2b'}
    response = client.post('/api/calculate', json=data)
    assert response.status_code == 400

@patch('backend.app.os.path.exists', return_value=True)
@patch('backend.app.send_from_directory')
def test_serve_static_files(mock_send, mock_exists, client):
    """Test serving static files (assets)."""
    mock_send.return_value = "mocked file"
    response = client.get('/assets/test.js')
    assert response.status_code == 200

def test_export_excel_endpoint_positive(client):
    """Test Excel export endpoint."""
    data = {
        'b2b_results': {'total_annual_value': 120000},
        'uop_results': {'total_annual_value': 100000}
    }
    response = client.post('/api/export/excel', json=data)
    assert response.status_code == 200
    assert response.content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
