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
    response = client.post('/api/calculate/break-even-analysis', json={})
    assert response.status_code == 200
    assert response.json == {"some": "data"}

@patch('src.app.calculate_sensitivity_analysis')
def test_sensitivity_analysis_endpoint_positive(mock_calculate, client):
    mock_calculate.return_value = {"some": "data"}
    response = client.post('/api/calculate/sensitivity-analysis', json={})
    assert response.status_code == 200
    assert response.json == {"some": "data"}

@patch('src.app.calculate_b2b_results')
@patch('src.app.calculate_uop_results')
@patch('src.app.calculate_break_even')
def test_calculate_endpoint_positive(mock_break_even, mock_uop, mock_b2b, client):
    mock_b2b.return_value = {'calkowita_roczna_wartosc': 120000}
    mock_uop.return_value = {'calkowita_roczna_wartosc': 100000}
    mock_break_even.return_value = 11000
    data = {
        'b2b': {'faktura_miesieczna': 10000, 'zus_rodzaj': 'pelny', 'forma_opodatkowania': 'liniowy'},
        'uop': {'wynagrodzenie_brutto': 8000},
        'calculation_mode': 'uop_to_b2b'
    }
    response = client.post('/api/calculate', json=data)
    assert response.status_code == 200
    assert response.json['break_even_faktura'] == 11000

@patch('src.app.pdf_generator.generate')
def test_export_to_pdf_endpoint_positive(mock_generate, client):
    mock_generate.return_value = b'pdf_content'
    response = client.post('/api/export/pdf', json={"b2b_results": {}, "uop_results": {}})
    assert response.status_code == 200
    assert response.data == b'pdf_content'

@patch('src.app.Workbook')
def test_export_to_excel_endpoint_positive(mock_workbook, client):
    mock_wb_instance = MagicMock()
    mock_workbook.return_value = mock_wb_instance
    data = {
        'b2b_results': {'calkowita_roczna_wartosc': 120000},
        'uop_results': {'calkowita_roczna_wartosc': 100000}
    }
    response = client.post('/api/export/excel', json=data)
    assert response.status_code == 200
    assert response.mimetype == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
