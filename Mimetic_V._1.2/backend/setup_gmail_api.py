"""
Script para obtener el refresh token de Gmail API.
Uso: python setup_gmail_api.py CLIENT_ID CLIENT_SECRET
"""
import sys
import json
import urllib.request
import urllib.parse

CLIENT_ID = sys.argv[1]
CLIENT_SECRET = sys.argv[2]

SCOPE = "https://www.googleapis.com/auth/gmail.send"
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"

auth_url = (
    "https://accounts.google.com/o/oauth2/v2/auth?"
    + urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPE,
        "access_type": "offline",
        "prompt": "consent",
    })
)

print("\n" + "=" * 60)
print("ABRE ESTA URL EN EL NAVEGADOR:")
print("=" * 60)
print(auth_url)
print("=" * 60)
print("\nInicia sesion con mimeticvalidated@gmail.com")
print("Autoriza, copia el codigo y PEGALO AQUI ABAJO:\n")

auth_code = input().strip()

data = urllib.parse.urlencode({
    "code": auth_code,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "redirect_uri": REDIRECT_URI,
    "grant_type": "authorization_code",
}).encode()

req = urllib.request.Request(
    "https://oauth2.googleapis.com/token",
    data=data,
    headers={"Content-Type": "application/x-www-form-urlencoded"},
)

with urllib.request.urlopen(req) as resp:
    token_data = json.loads(resp.read())

refresh_token = token_data.get("refresh_token")
if not refresh_token:
    print("\nERROR: No se obtuvo refresh token.")
    print("Posible causa: ya se uso este codigo o la cuenta no es mimeticvalidated@gmail.com.")
    sys.exit(1)

print("\n" + "=" * 60)
print("REFRESH TOKEN (copia exactamente esto):")
print("=" * 60)
print(refresh_token)
print("=" * 60)
print("\nAgrega estas 3 variables a Render > Environment:")
print(f"  GMAIL_API_CLIENT_ID = {CLIENT_ID}")
print(f"  GMAIL_API_CLIENT_SECRET = {CLIENT_SECRET}")
print(f"  GMAIL_API_REFRESH_TOKEN = {refresh_token}")
