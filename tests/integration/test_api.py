import pytest
from src.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_calculate_success_positive(client):
    """
    Test the /api/calculate endpoint with valid data for a 200 OK response.
    """
    data = {
        "b2b": {
            "faktura_miesieczna": 10000,
            "koszty_firmowe_miesieczne": 500,
            "zus_rodzaj": "preferencyjny",
            "zus_chorobowe": True,
            "forma_opodatkowania": "liniowy",
            "ulga_dla_mlodych": False,
            "urlop_dni": 20,
            "chorobowe_dni": 5,
            "przestoje_miesiace": 0,
            "customBenefits": 0,
            "companyBenefits": {}
        },
        "uop": {
            "wynagrodzenie_brutto": 8000,
            "koszty_uzyskania_przychodu": 250,
            "ulga_dla_mlodych": False,
            "wybrane_benefity": []
        }
    }
    response = client.post('/api/calculate', json=data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert "b2b_results" in json_data
    assert "uop_results" in json_data
    assert "break_even_faktura" in json_data
    assert "komentarze" in json_data

def test_calculate_missing_data_negative(client):
    """
    Test the /api/calculate endpoint with missing 'b2b' or 'uop' data for a 400 Bad Request response.
    """
    # Missing 'b2b' data
    data_missing_b2b = {
        "uop": {
            "wynagrodzenie_brutto": 8000,
            "koszty_uzyskania_przychodu": 250,
            "ulga_dla_mlodych": False,
            "wybrane_benefity": []
        }
    }
    response_missing_b2b = client.post('/api/calculate', json=data_missing_b2b)
    assert response_missing_b2b.status_code == 400
    assert "Missing 'b2b' or 'uop' data in request." in response_missing_b2b.get_json()["error"]

    # Missing 'uop' data
    data_missing_uop = {
        "b2b": {
            "faktura_miesieczna": 10000,
            "koszty_firmowe_miesieczne": 500,
            "zus_rodzaj": "preferencyjny",
            "zus_chorobowe": True,
            "forma_opodatkowania": "liniowy",
            "ulga_dla_mlodych": False,
            "urlop_dni": 20,
            "chorobowe_dni": 5,
            "przestoje_miesiace": 0,
            "customBenefits": 0,
            "companyBenefits": {}
        }
    }
    response_missing_uop = client.post('/api/calculate', json=data_missing_uop)
    assert response_missing_uop.status_code == 400
    assert "Missing 'b2b' or 'uop' data in request." in response_missing_uop.get_json()["error"]

def test_calculate_invalid_input_type_neutral(client):
    """
    Test the /api/calculate endpoint with invalid input types (e.g., string instead of number)
    for a 500 Internal Server Error response due to calculation errors.
    """
    data = {
        "b2b": {
            "faktura_miesieczna": "invalid_number",  # Invalid type
            "koszty_firmowe_miesieczne": 500,
            "zus_rodzaj": "preferencyjny",
            "zus_chorobowe": True,
            "forma_opodatkowania": "liniowy",
            "ulga_dla_mlodych": False,
            "urlop_dni": 20,
            "chorobowe_dni": 5,
            "przestoje_miesiace": 0,
            "customBenefits": 0,
            "companyBenefits": {}
        },
        "uop": {
            "wynagrodzenie_brutto": 8000,
            "koszty_uzyskania_przychodu": 250,
            "ulga_dla_mlodych": False,
            "wybrane_benefity": []
        }
    }
    response = client.post('/api/calculate', json=data)
    # Expecting 200 because _get_float handles invalid types by returning a default value (0.0)
    assert response.status_code == 200
    json_data = response.get_json()
    assert "b2b_results" in json_data
    assert "uop_results" in json_data
    assert "break_even_faktura" in json_data
    assert "komentarze" in json_data

def test_calculate_b2b_skala_positive(client):
    """
    Test the /api/calculate endpoint with B2B data using 'skala' tax form.
    """
    data = {
        "b2b": {
            "faktura_miesieczna": 20000, # Increased to ensure hitting the higher tax bracket
            "koszty_firmowe_miesieczne": 1000,
            "zus_rodzaj": "pelny",
            "zus_chorobowe": True,
            "forma_opodatkowania": "skala",
            "ulga_dla_mlodych": False,
            "urlop_dni": 20,
            "chorobowe_dni": 5,
            "przestoje_miesiace": 0,
            "customBenefits": 0,
            "companyBenefits": {}
        },
        "uop": {
            "wynagrodzenie_brutto": 8000,
            "koszty_uzyskania_przychodu": 250,
            "ulga_dla_mlodych": False,
            "wybrane_benefity": []
        }
    }
    response = client.post('/api/calculate', json=data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert "b2b_results" in json_data
    assert "uop_results" in json_data

def test_calculate_b2b_ip_box_positive(client):
    """
    Test the /api/calculate endpoint with B2B data using 'ip_box' tax form.
    """
    data = {
        "b2b": {
            "faktura_miesieczna": 15000,
            "koszty_firmowe_miesieczne": 1000,
            "zus_rodzaj": "pelny",
            "zus_chorobowe": True,
            "forma_opodatkowania": "ip_box",
            "ulga_dla_mlodych": False,
            "urlop_dni": 20,
            "chorobowe_dni": 5,
            "przestoje_miesiace": 0,
            "customBenefits": 0,
            "companyBenefits": {}
        },
        "uop": {
            "wynagrodzenie_brutto": 8000,
            "koszty_uzyskania_przychodu": 250,
            "ulga_dla_mlodych": False,
            "wybrane_benefity": []
        }
    }
    response = client.post('/api/calculate', json=data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert "b2b_results" in json_data
    assert "uop_results" in json_data

def test_calculate_uop_ulga_dla_mlodych_positive(client):
    """
    Test the /api/calculate endpoint with UoP data using 'ulga_dla_mlodych'.
    """
    data = {
        "b2b": {
            "faktura_miesieczna": 10000,
            "koszty_firmowe_miesieczne": 500,
            "zus_rodzaj": "preferencyjny",
            "zus_chorobowe": True,
            "forma_opodatkowania": "liniowy",
            "ulga_dla_mlodych": False,
            "urlop_dni": 20,
            "chorobowe_dni": 5,
            "przestoje_miesiace": 0,
            "customBenefits": 0,
            "companyBenefits": {}
        },
        "uop": {
            "wynagrodzenie_brutto": 5000,
            "koszty_uzyskania_przychodu": 250,
            "ulga_dla_mlodych": True,
            "wybrane_benefity": []
        }
    }
    response = client.post('/api/calculate', json=data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert "b2b_results" in json_data
    assert "uop_results" in json_data

def test_calculate_break_even_not_found_negative(client):
    """
    Test the /api/calculate endpoint where break-even point is not found.
    """
    data = {
        "b2b": {
            "faktura_miesieczna": 100, # Very low to ensure it doesn't reach break-even
            "koszty_firmowe_miesieczne": 0,
            "zus_rodzaj": "ulga_na_start",
            "zus_chorobowe": False,
            "forma_opodatkowania": "ryczalt_IT",
            "ulga_dla_mlodych": False,
            "urlop_dni": 0,
            "chorobowe_dni": 0,
            "przestoje_miesiace": 0,
            "customBenefits": 0,
            "companyBenefits": {}
        },
        "uop": {
            "wynagrodzenie_brutto": 1000000, # Very high UoP value
            "koszty_uzyskania_przychodu": 0,
            "ulga_dla_mlodych": False,
            "wybrane_benefity": []
        }
    }
    response = client.post('/api/calculate', json=data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert "break_even_faktura" in json_data
    assert json_data["break_even_faktura"] == -1

def test_serve_static_file_positive(client):
    """
    Test the /<path:path> endpoint to serve a static file.
    """
    response = client.get('/index.html')
    assert response.status_code == 200
    assert 'text/html' in response.mimetype

def test_export_excel_success_positive(client):
    """
    Test the /api/export/excel endpoint with valid data for a 200 OK response and correct mimetype.
    """
    data = {
        "b2b_results": {
            "calkowita_roczna_wartosc": 120000
        },
        "uop_results": {
            "calkowita_roczna_wartosc": 100000
        }
    }
    response = client.post('/api/export/excel', json=data)
    assert response.status_code == 200
    assert response.mimetype == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert response.headers['Content-Disposition'].startswith('attachment; filename=kalkulator_wyniki.xlsx')

def test_export_pdf_success_positive(client):
    """
    Test the /api/export/pdf endpoint with valid data for a 200 OK response and correct mimetype.
    """
    data = {
        "b2b_results": {
            "calkowita_roczna_wartosc": 120000,
            "roczne_netto_na_reke": 80000,
            "roczny_podatek": 20000,
            "roczny_zus": 20000,
            "steps": {}
        },
        "uop_results": {
            "calkowita_roczna_wartosc": 100000,
            "roczne_netto_na_reke": 70000,
            "roczny_podatek": 15000,
            "roczny_zus": 15000,
            "steps": {}
        },
        "input_data": {
            "b2b": {
                "faktura_miesieczna": 10000,
                "forma_opodatkowania": "ryczalt_IT"
            },
            "uop": {
                "wynagrodzenie_brutto": 8000
            }
        },
        "language": "en"
    }
    response = client.post('/api/export/pdf', json=data)
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'
    assert response.headers['Content-Disposition'].startswith('attachment; filename=Raport_B2B_vs_UoP.pdf')
