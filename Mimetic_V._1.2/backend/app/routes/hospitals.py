from fastapi import APIRouter, HTTPException, status, Depends, Query
from datetime import datetime
from bson import ObjectId
from app.database.mongodb import get_db
from app.models.hospital import HospitalCreate, HospitalUpdate, HospitalOut
from app.routes.auth import require_super_admin
from app.models.user import UserOut

router = APIRouter(prefix="/hospitals", tags=["Hospitals"])


def hospital_to_out(h: dict) -> HospitalOut:
    return HospitalOut(
        id=str(h["_id"]),
        name=h.get("name", ""),
        code=h.get("code", ""),
        address=h.get("address", ""),
        phone=h.get("phone", ""),
        email=h.get("email", ""),
        active=h.get("active", True),
        created_at=h.get("created_at", datetime.utcnow()),
    )


@router.get("", response_model=list[HospitalOut])
async def list_hospitals(
    include_inactive: bool = Query(False, description="Include inactive hospitals"),
    admin: UserOut = Depends(require_super_admin),
):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Base de datos no disponible")

    query = {} if include_inactive else {"active": True}
    cursor = db.hospitals.find(query).sort("name", 1)
    hospitals = await cursor.to_list(length=1000)
    return [hospital_to_out(h) for h in hospitals]


@router.post("", response_model=HospitalOut, status_code=status.HTTP_201_CREATED)
async def create_hospital(
    data: HospitalCreate,
    admin: UserOut = Depends(require_super_admin),
):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Base de datos no disponible")

    code = data.code.strip().upper()
    existing_code = await db.hospitals.find_one({"code": code})
    if existing_code:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El código del hospital ya existe")

    doc = {
        "name": data.name.strip(),
        "code": code,
        "address": data.address.strip(),
        "phone": data.phone.strip(),
        "email": data.email.strip(),
        "active": True,
        "created_at": datetime.utcnow(),
    }
    result = await db.hospitals.insert_one(doc)
    created = await db.hospitals.find_one({"_id": result.inserted_id})
    return hospital_to_out(created)


@router.get("/{hospital_id}", response_model=HospitalOut)
async def get_hospital(
    hospital_id: str,
    admin: UserOut = Depends(require_super_admin),
):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Base de datos no disponible")

    hospital = await db.hospitals.find_one({"_id": ObjectId(hospital_id)})
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital no encontrado")

    return hospital_to_out(hospital)


@router.put("/{hospital_id}", response_model=HospitalOut)
async def update_hospital(
    hospital_id: str,
    data: HospitalUpdate,
    admin: UserOut = Depends(require_super_admin),
):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Base de datos no disponible")

    existing = await db.hospitals.find_one({"_id": ObjectId(hospital_id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Hospital no encontrado")

    update = {}
    if data.name is not None:
        update["name"] = data.name.strip()
    if data.code is not None:
        new_code = data.code.strip().upper()
        code_exists = await db.hospitals.find_one({"code": new_code, "_id": {"$ne": ObjectId(hospital_id)}})
        if code_exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El código del hospital ya existe")
        update["code"] = new_code
    if data.address is not None:
        update["address"] = data.address.strip()
    if data.phone is not None:
        update["phone"] = data.phone.strip()
    if data.email is not None:
        update["email"] = data.email.strip()
    if data.active is not None:
        update["active"] = data.active

    if update:
        await db.hospitals.update_one({"_id": ObjectId(hospital_id)}, {"$set": update})

    updated = await db.hospitals.find_one({"_id": ObjectId(hospital_id)})
    return hospital_to_out(updated)


@router.delete("/{hospital_id}")
async def delete_hospital(
    hospital_id: str,
    admin: UserOut = Depends(require_super_admin),
):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Base de datos no disponible")

    existing = await db.hospitals.find_one({"_id": ObjectId(hospital_id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Hospital no encontrado")

    users_in_hospital = await db.users.count_documents({"hospital_id": hospital_id})
    if users_in_hospital > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot delete hospital with {users_in_hospital} active users. Deactivate it instead.",
        )

    await db.hospitals.delete_one({"_id": ObjectId(hospital_id)})
    return {"message": "Hospital deleted"}