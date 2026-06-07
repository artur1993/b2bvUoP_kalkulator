import pytest
from pydantic import ValidationError
from backend.validation import (
    BenefitModel,
    B2BDataModel,
    DeductibleCostSettingsModel,
    UoPDataModel,
    CalculationRequestModel,
)


def _valid_b2b_data():
    return {
        "monthly_invoice_amount": 10000.0,
        "tax_form": "flat_tax",
        "zus_type": "full",
        "age": 30,
    }


def _valid_uop_data():
    return {
        "monthly_gross_salary": 10000.0,
        "deductible_cost_settings": {"type": "standard"},
        "age": 30,
    }


def _valid_calculation_request():
    return {
        "b2b": _valid_b2b_data(),
        "uop": _valid_uop_data(),
        "calculation_mode": "uop_to_b2b",
    }


# --- BenefitModel Tests ---


def test_benefit_model_valid():
    BenefitModel(enabled=True, days=10, value=100.0)


def test_benefit_model_defaults():
    benefit = BenefitModel()
    assert benefit.enabled is False
    assert benefit.days == 0
    assert benefit.value == 0.0


# --- B2BDataModel Tests ---


def test_b2b_model_valid():
    B2BDataModel(**_valid_b2b_data())


@pytest.mark.parametrize(
    "field, value",
    [
        ("monthly_invoice_amount", -1),
        ("monthly_invoice_amount", 10_000_001),
        ("tax_form", "invalid"),
        ("zus_type", "small_business"),  # legacy, now rejected
        ("ip_box_qualified_share", -1),
        ("ip_box_qualified_share", 101),
        ("ip_box_base_form", "lump_sum_it"),  # invalid pattern
        ("monthly_business_costs", -0.1),
        ("vacation_days", -1),
        ("vacation_days", 366),
        ("sick_days", -1),
        ("sick_days", 366),
        ("stoppage_months", -1),
        ("stoppage_months", 13),
        ("age", 17),
        ("age", 101),
        ("customBenefits", -1),
    ],
)
def test_b2b_model_invalid_fields(field, value):
    data = _valid_b2b_data()
    data[field] = value
    with pytest.raises(ValidationError):
        B2BDataModel(**data)


def test_b2b_model_required_fields():
    for field in ["monthly_invoice_amount", "tax_form", "zus_type", "age"]:
        data = _valid_b2b_data()
        del data[field]
        with pytest.raises(ValidationError):
            B2BDataModel(**data)


def test_b2b_model_extra_forbid():
    data = _valid_b2b_data()
    data["extra_field"] = "foo"
    with pytest.raises(ValidationError):
        B2BDataModel(**data)


def test_b2b_model_youth_relief_forbidden():
    # youth_relief is not in B2BDataModel, should be rejected by extra="forbid"
    data = _valid_b2b_data()
    data["youth_relief"] = True
    with pytest.raises(ValidationError):
        B2BDataModel(**data)


# --- DeductibleCostSettingsModel Tests ---


@pytest.mark.parametrize("cost_type", ["standard", "elevated", "author_50", "none"])
def test_deductible_costs_valid(cost_type):
    DeductibleCostSettingsModel(type=cost_type)


def test_deductible_costs_invalid_type():
    with pytest.raises(ValidationError):
        DeductibleCostSettingsModel(type="invalid")


@pytest.mark.parametrize("percentage", [-0.1, 100.1])
def test_deductible_costs_invalid_percentage(percentage):
    with pytest.raises(ValidationError):
        DeductibleCostSettingsModel(type="author_50", creative_work_percentage=percentage)


# --- UoPDataModel Tests ---


def test_uop_model_valid():
    UoPDataModel(**_valid_uop_data())


@pytest.mark.parametrize(
    "field, value",
    [
        ("monthly_gross_salary", -1),
        ("age", 17),
        ("age", 101),
    ],
)
def test_uop_model_invalid_fields(field, value):
    data = _valid_uop_data()
    data[field] = value
    with pytest.raises(ValidationError):
        UoPDataModel(**data)


def test_uop_youth_relief_valid_age():
    UoPDataModel(
        monthly_gross_salary=5000,
        deductible_cost_settings={"type": "standard"},
        age=25,
        youth_relief=True,
    )


def test_uop_youth_relief_invalid_age():
    with pytest.raises(ValidationError) as excinfo:
        UoPDataModel(
            monthly_gross_salary=5000,
            deductible_cost_settings={"type": "standard"},
            age=26,
            youth_relief=True,
        )
    assert "Youth tax relief is available only for people under 26" in str(excinfo.value)


# --- CalculationRequestModel Tests ---


def test_calculation_request_valid():
    CalculationRequestModel(**_valid_calculation_request())


@pytest.mark.parametrize("mode", ["uop_to_b2b", "b2b_to_uop", "employer_budget"])
def test_calculation_request_modes(mode):
    data = _valid_calculation_request()
    data["calculation_mode"] = mode
    CalculationRequestModel(**data)


def test_calculation_request_invalid_mode():
    data = _valid_calculation_request()
    data["calculation_mode"] = "invalid"
    with pytest.raises(ValidationError):
        CalculationRequestModel(**data)


# --- Endpoint Integration Tests (verify decorator/response) ---


def test_api_calculate_valid_payload(client):
    response = client.post("/api/calculate", json=_valid_calculation_request())
    assert response.status_code == 200


def test_api_calculate_empty_payload(client):
    response = client.post("/api/calculate", json={})
    assert response.status_code == 400
    assert response.json["error"] == "Request body cannot be empty."


def test_api_calculate_validation_failure_details(client):
    data = _valid_calculation_request()
    data["b2b"]["monthly_invoice_amount"] = -1
    response = client.post("/api/calculate", json=data)

    assert response.status_code == 400
    assert response.json["error"] == "Validation failed"
    assert "details" in response.json
    assert any(d["loc"] == ["b2b", "monthly_invoice_amount"] for d in response.json["details"])
