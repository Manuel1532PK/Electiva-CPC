"""
MIMETIC - Script de gestión desde terminal.

Uso:
  python manage.py create-hospital --name "Hospital San Juan" --code HSJ-001 [--email admin@hsj.com]
  python manage.py create-user --hospital HSJ-001 --email dr@hsj.com --role medico --name "Dr. García"
  python manage.py list-hospitals
  python manage.py list-users [--hospital HSJ-001]
  python manage.py reset-password --email user@hsj.com --new-password "nueva123"
  python manage.py deactivate-user --email user@hsj.com

Solo debe ser ejecutado por ingenieros de sistemas de MIMETIC con acceso al servidor.
"""

import argparse
import asyncio
import getpass
import sys
from datetime import datetime
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from bson import ObjectId

load_dotenv()

import os

MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGODB_DB_NAME", "mimetic_ai")

VALID_ROLES = ("super_admin", "admin", "medico", "paciente")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_collection(client, name):
    return client[DB_NAME][name]


async def find_hospital(db, code: str):
    return await db.hospitals.find_one({"code": code.strip().upper()})


async def cmd_create_hospital(args):
    client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=30000)
    db = client[DB_NAME]
    code = args.code.strip().upper()

    existing = await db.hospitals.find_one({"code": code})
    if existing:
        print(f"[ERROR] Ya existe un hospital con código '{code}'")
        client.close()
        return 1

    doc = {
        "name": args.name.strip(),
        "code": code,
        "address": args.address or "",
        "phone": args.phone or "",
        "email": args.email or "",
        "active": True,
        "created_at": datetime.utcnow(),
    }
    result = await db.hospitals.insert_one(doc)

    print(f"[OK] Hospital creado: {doc['name']} (código {code}, id {result.inserted_id})")

    if args.admin_email:
        admin_pass = args.admin_password or getpass.getpass(f"Contraseña para admin '{args.admin_email}': ")
        if not admin_pass:
            print("[ERROR] Contraseña vacía. No se creó el admin.")
            client.close()
            return 1
        await db.users.insert_one({
            "email": args.admin_email.strip().lower(),
            "name": args.admin_name or "Administrador",
            "password_hash": pwd_context.hash(admin_pass),
            "role": "admin",
            "hospital_id": str(result.inserted_id),
            "verified": True,
            "created_at": datetime.utcnow(),
        })
        print(f"[OK] Admin creado para {doc['name']}: {args.admin_email}")

    client.close()
    return 0


async def cmd_create_user(args):
    client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=30000)
    db = client[DB_NAME]

    if args.role not in VALID_ROLES:
        print(f"[ERROR] Rol inválido. Use: {', '.join(VALID_ROLES)}")
        client.close()
        return 1

    if args.role != "super_admin":
        hospital = await find_hospital(db, args.hospital)
        if not hospital:
            print(f"[ERROR] Hospital '{args.hospital}' no encontrado")
            client.close()
            return 1
        hospital_id = str(hospital["_id"])
    else:
        hospital_id = ""

    email = args.email.strip().lower()
    existing = await db.users.find_one({"email": email})
    if existing:
        print(f"[ERROR] Ya existe un usuario con email '{email}'")
        client.close()
        return 1

    password = args.password or getpass.getpass(f"Contraseña para '{email}': ")
    if len(password) < 6:
        print("[ERROR] La contraseña debe tener al menos 6 caracteres")
        client.close()
        return 1

    doc = {
        "email": email,
        "name": args.name,
        "password_hash": pwd_context.hash(password),
        "role": args.role,
        "hospital_id": hospital_id,
        "verified": True,
        "created_at": datetime.utcnow(),
    }
    result = await db.users.insert_one(doc)

    location = f"hospital '{args.hospital}'" if args.role != "super_admin" else "sistema (super admin)"
    print(f"[OK] Usuario creado: {email} con rol '{args.role}' en {location} (id {result.inserted_id})")

    client.close()
    return 0


async def cmd_list_hospitals(args):
    client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=30000)
    db = client[DB_NAME]

    cursor = db.hospitals.find({}).sort("name", 1)
    hospitals = await cursor.to_list(length=1000)

    if not hospitals:
        print("No hay hospitales registrados.")
    for h in hospitals:
        users_in = await db.users.count_documents({"hospital_id": str(h["_id"])})
        status = "activo" if h.get("active", True) else "inactivo"
        print(f"  {h['code']:<12} {h['name']:<35} usuarios: {users_in:<4} estado: {status}")

    client.close()
    return 0


