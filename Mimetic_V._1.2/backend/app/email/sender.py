import smtplib
import json
import base64
import threading
import logging
from datetime import datetime
import urllib.request
import urllib.parse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import (
    SMTP_HOST, SMTP_PORT, SMTP_USE_SSL, SMTP_USER, SMTP_PASSWORD,
    SENDGRID_API_KEY, FROM_EMAIL,
    GMAIL_API_CLIENT_ID, GMAIL_API_CLIENT_SECRET, GMAIL_API_REFRESH_TOKEN,
)

logger = logging.getLogger(__name__)


def _build_html(code: str, name: str) -> str:
    greeting = f"Hola, <strong>{name}</strong>," if name else "Hola,"
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin:0; padding:0; background-color:#f4f6fb; font-family:'Segoe UI', Arial, Helvetica, sans-serif;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" bgcolor="#f4f6fb" style="padding:32px 16px;">
            <tr>
                <td align="center">
                    <table role="presentation" cellspacing="0" cellpadding="0" width="520" style="max-width:520px; width:100%; background-color:#ffffff; border-radius:16px; overflow:hidden; box-shadow:0 8px 30px rgba(99,102,241,0.12); border:1px solid #e5e9f4;">
                        <!-- Header -->
                        <tr>
                            <td style="background:linear-gradient(135deg,#4f46e5 0%,#7c3aed 100%); padding:32px 40px; text-align:center;">
                                <div style="font-size:13px; letter-spacing:6px; color:#c7d2fe; text-transform:uppercase; font-weight:600;">Semillero Quantum · UNIMINUTO</div>
                                <div style="font-size:30px; font-weight:800; color:#ffffff; margin-top:8px; letter-spacing:1px;">MIMETIC</div>
                                <div style="font-size:14px; color:#e0e7ff; margin-top:4px;">Sistema de apoyo al diagnóstico médico</div>
                            </td>
                        </tr>
                        <!-- Body -->
                        <tr>
                            <td style="padding:36px 40px 28px 40px;">
                                <div style="font-size:20px; color:#1e293b; font-weight:700; margin-bottom:12px;">Verificación de cuenta</div>
                                <div style="font-size:15px; color:#475569; line-height:1.7;">
                                    {greeting}
                                    <br><br>
                                    Para completar el registro en <strong>MIMETIC</strong>, ingresa el siguiente
                                    código de verificación de <strong>6 dígitos</strong> en la aplicación:
                                </div>

                                <!-- Code box -->
                                <div style="margin:28px 0 24px 0; text-align:center;">
                                    <div style="display:inline-block; background:#eef2ff; border:2px dashed #a5b4fc; border-radius:14px; padding:20px 32px;">
                                        <div style="font-size:14px; color:#6366f1; font-weight:600; letter-spacing:2px; margin-bottom:6px;">TU CÓDIGO DE VERIFICACIÓN</div>
                                        <div style="font-size:38px; font-weight:800; letter-spacing:10px; color:#1e293b; font-family:Consolas, 'Courier New', monospace;">{code}</div>
                                    </div>
                                </div>

                                <div style="font-size:14px; color:#64748b; line-height:1.6; text-align:center;">
                                    ⏱️ Este código expira en <strong>10 minutos</strong>.<br>
                                    No lo compartas con nadie.
                                </div>
                            </td>
                        </tr>
                        <!-- Footer -->
                        <tr>
                            <td style="padding:20px 40px 32px 40px; background-color:#f8faff; border-top:1px solid #eceff8;">
                                <div style="font-size:13px; color:#94a3b8; line-height:1.6; text-align:center;">
                                    Si no solicitaste este código, ignora este mensaje y protege tu cuenta.
                                    <br><br>
                                    <span style="color:#94a3b8;">Semillero Quantum · UNIMINUTO</span>
                                    <br>
                                    <span style="color:#b3bccc;">© {datetime.now().year} MIMETIC. Todos los derechos reservados.</span>
                                </div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


def _send_smtp(to_email: str, html: str):
    msg = MIMEMultipart()
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = "Código de verificación - MIMETIC"
    msg.attach(MIMEText(html, "html"))

    if SMTP_USE_SSL:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
    else:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
    logger.info(f"Email sent via SMTP to {to_email}")


def _send_sendgrid(to_email: str, html: str):
    data = json.dumps({
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": "mimeticvalidated@gmail.com", "name": "MIMETIC"},
        "subject": "Código de verificación - MIMETIC",
        "content": [{"type": "text/html", "value": html}],
    }).encode()
    req = urllib.request.Request(
        "https://api.sendgrid.com/v3/mail/send",
        data=data,
        headers={
            "Authorization": f"Bearer {SENDGRID_API_KEY}",
            "Content-Type": "application/json",
        },
    )
    urllib.request.urlopen(req, timeout=15)
    logger.info(f"Email sent via SendGrid to {to_email}")


def _send_gmail_api(to_email: str, html: str):
    import time

    data = urllib.parse.urlencode({
        "client_id": GMAIL_API_CLIENT_ID,
        "client_secret": GMAIL_API_CLIENT_SECRET,
        "refresh_token": GMAIL_API_REFRESH_TOKEN,
        "grant_type": "refresh_token",
    }).encode()
    token_req = urllib.request.Request(
        "https://oauth2.googleapis.com/token", data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(token_req, timeout=15) as resp:
        token_data = json.loads(resp.read())
    access_token = token_data["access_token"]

    msg = MIMEText(html, "html")
    msg["From"] = "MIMETIC <mimeticvalidated@gmail.com>"
    msg["To"] = to_email
    msg["Subject"] = "Código de verificación - MIMETIC"
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    body = json.dumps({"raw": raw}).encode()
    send_req = urllib.request.Request(
        "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
        data=body,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(send_req, timeout=15) as resp:
        logger.info(f"Email sent via Gmail API to {to_email}: {resp.status}")


def _send(to_email: str, code: str, name: str):
    html = _build_html(code, name)

    if GMAIL_API_CLIENT_ID and GMAIL_API_CLIENT_SECRET and GMAIL_API_REFRESH_TOKEN:
        try:
            _send_gmail_api(to_email, html)
            return
        except Exception as e:
            logger.error(f"Gmail API failed for {to_email}: {e}")

    if SENDGRID_API_KEY:
        try:
            _send_sendgrid(to_email, html)
            return
        except Exception as e:
            logger.error(f"SendGrid failed for {to_email}: {e}")

    if SMTP_USER and SMTP_PASSWORD:
        try:
            _send_smtp(to_email, html)
            return
        except Exception as e:
            logger.error(f"SMTP failed for {to_email}: {e}")

    logger.warning(f"No email provider configured, unable to send to {to_email}")


def send_verification_code(to_email: str, code: str, name: str):
    threading.Thread(target=_send, args=(to_email, code, name), daemon=True).start()
