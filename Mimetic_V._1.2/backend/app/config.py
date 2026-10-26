import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "mimetic_ai")
JWT_SECRET = os.getenv("JWT_SECRET", "mimetic-ai-secret-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
FROM_EMAIL = os.getenv("FROM_EMAIL", "MIMETIC <mimeticvalidated@gmail.com>")

# Gmail SMTP (fallback, no funciona en Render free tier)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USE_SSL = os.getenv("SMTP_USE_SSL", "").lower() == "true"
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# Gmail API via HTTPS (funciona desde Render)
GMAIL_API_CLIENT_ID = os.getenv("GMAIL_API_CLIENT_ID", "")
GMAIL_API_CLIENT_SECRET = os.getenv("GMAIL_API_CLIENT_SECRET", "")
GMAIL_API_REFRESH_TOKEN = os.getenv("GMAIL_API_REFRESH_TOKEN", "")

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")

# Orígenes (dominios) permitidos por CORS. Separados por comas.
CORS_ORIGINS = [
    o.strip().rstrip("/")
    for o in os.getenv(
        "CORS_ORIGINS",
        "https://mimetic-ai.vercel.app,http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173",
    ).split(",")
    if o.strip()
]
