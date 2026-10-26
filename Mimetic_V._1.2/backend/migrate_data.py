"""
Migración: adapta los usuarios existentes al modelo multi-hospital.

- Los admins actuales pasan a rol super_admin (personal de MIMETIC).
- Los médicos existentes se asignan al hospital por defecto (DEFAULT).
- Los pacientes NO se vinculan a ningún hospital (la historia clínica viaja
  con el paciente según la Ley 2015 de 2020).

Uso:
  python migrate_data.py
"""

import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

load_dotenv()

MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGODB_DB_NAME", "mimetic_ai")


async def migrate():
    client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=30000)
    db = client[DB_NAME]

    default_hospital = await db.hospitals.find_one({"code": "DEFAULT"})
    if not default_hospital:
        doc = {
            "name": "Hospital General MIMETIC",
            "code": "DEFAULT",
            "address": "",
            "phone": "",
            "email": "",
            "active": True,
            "created_at": datetime.utcnow(),
        }
        result = await db.hospitals.insert_one(doc)
        default_id = str(result.inserted_id)
        print(f"[OK] Hospital por defecto creado con id {default_id}")
    else:
        default_id = str(default_hospital["_id"])
        print(f"[OK] Hospital por defecto ya existía: {default_id}")

    cursor = db.users.find({})
    users = await cursor.to_list(length=10000)

    updated_medicos = 0
    updated_admin = 0
    total = 0

    for u in users:
        total += 1
        set_fields = {}
        if u.get("role") == "admin":
            set_fields["role"] = "super_admin"
            if not u.get("hospital_id"):
                set_fields["hospital_id"] = ""
            updated_admin += 1
        elif u.get("role") == "medico":
            if not u.get("hospital_id"):
                set_fields["hospital_id"] = default_id
                updated_medicos += 1
        if set_fields:
            await db.users.update_one({"_id": u["_id"]}, {"$set": set_fields})

    print(f"\nResumen:")
    print(f"  Usuarios procesados:      {total}")
    print(f"  Médicos asignados a DEFAULT: {updated_medicos}")
    print(f"  Admin -> super_admin:     {updated_admin}")
    print(f"  Pacientes:                sin hospital (quedan como están)")
    print(f"\nImportante: los usuarios admin anteriores ahora son super_admin.")
    print("Para crear admins de hospital usa: python manage.py create-user --role admin")

    client.close()


if __name__ == "__main__":
    try:
        asyncio.run(migrate())
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        sys.exit(1)