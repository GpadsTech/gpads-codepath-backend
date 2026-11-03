from unittest.mock import patch

from app.exceptions.application_exceptions import exception_handler


def test_unexpected_error_logs_traceback_without_exposing_it(client, monkeypatch):
    def fail(*args):
        raise RuntimeError("diagnostic failure")

    monkeypatch.setattr("app.services.auth_service.AuthService.authenticate", fail)
    with patch("app.exceptions.application_exceptions.logger.error") as log:
        response = client.get("/api/auth/me/")
    assert response.status_code == 500
    assert response.data["error"]["code"] == "INTERNAL_ERROR"
    assert "diagnostic failure" not in str(response.data)
    args, kwargs = log.call_args
    assert args[1:] == ("GET", "/api/auth/me/")
    assert kwargs["exc_info"][0] is RuntimeError
    assert kwargs["exc_info"][2] is not None


def test_expected_error_does_not_log_internal_failure():
    from rest_framework.exceptions import AuthenticationFailed

    with patch("app.exceptions.application_exceptions.logger.error") as log:
        response = exception_handler(AuthenticationFailed("Invalid"), {})
    assert response.status_code == 401
    log.assert_not_called()
