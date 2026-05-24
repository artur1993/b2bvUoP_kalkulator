from functools import wraps
from flask import request, jsonify, g, current_app
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator
from typing import Optional, List, Dict, Union

class BenefitModel(BaseModel):
    enabled: bool = False
    days: Optional[int] = 0
    value: Optional[float] = 0.0

class B2BDataModel(BaseModel):
    model_config = ConfigDict(extra='forbid')

    monthly_invoice_amount: float = Field(..., ge=0)
    tax_form: str = Field(..., pattern='^(lump_sum_it|flat_tax|tax_scale|ip_box)$')
    zus_type: str = Field(..., pattern='^(start_relief|preferential|full)$')
    sickness_insurance: bool = False
    ip_box_qualified_share: float = Field(100.0, ge=0, le=100)
    ip_box_base_form: str = Field('flat_tax', pattern='^(flat_tax|tax_scale)$')
    monthly_business_costs: float = Field(0.0, ge=0)
    vacation_days: int = Field(0, ge=0)
    sick_days: int = Field(0, ge=0)
    stoppage_months: int = Field(0, ge=0)
    age: int = Field(..., ge=18)
    customBenefits: float = Field(0.0, ge=0)
    companyBenefits: Optional[Dict[str, BenefitModel]] = None

class DeductibleCostSettingsModel(BaseModel):
    type: str = Field(..., pattern='^(standard|elevated|author_50|none)$')
    creative_work_percentage: Optional[float] = Field(0.0, ge=0, le=100)

class UoPDataModel(BaseModel):
    monthly_gross_salary: float = Field(..., ge=0)
    deductible_cost_settings: DeductibleCostSettingsModel
    selected_benefits: List[str] = []
    age: int = Field(..., ge=18)
    youth_relief: bool = False

    @model_validator(mode='after')
    def validate_youth_relief_age(self):
        if self.youth_relief and self.age >= 26:
            raise ValueError('Youth tax relief is available only for people under 26.')
        return self

class CalculationRequestModel(BaseModel):
    b2b: B2BDataModel
    uop: UoPDataModel
    calculation_mode: str = Field(..., pattern='^(uop_to_b2b|b2b_to_uop)$')
    language: Optional[str] = "pl"

def validate_calculation_request(f):
    """Decorator to validate the main calculation request using Pydantic."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            json_data = request.get_json()
            if not json_data:
                return jsonify({"error": "Request body cannot be empty."}), 400
            
            validated_model = CalculationRequestModel(**json_data)
            # Store as dict for compatibility with existing logic
            g.validated_data = validated_model.model_dump()
            return f(*args, **kwargs)
        except ValidationError as e:
            details = e.errors(include_context=False)
            current_app.logger.error(f"Pydantic Validation Error: {details}")
            return jsonify({
                "error": "Validation failed",
                "details": details
            }), 400
        except Exception as e:
            current_app.logger.exception(f"Unexpected validation error: {e}")
            return jsonify({"error": "Internal validation error"}), 500
            
    return decorated_function
