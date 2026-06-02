from collections.abc import Callable
from functools import wraps
from typing import Any, Self

from flask import current_app, g, jsonify, request
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator


class BenefitModel(BaseModel):
    enabled: bool = False
    days: int | None = 0
    value: float | None = 0.0


class B2BDataModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    monthly_invoice_amount: float = Field(..., ge=0, le=10_000_000)
    tax_form: str = Field(..., pattern="^(lump_sum_it|flat_tax|tax_scale|ip_box)$")
    zus_type: str = Field(..., pattern="^(start_relief|preferential|full)$")
    sickness_insurance: bool = False
    ip_box_qualified_share: float = Field(100.0, ge=0, le=100)
    ip_box_base_form: str = Field("flat_tax", pattern="^(flat_tax|tax_scale)$")
    monthly_business_costs: float = Field(0.0, ge=0, le=10_000_000)
    vacation_days: int = Field(0, ge=0, le=365)
    sick_days: int = Field(0, ge=0, le=365)
    stoppage_months: int = Field(0, ge=0, le=12)
    age: int = Field(..., ge=18, le=100)
    customBenefits: float = Field(0.0, ge=0, le=10_000_000)
    companyBenefits: dict[str, BenefitModel] | None = None


class DeductibleCostSettingsModel(BaseModel):
    type: str = Field(..., pattern="^(standard|elevated|author_50|none)$")
    creative_work_percentage: float | None = Field(0.0, ge=0, le=100)


class UoPDataModel(BaseModel):
    monthly_gross_salary: float = Field(..., ge=0, le=10_000_000)
    deductible_cost_settings: DeductibleCostSettingsModel
    selected_benefits: list[str] = []
    age: int = Field(..., ge=18, le=100)
    youth_relief: bool = False
    annual_bonus_pct: float = Field(0.0, ge=0, le=200)
    custom_benefits_value: float = Field(0.0, ge=0, le=10_000_000)

    @model_validator(mode="after")
    def validate_youth_relief_age(self) -> Self:
        if self.youth_relief and self.age >= 26:
            raise ValueError("Youth tax relief is available only for people under 26.")
        return self


class CalculationRequestModel(BaseModel):
    b2b: B2BDataModel
    uop: UoPDataModel
    calculation_mode: str = Field(..., pattern="^(uop_to_b2b|b2b_to_uop)$")
    language: str | None = "pl"


class BreakEvenAnalysisRequest(BaseModel):
    b2b: B2BDataModel
    uop: UoPDataModel


class ExcelExportRequest(BaseModel):
    b2b_results: dict[str, Any]
    uop_results: dict[str, Any]


def validate(model_class: type[BaseModel]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Validate a JSON request body using the given Pydantic model."""

    def decorator(f: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            try:
                json_data = request.get_json()
                if not json_data:
                    return jsonify({"error": "Request body cannot be empty."}), 400

                validated_model = model_class(**json_data)
                g.validated_data = validated_model.model_dump()
                return f(*args, **kwargs)
            except ValidationError as e:
                details = e.errors(include_context=False)
                current_app.logger.error(f"Pydantic Validation Error: {details}")
                return (
                    jsonify({"error": "Validation failed", "details": details}),
                    400,
                )
            except Exception as e:
                current_app.logger.exception(f"Unexpected validation error: {e}")
                return jsonify({"error": "Internal validation error"}), 500

        return decorated_function

    return decorator
