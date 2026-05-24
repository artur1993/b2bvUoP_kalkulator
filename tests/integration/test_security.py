from src.app import get_cors_origins, is_debug_enabled


def test_debug_mode_disabled_by_default(monkeypatch):
    monkeypatch.delenv('FLASK_ENV', raising=False)

    assert is_debug_enabled() is False


def test_debug_mode_enabled_via_env(monkeypatch):
    monkeypatch.setenv('FLASK_ENV', 'development')

    assert is_debug_enabled() is True


def test_break_even_garbage_payload_returns_400(client):
    response = client.post('/api/calculate/break-even-analysis', json={"junk": 1})

    assert response.status_code == 400
    assert response.json['error'] == 'Validation failed'


def test_excel_export_garbage_payload_returns_400(client):
    response = client.post('/api/export/excel', json={"junk": 1})

    assert response.status_code == 400
    assert response.json['error'] == 'Validation failed'


def test_default_cors_origins(monkeypatch):
    monkeypatch.delenv('CORS_ORIGINS', raising=False)

    assert get_cors_origins() == ['http://localhost:5173']


def test_cors_allows_default_localhost_origin(client):
    response = client.get('/api/calculate', headers={'Origin': 'http://localhost:5173'})

    assert response.headers['Access-Control-Allow-Origin'] == 'http://localhost:5173'


def test_cors_blocks_unknown_origin(client):
    response = client.get('/api/calculate', headers={'Origin': 'http://attacker.com'})

    assert 'Access-Control-Allow-Origin' not in response.headers
