from src.app import is_debug_enabled


def test_debug_mode_disabled_by_default(monkeypatch):
    monkeypatch.delenv('FLASK_ENV', raising=False)

    assert is_debug_enabled() is False


def test_debug_mode_enabled_via_env(monkeypatch):
    monkeypatch.setenv('FLASK_ENV', 'development')

    assert is_debug_enabled() is True
