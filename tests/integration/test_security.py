from unittest.mock import patch

from backend.app import get_cors_origins, is_debug_enabled


def test_debug_mode_disabled_by_default(monkeypatch):
    monkeypatch.delenv("FLASK_ENV", raising=False)

    assert is_debug_enabled() is False


def test_debug_mode_enabled_via_env(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "development")

    assert is_debug_enabled() is True


def test_oversized_payload_rejected_with_413_negative(client):
    # Payload powyżej MAX_CONTENT_LENGTH (64 KiB) ma być odcięty przed parsowaniem.
    oversized = {"b2b": {"junk": "x" * (80 * 1024)}}
    response = client.post("/api/calculate", json=oversized)
    assert response.status_code == 413


def test_normal_payload_within_limit_accepted_positive(client):
    request_data = {
        "calculation_mode": "uop_to_b2b",
        "b2b": {
            "monthly_invoice_amount": 18000,
            "tax_form": "lump_sum_it",
            "zus_type": "full",
            "sickness_insurance": False,
            "monthly_business_costs": 0,
            "vacation_days": 0,
            "sick_days": 0,
            "stoppage_months": 0,
            "age": 30,
            "customBenefits": 0,
            "companyBenefits": {},
        },
        "uop": {
            "monthly_gross_salary": 12000,
            "deductible_cost_settings": {"type": "standard"},
            "selected_benefits": [],
            "age": 30,
            "youth_relief": False,
        },
    }
    response = client.post("/api/calculate", json=request_data)
    assert response.status_code == 200


def test_break_even_garbage_payload_returns_400(client):
    response = client.post("/api/calculate/break-even-analysis", json={"junk": 1})

    assert response.status_code == 400
    assert response.json["error"] == "Validation failed"


def test_excel_export_garbage_payload_returns_400(client):
    response = client.post("/api/export/excel", json={"junk": 1})

    assert response.status_code == 400
    assert response.json["error"] == "Validation failed"


def test_default_cors_origins(monkeypatch):
    monkeypatch.delenv("CORS_ORIGINS", raising=False)

    assert get_cors_origins() == ["http://localhost:5173"]


def test_cors_allows_default_localhost_origin(client):
    response = client.get("/api/calculate", headers={"Origin": "http://localhost:5173"})

    assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:5173"


def test_cors_blocks_unknown_origin(client):
    response = client.get("/api/calculate", headers={"Origin": "http://attacker.com"})

    assert "Access-Control-Allow-Origin" not in response.headers


def test_error_handler_no_traceback(client):
    request_data = {
        "b2b": {
            "monthly_invoice_amount": 10000,
            "monthly_business_costs": 500,
            "age": 30,
            "vacation_days": 20,
            "sick_days": 5,
            "stoppage_months": 0,
            "customBenefits": 0,
            "sickness_insurance": True,
            "zus_type": "preferential",
            "tax_form": "lump_sum_it",
        },
        "uop": {
            "monthly_gross_salary": 8000,
            "age": 30,
            "youth_relief": False,
            "deductible_cost_settings": {"type": "standard"},
        },
        "calculation_mode": "uop_to_b2b",
        "language": "pl",
    }

    with patch(
        "backend.services.calculation_service.calculate_b2b_results",
        side_effect=ValueError("secret crash detail"),
    ):
        response = client.post("/api/calculate", json=request_data)

    body = response.get_data(as_text=True)
    assert response.status_code == 500
    assert response.json == {"error": "An internal server error occurred."}
    assert "Traceback" not in body
    assert "ValueError" not in body
    assert "secret crash detail" not in body
