from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from bson import ObjectId
from app.config import JWT_SECRET, JWT_ALGORITHM
from app.database.mongodb import get_db

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    db = get_db()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    if not user.get("active", True):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cuenta deshabilitada")

    from app.models.user import UserOut
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
        created_at=user.get("created_at"),
    )
