import pytest
from flask import Flask

@pytest.fixture
def app():
    from server import app
    app.config.update({
        "TESTING": True,
    })
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_err(client, app):
    from server import err
    from cache_engine import err_hist

    err_hist.clear()

    with app.test_request_context('/test-path'):
        response, status_code = err("Test error message", code=404, etype="TEST_ERROR")

        assert status_code == 404
        assert response.json == {"status": "error", "message": "Test error message"}

        errors = err_hist.recent(1)
        assert len(errors) == 1
        assert errors[0]["error_type"] == "TEST_ERROR"
        assert errors[0]["detail"] == "Test error message"
        assert errors[0]["context"] == {"path": "/test-path"}

def test_err_default_args(client, app):
    from server import err
    from cache_engine import err_hist

    err_hist.clear()

    with app.test_request_context('/test-default-path'):
        response, status_code = err("Default test error")

        assert status_code == 400
        assert response.json == {"status": "error", "message": "Default test error"}

        errors = err_hist.recent(1)
        assert len(errors) == 1
        assert errors[0]["error_type"] == "API_ERROR"
        assert errors[0]["detail"] == "Default test error"
        assert errors[0]["context"] == {"path": "/test-default-path"}
