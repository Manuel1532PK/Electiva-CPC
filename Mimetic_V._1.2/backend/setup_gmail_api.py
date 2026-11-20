"""
Obtiene el GMAIL_API_REFRESH_TOKEN usando el flujo OAuth recomendado para
aplicaciones instaladas (loopback local + PKCE). El flujo `oob` quedó obsoleto.

Uso:
    python setup_gmail_api.py CLIENT_ID CLIENT_SECRET [EMAIL]

En Google Cloud crea un cliente OAuth de tipo "Aplicación de escritorio" y
agrega como URI de redireccionamiento autorizado:
    http://127.0.0.1:8090/callback
"""
import base64
import hashlib
import json
import secrets
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

if len(sys.argv) < 3:
    print(__doc__)
    sys.exit(1)

CLIENT_ID = sys.argv[1]
CLIENT_SECRET = sys.argv[2]
EMAIL_HINT = sys.argv[3] if len(sys.argv) > 3 else ""

SCOPE = "https://www.googleapis.com/auth/gmail.send"
REDIRECT_URI = "http://127.0.0.1:8090/callback"
PORT = 8090

STATE = secrets.token_urlsafe(24)
CODE_VERIFIER = secrets.token_urlsafe(48)
CODE_CHALLENGE = (
    base64.urlsafe_b64encode(hashlib.sha256(CODE_VERIFIER.encode()).digest())
    .decode()
    .rstrip("=")
)

_received = {}


class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/callback":
            self.send_error(404)
            return

        params = urllib.parse.parse_qs(parsed.query)
        _received.update({
            "code": params.get("code", [""])[0],
            "state": params.get("state", [""])[0],
            "error": params.get("error", [""])[0],
        })

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(
            "<h2>Autorización recibida</h2>"
            "<p>Ya puedes cerrar esta pestaña y volver a la terminal.</p>".encode("utf-8")
        )

    def log_message(self, *args):
        pass


server = HTTPServer(("127.0.0.1", PORT), CallbackHandler)
thread = threading.Thread(target=server.handle_request, daemon=True)
thread.start()

params = {
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
    "response_type": "code",
    "scope": SCOPE,
    "access_type": "offline",
    "prompt": "consent",
    "state": STATE,
    "code_challenge": CODE_CHALLENGE,
    "code_challenge_method": "S256",
}
if EMAIL_HINT:
    params["login_hint"] = EMAIL_HINT

auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)

print("\n" + "=" * 70)
print("ABRE ESTA URL EN EL NAVEGADOR (ya intenté abrirla automáticamente):")
print("=" * 70)
print(auth_url)
print("=" * 70)
print(f"\nInicia sesión con {EMAIL_HINT or 'la cuenta que enviará los correos'} y autoriza el acceso.")
print("Esperando la autorización en http://127.0.0.1:8090/callback ...\n")

webbrowser.open(auth_url)
thread.join(timeout=600)
server.server_close()

if not _received:
    print("ERROR: no se recibió la autorización a tiempo.")
    sys.exit(1)

if _received.get("error"):
    print(f"ERROR de Google: {_received['error']}")
    sys.exit(1)

if _received.get("state") != STATE:
    print("ERROR: el state no coincide. Posible intento CSRF; vuelve a intentarlo.")
    sys.exit(1)

auth_code = _received.get("code", "")
if not auth_code:
    print("ERROR: Google no devolvió un código de autorización.")
    sys.exit(1)

token_data = urllib.parse.urlencode({
    "code": auth_code,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "redirect_uri": REDIRECT_URI,
    "grant_type": "authorization_code",
    "code_verifier": CODE_VERIFIER,
}).encode()

req = urllib.request.Request(
    "https://oauth2.googleapis.com/token",
    data=token_data,
    headers={"Content-Type": "application/x-www-form-urlencoded"},
)

try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        tokens = json.loads(resp.read())
except urllib.error.HTTPError as e:
    print(f"ERROR al intercambiar el código: HTTP {e.code}")
    print(e.read().decode(errors="replace"))
    sys.exit(1)

refresh_token = tokens.get("refresh_token")
if not refresh_token:
    print("\nERROR: Google no devolvió refresh_token.")
    print("Solución: revoca el acceso en https://myaccount.google.com/permissions")
    print("y vuelve a ejecutar este script.")
    sys.exit(1)

print("\n" + "=" * 70)
print("REFRESH TOKEN (copia exactamente esto):")
print("=" * 70)
print(refresh_token)
print("=" * 70)
print("\nVariables a configurar:")
print(f"  EMAIL_PROVIDER = gmail_api")
print(f"  FROM_EMAIL = MIMETIC <{EMAIL_HINT or 'tu-cuenta@gmail.com'}>")
print(f"  GMAIL_API_CLIENT_ID = {CLIENT_ID}")
print("  GMAIL_API_CLIENT_SECRET = <secreto ya configurado en la consola>")
print(f"  GMAIL_API_REFRESH_TOKEN = {refresh_token}")
