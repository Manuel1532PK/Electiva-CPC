import asyncio
import logging
import os

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.uri_parser import parse_uri
from app.config import MONGODB_URL, MONGODB_DB_NAME

logger = logging.getLogger("mimetic.mongodb")

client = None
db = None

DB_MAX_RETRIES = 3
DB_RETRY_DELAY = 2.0
DB_PING_TIMEOUT_S = 3.0
DB_HEALTH_SELECTION_TIMEOUT_MS = 5000


def _strip_insecure_params(url: str) -> str:
    """Elimina parametros de la URL que desactivan la verificacion de certificados TLS."""
    url = url.replace("tlsInsecure=true", "").replace("tlsAllowInvalidCertificates=true", "")
    url = url.replace("tlsAllowInvalidHostnames=true", "")
    return url.replace("&&", "&").replace("?&", "?").rstrip("&?")


def _is_local_url(url: str) -> bool:
    """True si todos los hosts de la URI son locales (sin TLS, p. ej. Docker)."""
    try:
        hosts = parse_uri(url)["nodelist"]
    except Exception:
        return False
    local_hosts = {"localhost", "127.0.0.1", "::1"}
    return bool(hosts) and all(host in local_hosts for host, _port in hosts)


def _tls_enabled(url: str) -> bool:
    """TLS por defecto en remoto (Atlas); desactivable/forzable con MONGODB_TLS."""
    override = os.getenv("MONGODB_TLS", "auto").strip().lower()
    if override in ("1", "true", "yes"):
        return True
    if override in ("0", "false", "no"):
        return False
    return not _is_local_url(url)


def _build_index_specs():
    """(collection, keys, options) para crear/garantizar índices de forma idempotente."""
    return [
        # Identidad y autenticación
        ("users", [("email", 1)], {"unique": True, "name": "users_email_unique"}),
        ("users", [("document_number", 1)], {"name": "users_document_number"}),
        # Historia clínica y sesiones
        ("clinical_histories", [("document_number", 1)], {"unique": True, "name": "clinical_histories_document_number_unique"}),
        ("sessions", [("document_number", 1), ("date", -1)], {"name": "sessions_document_date"}),
        ("sessions", [("doctor_id", 1)], {"name": "sessions_doctor_id"}),
        ("sessions", [("diagnoses.name", 1)], {"name": "sessions_diagnoses_name"}),
        # Hospitales
        ("hospitals", [("code", 1)], {"unique": True, "name": "hospitals_code_unique"}),
        # Catálogos de conocimiento
        ("symptoms", [("name", 1)], {"unique": True, "name": "symptoms_name_unique"}),
        ("symptoms", [("category", 1)], {"name": "symptoms_category"}),
        ("diseases", [("name", 1)], {"unique": True, "name": "diseases_name_unique"}),
        ("treatments", [("disease_name", 1)], {"unique": True, "name": "treatments_disease_name_unique"}),
        ("verification_codes", [("email", 1)], {"unique": True, "name": "verification_codes_email_unique"}),
    ]


async def create_indexes():
    """Crea los índices de la base de datos (idempotente). No rompe datos existentes."""
    try:
        for coll_name, keys, options in _build_index_specs():
            await db[coll_name].create_index(keys, **options)
        logger.info("Indexes created/verified")
    except Exception as e:
        logger.warning("No se pudieron crear todos los índices: %s: %s", type(e).__name__, e)


async def connect_db(*, max_retries: int = DB_MAX_RETRIES, server_selection_timeout_ms: int = 30000) -> bool:
    """Conecta a MongoDB con reintentos. Devuelve True si la conexión quedó activa."""
    global client, db
    _temp_client = None
    for attempt in range(1, max_retries + 1):
        try:
            url = _strip_insecure_params(MONGODB_URL)
            use_tls = _tls_enabled(url)
            tls_opts = (
                {"tls": True, "tlsAllowInvalidCertificates": False, "tlsAllowInvalidHostnames": False}
                if use_tls
                else {"tls": False}
            )
            _temp_client = AsyncIOMotorClient(
                url,
                serverSelectionTimeoutMS=server_selection_timeout_ms,
                connectTimeoutMS=server_selection_timeout_ms,
                **tls_opts,
            )
            _temp_db = _temp_client[MONGODB_DB_NAME]
            await _temp_db.command("ping")
            if client is not None:
                try:
                    client.close()
                except Exception:
                    pass
            client = _temp_client
            db = _temp_db
            logger.info("Connected to MongoDB (attempt %d/%d)", attempt, max_retries)
            await create_indexes()
            return True
        except Exception as e:
            if _temp_client is not None:
                try:
                    _temp_client.close()
                except Exception:
                    pass
                _temp_client = None
            logger.warning(
                "MongoDB connection attempt %d/%d failed: %s: %s",
                attempt,
                max_retries,
                type(e).__name__,
                e,
            )
            if attempt < max_retries:
                await asyncio.sleep(DB_RETRY_DELAY)
    client = None
    db = None
    return False


async def close_db():
    global client
    if client is not None:
        try:
            client.close()
        except Exception:
            pass
        logger.info("Disconnected from MongoDB")


async def db_is_ready() -> bool:
    """Ping real al servidor MongoDB. Útil para health checks."""
    if db is None:
        return False
    try:
        await asyncio.wait_for(db.command("ping"), timeout=DB_PING_TIMEOUT_S)
        return True
    except Exception:
        return False


async def ensure_connected() -> bool:
    """Verifica la conexión real y reconecta si es necesario (reconnect lazy)."""
    if await db_is_ready():
        return True
    return await connect_db(
        max_retries=1,
        server_selection_timeout_ms=DB_HEALTH_SELECTION_TIMEOUT_MS,
    )


def get_db():
    return db