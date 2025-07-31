import json
import pytest
from unittest.mock import patch
from src.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def base_request():
    return {
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

# ... (pozostałe testy bez zmian)

@patch('src.app.send_from_directory')
@patch('src.app.os.path.exists', return_value=True)
def test_serve_static_file_positive(mock_exists, mock_send, client):
    mock_send.return_value = "mocked file content"
    response = client.get('/index.html')
    assert response.status_code == 200
    assert response.data == b"mocked file content"

@patch('src.app.send_from_directory')
@patch('src.app.os.path.exists', return_value=False)
def test_serve_nonexistent_file_negative(mock_exists, mock_send, client):
    mock_send.return_value = "mocked index.html"
    response = client.get('/nonexistent-file.html')
    assert response.status_code == 200
    assert response.data == b"mocked index.html"
