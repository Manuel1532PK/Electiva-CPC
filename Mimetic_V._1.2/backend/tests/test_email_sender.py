from unittest.mock import patch

import pytest
from fastapi import HTTPException

from app.email import sender
from app.routes import auth


def test_sin_proveedor_devuelve_error_explicito(monkeypatch):
    monkeypatch.setattr(sender, "EMAIL_PROVIDER", "none")
    monkeypatch.setattr(sender, "DEV_EMAIL_FALLBACK", False)

    result = sender.send_verification_code("test@example.com", "123456", "Test")

    assert result["delivered"] is False
    assert result["provider"] is None
    assert "proveedor" in result["error"].lower()
    assert result["dev_code"] is None


def test_fallback_de_desarrollo_devuelve_codigo(monkeypatch):
    monkeypatch.setattr(sender, "EMAIL_PROVIDER", "none")
    monkeypatch.setattr(sender, "DEV_EMAIL_FALLBACK", True)

    result = sender.send_verification_code("test@example.com", "654321", "Test")

    assert result["delivered"] is True
    assert result["provider"] == "dev_fallback"
    assert result["dev_code"] == "654321"


def test_proveedor_smtp_entrega_y_reporta_exito(monkeypatch):
    monkeypatch.setattr(sender, "EMAIL_PROVIDER", "smtp")
    monkeypatch.setattr(sender, "DEV_EMAIL_FALLBACK", False)

    with patch.object(sender, "_send_smtp") as smtp:
        result = sender.send_verification_code("test@example.com", "111111", "Test")

    smtp.assert_called_once()
    assert result["delivered"] is True
    assert result["provider"] == "smtp"
    assert result["dev_code"] is None


def test_fallo_del_proveedor_se_reporta(monkeypatch):
    monkeypatch.setattr(sender, "EMAIL_PROVIDER", "smtp")
    monkeypatch.setattr(sender, "DEV_EMAIL_FALLBACK", False)

    with patch.object(sender, "_send_smtp", side_effect=RuntimeError("SMTP caído")):
        result = sender.send_verification_code("test@example.com", "222222", "Test")

    assert result["delivered"] is False
    assert "SMTP caído" in result["error"]


def test_endpoint_falla_con_503_si_no_hay_entrega():
    with patch.object(
        auth,
        "send_verification_code",
        return_value={
            "delivered": False,
            "provider": None,
            "error": "No hay proveedor de correo configurado",
            "dev_code": None,
        },
    ):
        with pytest.raises(HTTPException) as exc:
            auth._deliver_verification_code("test@example.com", "333333", "Test")

    assert exc.value.status_code == 503
    assert "No se pudo enviar" in exc.value.detail


def test_endpoint_devuelve_dev_code_cuando_hay_fallback():
    with patch.object(
        auth,
        "send_verification_code",
        return_value={
            "delivered": True,
            "provider": "dev_fallback",
            "error": None,
            "dev_code": "444444",
        },
    ):
        response = auth._deliver_verification_code("test@example.com", "444444", "Test")

    assert response["dev_code"] == "444444"
    assert "desarrollo" in response["message"]
