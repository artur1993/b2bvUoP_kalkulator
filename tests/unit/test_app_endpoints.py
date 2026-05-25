import json
import pytest
from unittest.mock import patch
from backend.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def base_request():
    return {
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
            "customBenefits": 0,
            "companyBenefits": {}
        },
        "uop": {
            "monthly_gross_salary": 15000,
            "deductible_cost_settings": {"type": "standard"},
            "selected_benefits": [],
            "age": 30,
            "youth_relief": False
        }
    }

# ... (pozostałe testy bez zmian)

# @patch('backend.app.send_from_directory')
# @patch('backend.app.os.path.exists', return_value=True)
# def test_serve_static_file_positive(mock_exists, mock_send, client):
#     mock_send.return_value = "mocked file content"
#     response = client.get('/index.html')
#     assert response.status_code == 200
#     assert response.data == b"mocked file content"

# @patch('backend.app.send_from_directory')
# @patch('backend.app.os.path.exists', return_value=False)
# def test_serve_nonexistent_file_negative(mock_exists, mock_send, client):
#     mock_send.return_value = "mocked index.html"
#     response = client.get('/nonexistent-file.html')
#     assert response.status_code == 200
#     assert response.data == b"mocked index.html"
