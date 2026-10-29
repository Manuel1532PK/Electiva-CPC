"""
Gestión de usuarios, roles y cuentas de administrador desde la terminal.

Permite crear administradores y gestionar roles sin pasar por el frontend.

Uso:
    python manage_admin.py create-admin --email admin@example.com --name "Admin" --password "cambiar123"
    python manage_admin.py list
    python manage_admin.py set-role --email medico@example.com --role medico
    python manage_admin.py set-verified --email user@example.com --verified 1
    python manage_admin.py reset-password --email user@example.com --password nueva123
    python manage_admin.py delete --email user@example.com --confirm SI

Roles válidos: admin, medico, paciente
"""
import argparse
import asyncio
import getpass
import sys

from dotenv import load_dotenv

load_dotenv()

VALID_ROLES = ("admin", "medico", "paciente")


def _load_db():
    from motor.motor_asyncio import AsyncIOMotorClient
    from app.config import MONGODB_URL, MONGODB_DB_NAME
    client = AsyncIOMotorClient(MONGODB_URL)
    return client, client[MONGODB_DB_NAME]


def _pwd_context():
    from passlib.context import CryptContext
    return CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_admin(email, name, password, role="admin"):
    if password is None:
        password = getpass.getpass("Contraseña para el usuario: ")
        verify = getpass.getpass("Repite la contraseña: ")
        if password != verify:
            sys.exit("Las contraseñas no coinciden")
    client, db = _load_db()
    try:
        existing = await db.users.find_one({"email": email})
        if existing:
            sys.exit(f"Ya existe un usuario con email {email}")
        pwd = _pwd_context().hash(password)
        await db.users.insert_one({
            "email": email,
            "name": name,
            "password_hash": pwd,
            "role": role,
            "verified": True,
            "created_at": __import__("datetime").datetime.utcnow(),
        })
        print(f"[OK] Usuario {role} creado: {email}")
    finally:
        client.close()


async def set_role(email, role):
    client, db = _load_db()
    try:
        res = await db.users.update_one({"email": email}, {"$set": {"role": role}})
        if res.matched_count == 0:
            sys.exit(f"No se encontró el usuario {email}")
        print(f"[OK] Rol de {email} actualizado a '{role}'")
    finally:
        client.close()


async def set_verified(email, verified):
    client, db = _load_db()
    try:
        res = await db.users.update_one({"email": email}, {"$set": {"verified": bool(verified)}})
        if res.matched_count == 0:
            sys.exit(f"No se encontró el usuario {email}")
        print(f"[OK] verified={bool(verified)} para {email}")
    finally:
        client.close()


async def reset_password(email, password):
    client, db = _load_db()
    try:
        hash_ = _pwd_context().hash(password)
        res = await db.users.update_one({"email": email}, {"$set": {"password_hash": hash_}})
        if res.matched_count == 0:
            sys.exit(f"No se encontró el usuario {email}")
        print(f"[OK] Contraseña de {email} restablecida")
    finally:
        client.close()


async def delete_user(email, confirm):
    if confirm != "SI":
        sys.exit("Debes indicar --confirm SI para eliminar")
    client, db = _load_db()
    try:
        res = await db.users.delete_one({"email": email})
        if res.deleted_count == 0:
            sys.exit(f"No se encontró el usuario {email}")
        print(f"[OK] Usuario eliminado: {email}")
    finally:
        client.close()


async def list_users():
    client, db = _load_db()
    try:
        users = await db.users.find(
            {},
            {"email": 1, "name": 1, "role": 1, "verified": 1, "created_at": 1},
        ).sort("role", 1).to_list(length=1000)
        if not users:
            print("No hay usuarios.")
            return
        print(f"{'EMAIL':<40} {'NOMBRE':<20} {'ROL':<9} VERIF")
        for u in users:
            print(f"{u.get('email',''):<40} {str(u.get('name',''))[:20]:<20} {u.get('role',''):<9} {u.get('verified',False)}")
    finally:
        client.close()


def main():
    parser = argparse.ArgumentParser(description="Gestión de usuarios/roles/admin desde terminal")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("create-admin", help="Crear un usuario administrador")
    p.add_argument("--email", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--password", default=None, help="Omitir para pedirla interactivamente")
    p.add_argument("--role", default="admin", choices=VALID_ROLES)

    p = sub.add_parser("list", help="Listar usuarios")
    p.set_defaults(func=list_users)

    p = sub.add_parser("set-role", help="Cambiar rol de un usuario")
    p.add_argument("--email", required=True)
    p.add_argument("--role", required=True, choices=VALID_ROLES)
    p.set_defaults(func=lambda a: set_role(a.email, a.role))

    p = sub.add_parser("set-verified", help="Marcar/desmarcar email verificado")
    p.add_argument("--email", required=True)
    p.add_argument("--verified", required=True, type=int, choices=[0, 1])
    p.set_defaults(func=lambda a: set_verified(a.email, a.verified))

    p = sub.add_parser("reset-password", help="Restablecer contraseña")
    p.add_argument("--email", required=True)
    p.add_argument("--password", required=True)
    p.set_defaults(func=lambda a: reset_password(a.email, a.password))

    p = sub.add_parser("delete", help="Eliminar un usuario")
    p.add_argument("--email", required=True)
    p.add_argument("--confirm", required=True, help="Debe ser 'SI'")
    p.set_defaults(func=lambda a: delete_user(a.email, a.confirm))

    args = parser.parse_args()

    if args.command == "create-admin":
        asyncio.run(create_admin(args.email, args.name, args.password, args.role))
    elif args.command == "list":
        asyncio.run(list_users())
    elif args.command == "set-role":
        asyncio.run(set_role(args.email, args.role))
    elif args.command == "set-verified":
        asyncio.run(set_verified(args.email, args.verified))
    elif args.command == "reset-password":
        asyncio.run(reset_password(args.email, args.password))
    elif args.command == "delete":
        asyncio.run(delete_user(args.email, args.confirm))


if __name__ == "__main__":
    main()
