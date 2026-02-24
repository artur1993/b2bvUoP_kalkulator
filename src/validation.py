from functools import wraps
from flask import request, jsonify, g, current_app

def _validate_schema(schema):
    """A generic validation function that checks data against a schema."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json()
            if not data:
                return jsonify({"error": "Request body cannot be empty."}), 400

            errors = {}
            for key, rules in schema.items():
                field_errors = _validate_field(key, data.get(key), rules)
                if field_errors:
                    errors[key] = field_errors
            
            if errors:
                current_app.logger.error(f"Validation errors: {errors}")
                return jsonify({"validation_errors": errors}), 400
            
            g.validated_data = data
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def _validate_field(field_name, value, rules):
    """Validates a single field based on a set of rules."""
    errors = []
    
    if rules.get('required') and value is None:
        errors.append("is a required field.")
        return errors # No further validation needed if required field is missing

    if value is None: # If not required and not present, skip other checks
        return []

    # Attempt type conversion for numerical fields if sent as strings
    if 'type' in rules:
        expected_type = rules['type']
        if expected_type in (int, float, (int, float)):
            try:
                if isinstance(value, str):
                    value = float(value) if expected_type == float or expected_type == (int, float) else int(value)
            except (ValueError, TypeError):
                pass # Let the instance check handle it

    if 'type' in rules and not isinstance(value, rules['type']):
        expected_type = rules['type']
        if isinstance(expected_type, tuple):
            type_names = [t.__name__ for t in expected_type]
            expected_name = " or ".join(type_names)
        else:
            expected_name = expected_type.__name__
        errors.append(f"must be of type {expected_name}.")
        return errors # Type mismatch, further checks might fail
    
    if 'allowed' in rules and value not in rules['allowed']:
        errors.append(f"has an invalid value. Allowed values are: {', '.join(map(str, rules['allowed']))}.")
        
    if 'min' in rules and value < rules['min']:
        errors.append(f"must be at least {rules['min']}.")
        
    if 'max' in rules and value > rules['max']:
        errors.append(f"cannot exceed {rules['max']}.")

    if 'schema' in rules and isinstance(value, dict):
        nested_errors = {}
        for key, nested_rules in rules['schema'].items():
            field_errors = _validate_field(key, value.get(key), nested_rules)
            if field_errors:
                nested_errors[key] = field_errors
        if nested_errors:
            errors.append(nested_errors)

    return errors

# --- Schemas for different endpoints ---

CALCULATION_SCHEMA = {
    'b2b': {
        'required': True, 'type': dict, 'schema': {
            'monthly_invoice_amount': {'required': True, 'type': (int, float), 'min': 0},
            'tax_form': {'required': True, 'type': str, 'allowed': ['lump_sum_it', 'flat_tax', 'tax_scale', 'ip_box']},
            'zus_type': {'required': True, 'type': str, 'allowed': ['start_relief', 'small_business', 'preferential', 'full']},
            'sickness_insurance': {'required': False, 'type': bool},
            'monthly_business_costs': {'required': False, 'type': (int, float), 'min': 0},
            'vacation_days': {'required': False, 'type': int, 'min': 0},
            'sick_days': {'required': False, 'type': int, 'min': 0},
            'stoppage_months': {'required': False, 'type': int, 'min': 0},
            'age': {'required': True, 'type': int, 'min': 18},
            'youth_relief': {'required': False, 'type': bool},
            'customBenefits': {'required': False, 'type': (int, float), 'min': 0},
            'companyBenefits': {'required': False, 'type': dict},
            'equalizePension': {'required': False, 'type': bool}
        }
    },
    'uop': {
        'required': True, 'type': dict, 'schema': {
            'monthly_gross_salary': {'required': True, 'type': (int, float), 'min': 0},
            'deductible_cost_settings': {
                'required': True, 'type': dict, 'schema': {
                    'type': {'required': True, 'type': str, 'allowed': ['standard', 'elevated', 'author_50', 'none']},
                    'creative_work_percentage': {'required': False, 'type': (int, float), 'min': 0, 'max': 100}
                }
            },
            'selected_benefits': {'required': False, 'type': list},
            'age': {'required': True, 'type': int, 'min': 18},
            'youth_relief': {'required': False, 'type': bool}
        }
    },
    'calculation_mode': {'required': True, 'type': str, 'allowed': ['uop_to_b2b', 'b2b_to_uop']},
    'language': {'required': False, 'type': str}
}

def validate_calculation_request(f):
    """Decorator to validate the main calculation request."""
    return _validate_schema(CALCULATION_SCHEMA)(f)
