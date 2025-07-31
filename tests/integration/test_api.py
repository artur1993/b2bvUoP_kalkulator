import pytest
import os
from unittest.mock import patch
from src.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('src.app.send_from_directory')
@patch('src.app.os.path.exists', return_value=True)
def test_serve_static_file_positive(mock_exists, mock_send, client):
    mock_send.return_value = "mocked file content"
    response = client.get('/index.html')
    assert response.status_code == 200
    assert response.data == b"mocked file content"

@patch('src.app.send_from_directory')
@patch('src.app.os.path.exists', return_value=False)
def test_serve_root_path_positive(mock_exists, mock_send, client):
    mock_send.return_value = "mocked index.html"
    response = client.get('/')
    assert response.status_code == 200
    assert response.data == b"mocked index.html"

@patch('src.app.os.path.exists', return_value=True)
@patch('src.app.send_from_directory')
def test_serve_existing_static_file_positive(mock_send, mock_exists, client):
    mock_send.return_value = "body { color: red; }"
    response = client.get('/test_static.css')
    assert response.status_code == 200
    assert response.data.decode('utf-8') == 'body { color: red; }'

def test_calculate_endpoint_missing_data_negative(client):
    response = client.post('/api/calculate', json={})
    assert response.status_code == 400
    assert b"Missing 'b2b' or 'uop' data" in response.data

def test_calculate_endpoint_invalid_mode_negative(client):
    data = {
        'b2b': {'faktura_miesieczna': 10000, 'zus_rodzaj': 'pelny', 'forma_opodatkowania': 'liniowy'},
        'uop': {'wynagrodzenie_brutto': 8000},
        'calculation_mode': 'invalid_mode'
    }
    response = client.post('/api/calculate', json=data)
    assert response.status_code == 400
    assert b"Invalid calculation_mode provided" in response.data

def test_export_excel_endpoint_error_path_negative(client):
    response = client.post('/api/export/excel', json=None)
    assert response.status_code == 500
    assert b"Failed to generate Excel file" in response.data

def test_export_pdf_endpoint_error_path_negative(client):
    response = client.post('/api/export/pdf', json=None)
    assert response.status_code == 500
    assert b"Failed to generate PDF file" in response.data

def test_export_advanced_pdf_endpoint_error_path_negative(client):
    response = client.post('/api/export/pdf/advanced', json=None)
    assert response.status_code == 500
    assert b"Failed to generate Advanced PDF file" in response.data

def test_break_even_analysis_no_json_negative(client):
    response = client.post('/api/calculate/break-even-analysis')
    assert response.status_code == 500

def test_sensitivity_analysis_no_json_negative(client):
    response = client.post('/api/calculate/sensitivity-analysis')
    assert response.status_code == 500

def test_calculate_no_json_negative(client):
    response = client.post('/api/calculate')
    assert response.status_code == 500


def test_export_advanced_pdf_b2b_better_positive(client):
    data = {
        'b2b_results': {'calkowita_roczna_wartosc': 150000, 'steps': {}},
        'uop_results': {'calkowita_roczna_wartosc': 100000, 'steps': {}},
        'break_even_faktura': 12000,
        'language': 'en',
        'input_data': {
            'b2b': {'faktura_miesieczna': 20000},
            'uop': {'wynagrodzenie_brutto': 15000}
        }
    }
    response = client.post('/api/export/pdf/advanced', json=data)
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'

def test_export_advanced_pdf_uop_better_positive(client):
    data = {
        'b2b_results': {'calkowita_roczna_wartosc': 100000, 'steps': {}},
        'uop_results': {'calkowita_roczna_wartosc': 150000, 'steps': {}},
        'break_even_faktura': 18000,
        'language': 'pl',
        'input_data': {
            'b2b': {'faktura_miesieczna': 15000},
            'uop': {'wynagrodzenie_brutto': 20000}
        }
    }
    response = client.post('/api/export/pdf/advanced', json=data)
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'

def test_export_advanced_pdf_similar_positive(client):
    data = {
        'b2b_results': {'calkowita_roczna_wartosc': 120000, 'steps': {}},
        'uop_results': {'calkowita_roczna_wartosc': 118000, 'steps': {}},
        'break_even_faktura': 12000,
        'language': 'en',
        'input_data': {
            'b2b': {'faktura_miesieczna': 16000},
            'uop': {'wynagrodzenie_brutto': 16000}
        }
    }
    response = client.post('/api/export/pdf/advanced', json=data)
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'

def test_calculate_with_pension_equalization_positive(client):
    data = {
        'b2b': {
            'faktura_miesieczna': 20000,
            'koszty_firmowe_miesieczne': 1500,
            'zus_rodzaj': 'pelny',
            'forma_opodatkowania': 'liniowy',
            'equalizePension': True
        },
        'uop': {
            'wynagrodzenie_brutto': 15000
        }
    }
    response = client.post('/api/calculate', json=data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert 'pension_details' in json_data
    assert json_data['pension_details']['invoice_increase'] > 0

@patch('src.app.calculate_b2b_results', side_effect=Exception('Calculation Error'))
def test_calculate_endpoint_logic_exception_negative(mock_b2b, client):
    data = {
        'b2b': {'faktura_miesieczna': 10000, 'zus_rodzaj': 'pelny', 'forma_opodatkowania': 'liniowy'},
        'uop': {'wynagrodzenie_brutto': 8000}
    }
    response = client.post('/api/calculate', json=data)
    assert response.status_code == 500
    assert b"An internal server error occurred" in response.data

def test_calculate_endpoint_incomplete_b2b_data_negative(client):
    data = {
        'b2b': {'faktura_miesieczna': 10000},
        'uop': {'wynagrodzenie_brutto': 8000}
    }
    response = client.post('/api/calculate', json=data)
    assert response.status_code == 500

def test_calculate_endpoint_incomplete_uop_data_negative(client):
    data = {
        'b2b': {'faktura_miesieczna': 10000, 'zus_rodzaj': 'pelny', 'forma_opodatkowania': 'liniowy'},
        'uop': {}
    }
    response = client.post('/api/calculate', json=data)
    assert response.status_code == 400