async def cmd_list_users(args):
    client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=30000)
    db = client[DB_NAME]

    query = {}
    if args.hospital:
        hospital = await find_hospital(db, args.hospital)
        if not hospital:
            print(f"[ERROR] Hospital '{args.hospital}' no encontrado")
            client.close()
            return 1
        query["hospital_id"] = str(hospital["_id"])
    if args.role:
        query["role"] = args.role

    cursor = db.users.find(query).sort("created_at", -1)
    users = await cursor.to_list(length=1000)

    if not users:
        print("No se encontraron usuarios.")
    for u in users:
        print(f"  {u.get('email',''):<40} {u.get('name',''):<30} rol: {u.get('role',''):<12} verified: {u.get('verified','')}")

    client.close()
    return 0


async def cmd_reset_password(args):
    client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=30000)
    db = client[DB_NAME]
    email = args.email.strip().lower()

    user = await db.users.find_one({"email": email})
    if not user:
        print(f"[ERROR] Usuario '{email}' no encontrado")
        client.close()
        return 1

    password = args.new_password or getpass.getpass(f"Nueva contraseña para '{email}': ")
    if len(password) < 6:
        print("[ERROR] La contraseña debe tener al menos 6 caracteres")
        client.close()
        return 1

    await db.users.update_one({"email": email}, {"$set": {"password_hash": pwd_context.hash(password)}})
    print(f"[OK] Contraseña actualizada para {email}")
    client.close()
    return 0


async def cmd_deactivate_user(args):
    client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=30000)
    db = client[DB_NAME]
    email = args.email.strip().lower()

    user = await db.users.find_one({"email": email})
    if not user:
        print(f"[ERROR] Usuario '{email}' no encontrado")
        client.close()
        return 1

    await db.users.update_one({"email": email}, {"$set": {"active": False}})
    print(f"[OK] Usuario '{email}' desactivado")
    client.close()
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="manage.py",
        description="Gestión de hospitales y usuarios de MIMETIC (solo ingenieros de sistemas)",
    )
    sub = parser.add_subparsers(dest="command")

    p_hosp = sub.add_parser("create-hospital", help="Crear un hospital (y opcionalmente su admin)")
    p_hosp.add_argument("--name", required=True)
    p_hosp.add_argument("--code", required=True)
    p_hosp.add_argument("--address", default="")
    p_hosp.add_argument("--phone", default="")
    p_hosp.add_argument("--email", default="")
    p_hosp.add_argument("--admin-email", default="")
    p_hosp.add_argument("--admin-name", default="Administrador")
    p_hosp.add_argument("--admin-password", default="")
    p_hosp.set_defaults(func=cmd_create_hospital)

    p_user = sub.add_parser("create-user", help="Crear un usuario con rol específico")
    p_user.add_argument("--email", required=True)
    p_user.add_argument("--name", required=True)
    p_user.add_argument("--role", required=True, choices=VALID_ROLES)
    p_user.add_argument("--hospital", default="", help="Código del hospital (obligatorio si rol != super_admin)")
    p_user.add_argument("--password", default="", help="Si se omite, se pide de forma segura")
    p_user.set_defaults(func=cmd_create_user)

    p_lh = sub.add_parser("list-hospitals", help="Listar hospitales")
    p_lh.set_defaults(func=cmd_list_hospitals)

    p_lu = sub.add_parser("list-users", help="Listar usuarios (opcionalmente filtrados)")
    p_lu.add_argument("--hospital", default="")
    p_lu.add_argument("--role", default="")
    p_lu.set_defaults(func=cmd_list_users)

    p_rp = sub.add_parser("reset-password", help="Restablecer contraseña de un usuario")
    p_rp.add_argument("--email", required=True)
    p_rp.add_argument("--new-password", default="")
    p_rp.set_defaults(func=cmd_reset_password)

    p_da = sub.add_parser("deactivate-user", help="Desactivar un usuario")
    p_da.add_argument("--email", required=True)
    p_da.set_defaults(func=cmd_deactivate_user)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 1

    try:
        return asyncio.run(args.func(args))
    except KeyboardInterrupt:
        print("\nCancelado.")
        return 130
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())