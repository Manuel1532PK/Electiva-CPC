from fastapi import APIRouter, HTTPException, status, Depends, Query, Request
from datetime import datetime, timedelta
import random
from jose import jwt
from passlib.context import CryptContext
from bson import ObjectId
from app.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_HOURS
from app.database.mongodb import get_db
from app.models.user import VALID_ROLES, UserCreate, UserCreateByAdmin, UserLogin, UserOut, Token
from app.auth.dependencies import get_current_user
from app.rate_limit import limiter
from app.email.sender import send_verification_code

router = APIRouter(prefix="/auth", tags=["Authentication"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def user_to_out(user: dict) -> UserOut:
    return UserOut(
        id=str(user["_id"]),
        email=user.get("email", ""),
        name=user.get("name", ""),
        role=user.get("role", "paciente"),
        hospital_id=user.get("hospital_id", ""),
        first_name=user.get("first_name", ""),
        last_name=user.get("last_name", ""),
        document_type=user.get("document_type", ""),
        document_number=user.get("document_number", ""),
        birth_date=user.get("birth_date", ""),
        country=user.get("country", ""),
        department=user.get("department", ""),
        city=user.get("city", ""),
        phone=user.get("phone", ""),
        active=user.get("active", True),
        created_at=user.get("created_at", datetime.utcnow()),
    )


def create_access_token(user_id: str, hospital_id: str = "") -> str:
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {"sub": user_id, "hospital_id": hospital_id, "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


async def require_super_admin(current_user: UserOut = Depends(get_current_user)):
    if current_user.role != "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Se requiere acceso de super administrador")
    return current_user


async def require_admin(current_user: UserOut = Depends(get_current_user)):
    if current_user.role not in ("super_admin", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Se requiere acceso de administrador")
    return current_user


@router.post("/test-email")
async def test_email(data: dict, current_user: UserOut = Depends(require_admin)):
    email = data.get("email", "")
    if not email:
        raise HTTPException(status_code=400, detail="El correo electrónico es obligatorio")
    from app.email.sender import send_verification_code
    code = str(random.randint(100000, 999999))
    send_verification_code(email, code, "Test User")
    return {"message": "Email sent (check Render logs for errors)", "code_preview": code}


@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(request: Request, data: UserCreate):
    db = get_db()

    existing = await db.users.find_one({"email": data.email})
    if existing:
        if existing.get("verified"):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Este correo electrónico ya está registrado")
        else:
            if data.document_number:
                doc_exists = await db.users.find_one({"document_number": data.document_number, "_id": {"$ne": existing["_id"]}})
                if doc_exists:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Este número de documento ya está registrado")
            await db.users.update_one(
                {"_id": existing["_id"]},
                {"$set": {
                    "name": data.name,
                    "first_name": data.first_name,
                    "last_name": data.last_name,
                    "document_type": data.document_type,
                    "document_number": data.document_number,
                    "birth_date": data.birth_date,
                    "country": data.country,
                    "department": data.department,
                    "city": data.city,
                    "phone": data.phone,
                    "password_hash": pwd_context.hash(data.password),
                }},
            )
            code = str(random.randint(100000, 999999))
            await db.verification_codes.update_one(
                {"email": data.email},
                {"$set": {"code": code, "expires_at": datetime.utcnow() + timedelta(minutes=10)}},
                upsert=True,
            )
            send_verification_code(data.email, code, data.name)
            return {"message": "Verification code sent to email", "email": data.email}

    if data.document_number:
        doc_exists = await db.users.find_one({"document_number": data.document_number})
        if doc_exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Este número de documento ya está registrado")

    password_hash = pwd_context.hash(data.password)
    user_doc = {
        "email": data.email,
        "name": data.name,
        "password_hash": password_hash,
        "role": "paciente",
        "first_name": data.first_name,
        "last_name": data.last_name,
        "document_type": data.document_type,
        "document_number": data.document_number,
        "birth_date": data.birth_date,
        "country": data.country,
        "department": data.department,
        "city": data.city,
        "phone": data.phone,
        "verified": False,
        "active": True,
        "created_at": datetime.utcnow(),
    }
    result = await db.users.insert_one(user_doc)

    code = str(random.randint(100000, 999999))
    await db.verification_codes.update_one(
        {"email": data.email},
        {"$set": {"code": code, "expires_at": datetime.utcnow() + timedelta(minutes=10)}},
        upsert=True,
    )

    send_verification_code(data.email, code, data.name)
    return {"message": "Verification code sent to email", "email": data.email}


@router.post("/verify-email", response_model=Token)
@limiter.limit("10/minute")
async def verify_email(request: Request, data: dict):
    db = get_db()
    email = data.get("email")
    code = data.get("code")

    if not email or not code:
        raise HTTPException(status_code=400, detail="El correo electrónico y el código son obligatorios")

    stored = await db.verification_codes.find_one({"email": email})
    if not stored:
        raise HTTPException(status_code=400, detail="No se encontró código de verificación. Regístrate de nuevo.")

    if stored["code"] != code:
        raise HTTPException(status_code=400, detail="Código de verificación inválido")

    if stored["expires_at"] < datetime.utcnow():
        raise HTTPException(status_code=400, detail="El código de verificación expiró. Regístrate de nuevo.")

    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=400, detail="Usuario no encontrado")

    await db.users.update_one({"email": email}, {"$set": {"verified": True}})
    await db.verification_codes.delete_one({"email": email})

    user = await db.users.find_one({"email": email})
    user_id = str(user["_id"])
    access_token = create_access_token(user_id, user.get("hospital_id", ""))

    return Token(access_token=access_token, user=user_to_out(user))


@router.post("/create-user", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreateByAdmin, admin: UserOut = Depends(require_admin)):
    db = get_db()

    if data.role not in VALID_ROLES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rol inválido. Use: super_admin, admin, medico, paciente")

    if admin.role == "super_admin":
        if data.role != "super_admin" and not data.hospital_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El hospital es obligatorio")
        if data.role == "super_admin":
            data.hospital_id = ""
        else:
            hospital = await db.hospitals.find_one({"_id": ObjectId(data.hospital_id)})
            if not hospital or not hospital.get("active", True):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Hospital no encontrado o inactivo")
    elif admin.role == "admin":
        if data.role not in ("medico", "paciente"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="El administrador solo puede crear médicos y pacientes")
        if data.hospital_id and data.hospital_id != admin.hospital_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No puedes crear usuarios en otro hospital")
        data.hospital_id = admin.hospital_id
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Se requiere acceso de administrador")

    email = data.email.strip().lower()
    existing = await db.users.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Este correo electrónico ya está registrado")

    password_hash = pwd_context.hash(data.password)
    user_doc = {
        "email": email,
        "name": data.name,
        "password_hash": password_hash,
        "role": data.role,
        "hospital_id": data.hospital_id,
        "verified": True,
        "active": True,
        "created_at": datetime.utcnow(),
    }
    result = await db.users.insert_one(user_doc)
    user = await db.users.find_one({"_id": result.inserted_id})

    return user_to_out(user)


@router.get("/users", response_model=list[UserOut])
async def list_users(
    role: str = Query("", description="Filter by role"),
    hospital_id: str = Query("", description="Filter by hospital"),
    current_user: UserOut = Depends(require_admin),
):
    db = get_db()

    query: dict = {}
    if current_user.role == "admin":
        query["hospital_id"] = current_user.hospital_id
    elif hospital_id:
        query["hospital_id"] = hospital_id

    if role:
        if role not in VALID_ROLES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Filtro de rol inválido")
        query["role"] = role

    cursor = db.users.find(query).sort("created_at", -1)
    users = await cursor.to_list(length=1000)
    return [user_to_out(u) for u in users]


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(request: Request, data: UserLogin):
    db = get_db()

    user = await db.users.find_one({"email": data.email})
    if not user or not pwd_context.verify(data.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Correo electrónico o contraseña incorrectos")

    if not user.get("active", True):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cuenta deshabilitada")

    if not user.get("verified", True):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Correo electrónico no verificado")

    user_id = str(user["_id"])
    access_token = create_access_token(user_id, user.get("hospital_id", ""))

    return Token(access_token=access_token, user=user_to_out(user))


async def verify_social_token(provider: str, token: str, email: str = "", name: str = "") -> dict:
    if provider != "google":
        raise HTTPException(status_code=400, detail="Proveedor inválido. Use: Google")

    import httpx

    async with httpx.AsyncClient() as client:
        me_res = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            params={"access_token": token},
        )
        if me_res.status_code != 200:
            raise HTTPException(status_code=401, detail="Token de Google inválido")
        me_data = me_res.json()
        return {"email": me_data.get("email", email), "name": me_data.get("name", name)}


@router.post("/social-login")
@limiter.limit("10/minute")
async def social_login(request: Request, data: dict):
    db = get_db()
    provider = data.get("provider")
    token = data.get("token")

    if not provider or not token:
        raise HTTPException(status_code=400, detail="El proveedor y el token son obligatorios")

    profile = await verify_social_token(provider, token)
    email = profile["email"]
    name = profile["name"]

    user = await db.users.find_one({"email": email})
    if user:
        if not user.get("active", True):
            raise HTTPException(status_code=403, detail="Cuenta deshabilitada")
        if not user.get("verified", False):
            raise HTTPException(status_code=403, detail="Correo electrónico no verificado")
        access_token = create_access_token(str(user["_id"]), user.get("hospital_id", ""))
        return Token(access_token=access_token, user=user_to_out(user))

    return {"provider": provider, "token": token, "email": email, "name": name, "new_user": True}


@router.post("/social-register")
@limiter.limit("5/minute")
async def social_register(request: Request, data: dict):
    db = get_db()
    provider = data.get("provider")
    token = data.get("token")
    email = data.get("email", "")
    name = data.get("name", "")

    if not provider or not token or not email or not name:
        raise HTTPException(status_code=400, detail="Proveedor, token, correo electrónico y nombre son obligatorios")

    await verify_social_token(provider, token)
    existing = await db.users.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=409, detail="Este correo electrónico ya está registrado")

    doc_num = data.get("document_number", "")
    if doc_num:
        doc_exists = await db.users.find_one({"document_number": doc_num})
        if doc_exists:
            raise HTTPException(status_code=409, detail="Este número de documento ya está registrado")

    user_doc = {
        "email": email,
        "name": name,
        "password_hash": "",
        "role": "paciente",
        "first_name": data.get("first_name", ""),
        "last_name": data.get("last_name", ""),
        "document_type": data.get("document_type", ""),
        "document_number": data.get("document_number", ""),
        "birth_date": data.get("birth_date", ""),
        "country": data.get("country", ""),
        "department": data.get("department", ""),
        "city": data.get("city", ""),
        "phone": data.get("phone", ""),
        "verified": False,
        "active": True,
        "created_at": datetime.utcnow(),
    }
    result = await db.users.insert_one(user_doc)

    code = str(random.randint(100000, 999999))
    await db.verification_codes.update_one(
        {"email": email},
        {"$set": {"code": code, "expires_at": datetime.utcnow() + timedelta(minutes=10)}},
        upsert=True,
    )
    send_verification_code(email, code, name)
    return {"message": "Verification code sent to email", "email": email}


@router.get("/me", response_model=UserOut)
async def get_me(current_user: UserOut = Depends(get_current_user)):
    return current_user
