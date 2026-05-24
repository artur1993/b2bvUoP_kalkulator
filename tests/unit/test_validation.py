def _valid_calculation_payload():
    return {
        'b2b': {
            'monthly_invoice_amount': 12000,
            'monthly_business_costs': 0,
            'zus_type': 'full',
            'tax_form': 'flat_tax',
            'sickness_insurance': False,
            'age': 24,
            'vacation_days': 0,
            'sick_days': 0,
            'stoppage_months': 0,
            'customBenefits': 0,
            'companyBenefits': {},
        },
        'uop': {
            'monthly_gross_salary': 10000,
            'deductible_cost_settings': {'type': 'standard'},
            'selected_benefits': [],
            'age': 24,
            'youth_relief': True,
        },
        'calculation_mode': 'uop_to_b2b',
        'language': 'pl',
    }


def test_pit_0_payload_rejected_for_b2b(client):
    payload = _valid_calculation_payload()
    payload['b2b']['youth_relief'] = True

    response = client.post('/api/calculate', json=payload)

    assert response.status_code == 400
    assert response.json['error'] == 'Validation failed'
    assert any(
        detail['loc'] == ['b2b', 'youth_relief']
        and detail['msg'] == 'Extra inputs are not permitted'
        for detail in response.json['details']
    )


def test_pit_0_uop_only_when_age_under_26(client):
    payload = _valid_calculation_payload()
    payload['uop']['age'] = 30
    payload['uop']['youth_relief'] = True

    response = client.post('/api/calculate', json=payload)

    assert response.status_code == 400
    assert response.json['error'] == 'Validation failed'
    assert 'Youth tax relief is available only for people under 26.' in str(response.json['details'])


def test_pit_0_uop_under_26_accepted(client):
    response = client.post('/api/calculate', json=_valid_calculation_payload())

    assert response.status_code == 200


def test_zus_type_small_business_rejected(client):
    payload = _valid_calculation_payload()
    payload['b2b']['zus_type'] = 'small_business'

    response = client.post('/api/calculate', json=payload)

    assert response.status_code == 400
    assert response.json['error'] == 'Validation failed'
    assert 'small_business' in str(response.json['details'])


def test_zus_type_start_relief_accepted(client):
    payload = _valid_calculation_payload()
    payload['b2b']['zus_type'] = 'start_relief'

    response = client.post('/api/calculate', json=payload)

    assert response.status_code == 200
    assert response.json['b2b_results']['steps']['annual_social_contributions'] == 0


def _assert_rejected(client, payload):
    response = client.post('/api/calculate', json=payload)

    assert response.status_code == 400
    assert response.json['error'] == 'Validation failed'
    return response.json['details']


def test_validation_vacation_days_over_365_rejected(client):
    payload = _valid_calculation_payload()
    payload['b2b']['vacation_days'] = 366

    details = _assert_rejected(client, payload)

    assert any(detail['loc'] == ['b2b', 'vacation_days'] for detail in details)


def test_validation_stoppage_months_over_12_rejected(client):
    payload = _valid_calculation_payload()
    payload['b2b']['stoppage_months'] = 13

    details = _assert_rejected(client, payload)

    assert any(detail['loc'] == ['b2b', 'stoppage_months'] for detail in details)


def test_validation_invoice_amount_over_10m_rejected(client):
    payload = _valid_calculation_payload()
    payload['b2b']['monthly_invoice_amount'] = 10_000_000.01

    details = _assert_rejected(client, payload)

    assert any(detail['loc'] == ['b2b', 'monthly_invoice_amount'] for detail in details)


def test_validation_age_over_100_rejected(client):
    payload = _valid_calculation_payload()
    payload['b2b']['age'] = 101

    details = _assert_rejected(client, payload)

    assert any(detail['loc'] == ['b2b', 'age'] for detail in details)


def test_validation_age_under_18_rejected(client):
    payload = _valid_calculation_payload()
    payload['b2b']['age'] = 17

    details = _assert_rejected(client, payload)

    assert any(detail['loc'] == ['b2b', 'age'] for detail in details)
