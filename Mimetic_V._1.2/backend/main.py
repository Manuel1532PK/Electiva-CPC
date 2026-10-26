from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.mongodb import connect_db, close_db, get_db, ensure_connected
from app.config import CORS_ORIGINS
from app.rate_limit import limiter
from app.logging_config import setup_logging, get_logger, LogContextMiddleware
from app.routes import diagnosis, knowledge, converse, patient, report, auth, clinical_history, hospitals, patient_portal

setup_logging()
logger = get_logger("mimetic.main")

knowledge_synced = False


async def auto_seed():
    global knowledge_synced
    db = get_db()
    if db is None:
        return
    from seed_data import symptoms, diseases, treatments
    from seed_data import _upsert_many, dedupe_collection

    logger.info("Deduplicating knowledge base (fix DuplicateKeyError)...")
    await dedupe_collection(db.symptoms, "name")
    await dedupe_collection(db.diseases, "name")
    await dedupe_collection(db.treatments, "disease_name")

    logger.info("Synchronizing knowledge base (idempotent upsert)...")
    n_s = await _upsert_many(db.symptoms, symptoms, "name")
    n_d = await _upsert_many(db.diseases, diseases, "name")
    n_t = await _upsert_many(db.treatments, treatments, "disease_name")
    knowledge_synced = True
    logger.info("Knowledge base synced: %d symptoms, %d diseases, %d treatments", n_s, n_d, n_t)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    await auto_seed()
    yield
    await close_db()


app = FastAPI(title="MIMETIC - Medical Expert System", lifespan=lifespan)

from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Demasiadas solicitudes. Intenta de nuevo más tarde."},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Ocurrió un error inesperado. Intenta de nuevo más tarde."},
    )

app.state.limiter = limiter

app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(LogContextMiddleware)

app.include_router(diagnosis.router, prefix="/api", tags=["Diagnosis"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["Knowledge Base"])
app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(converse.router, prefix="/api", tags=["Conversation"])
app.include_router(patient.router, prefix="/api", tags=["Patient"])
app.include_router(report.router, prefix="/api", tags=["Report"])
app.include_router(clinical_history.router, prefix="/api", tags=["Clinical History"])
app.include_router(hospitals.router, prefix="/api", tags=["Hospitals"])
app.include_router(patient_portal.router, prefix="/api", tags=["Patient Portal"])


@app.get("/health")
async def health():
    db_ok = await ensure_connected()
    if db_ok and not knowledge_synced:
        await auto_seed()
    return {"status": "ok" if db_ok else "degraded", "service": "MIMETIC", "database": "connected" if db_ok else "disconnected"}
