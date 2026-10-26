"""
Importación de conocimiento médico desde archivos externos (Excel / CSV / JSON).

Permite alimentar la base de conocimiento de MIMETIC de forma manual y masiva
desde hojas de cálculo u otros archivos, sin tocar código.

Formatos soportados:
  1. JSON estructurado (igual que el del seed / el generado por ai_generate_knowledge.py)
        {"symptoms": [...], "diseases": [...], "treatments": [...]}
     o un JSON de una sola colección:
        [ {...}, {...} ]  (se inserta en la colección indicada con --collection)

  2. CSV / Excel con columnas:
        enfermedad, descripcion, severidad, sintomas (separados por | o ,),
        medicamentos (JSON opcional), general_recommendations, source
     Los síntomas se registran/actualizan automáticamente como catálogo.

Uso:
    python import_from_excel.py --file datos.xlsx --type excel
    python import_from_excel.py --file datos.csv --type csv
    python import_from_excel.py --file knowledge.json --type json
    python import_from_excel.py --file diseases.json --type json --collection diseases
    python import_from_excel.py --file lista.json --type json --collection treatments --key disease_name

Requisitos opcionales para Excel: pip install pandas openpyxl
"""
import argparse
import asyncio
import csv
import json
import os
import sys

from dotenv import load_dotenv

from app.utils import normalize_text

load_dotenv()

VALID_COLLECTIONS = ("symptoms", "diseases", "treatments")


def _load_db():
    from motor.motor_asyncio import AsyncIOMotorClient
    from app.config import MONGODB_URL, MONGODB_DB_NAME
    client = AsyncIOMotorClient(MONGODB_URL)
    return client, client[MONGODB_DB_NAME]


async def _upsert(coll, docs, key_field):
    inserted = updated = 0
    errors = []
    for i, doc in enumerate(docs):
        key = doc.get(key_field)
        if not key:
            errors.append({"index": i, "reason": "missing key field"})
            continue
        patch = {k: v for k, v in doc.items() if k != "_id"}
        res = await coll.update_one({key_field: key}, {"$set": patch}, upsert=True)
        if res.upserted_id is not None:
            inserted += 1
        else:
            updated += 1
    return inserted, updated, errors


def _split_symptoms(raw) -> list[str]:
    """Divide síntomas y los normaliza/deduplica (p. ej. "Fiebre, fiebre" -> ["fiebre"])."""
    if isinstance(raw, list):
        parts = [str(s) for s in raw if str(s).strip()]
    else:
        parts = [p for p in str(raw).split("|") if p.strip()]
    seen = set()
    normalized = []
    for p in parts:
        n = normalize_text(p)
        if n and n not in seen:
            seen.add(n)
            normalized.append(n)
    return normalized


def _rows_from_excel(path):
    try:
        import pandas as pd
    except ImportError:
        sys.exit("Falta pandas/openpyxl: pip install pandas openpyxl")
    df = pd.read_excel(path, dtype=str).fillna("")
    return df.to_dict("records")


def _rows_from_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


async def _validate_symptoms_catalog(db, symptoms: list[str]):
    """Registra síntomas faltantes en el catálogo de forma idempotente.

    Guarda siempre el nombre normalizado (sin acentos) y tolera la existencia
    previa de duplicados con acento ("Vómito" vs "vomito") mediante el manejo
    de DuplicateKeyError bajo el índice único de ``name``.
    """
    from pymongo.errors import DuplicateKeyError

    added = 0
    for s in symptoms:
        name = normalize_text(s)
        if not name:
            continue
        doc = {"name": name, "description": "", "category": "generales"}
        try:
            res = await db.symptoms.update_one({"name": name}, {"$set": doc}, upsert=True)
        except DuplicateKeyError:
            res = None
        if res is not None and res.upserted_id is not None:
            added += 1
    return added


async def import_diseases_tabular(rows, to_db=True):
    """Convierte filas tabulares en diseases+treatments y los sincroniza."""
    client, db = _load_db()
    try:
        d_inserted = d_updated = 0
        t_inserted = t_updated = 0
        sym_added = 0
        for row in rows:
            name = normalize_text(row.get("enfermedad") or "")
            if not name:
                continue
            symptoms = _split_symptoms(row.get("sintomas", ""))
            sym_added += await _validate_symptoms_catalog(db, symptoms)
            disease = {
                "name": name,
                "description": (row.get("descripcion") or "").strip(),
                "symptoms": symptoms,
                "severity": (row.get("severidad") or "moderate").strip(),
            }
            res = await db.diseases.update_one({"name": name}, {"$set": disease}, upsert=True)
            d_inserted += 1 if res.upserted_id is not None else 0
            d_updated += 0 if res.upserted_id is not None else 1

            tname = name
            existing_t = await db.treatments.find_one({"disease_name": tname})
            if existing_t:
                t_inserted += 0
                t_updated += 1
                continue
            treatment = {
                "disease_name": tname,
                "medicines": [],
                "alternative_medicines": [],
                "non_pharmacological_treatments": [],
                "general_recommendations": (row.get("general_recommendations") or "").strip(),
                "source": "Importado desde archivo",
            }
            await db.treatments.insert_one(treatment)
            t_inserted += 1

        if to_db:
            print(f"[DB] diseases: {d_inserted} insertadas, {d_updated} actualizadas")
            print(f"[DB] treatments: {t_inserted} insertados, {t_updated} existentes (sin sobrescribir)")
            print(f"[DB] síntomas agregados al catálogo: {sym_added}")
        else:
            print(f"Simulación: {d_inserted} diseases nuevas, {sym_added} síntomas nuevos")
    finally:
        client.close()


async def import_json_collection(collection, docs, key_field, to_db=True):
    client, db = _load_db()
    try:
        coll = db[collection]
        inserted, updated, errors = _upsert(coll, docs, key_field)
        print(f"[DB] {collection}: {inserted} insertados, {updated} actualizados, {len(errors)} errores")
        for e in errors:
            print("   error:", e)
    finally:
        client.close()


async def import_json_full(data, to_db=True):
    client, db = _load_db()
    try:
        for coll, docs, key in (
            ("symptoms", data.get("symptoms", []), "name"),
            ("diseases", data.get("diseases", []), "name"),
            ("treatments", data.get("treatments", []), "disease_name"),
        ):
            if docs:
                inserted, updated, errors = _upsert(db[coll], docs, key)
                print(f"[DB] {coll}: {inserted} insertados, {updated} actualizados, {len(errors)} errores")
    finally:
        client.close()


def main():
    parser = argparse.ArgumentParser(description="Importar conocimiento desde Excel/CSV/JSON")
    parser.add_argument("--file", required=True, help="Ruta al archivo")
    parser.add_argument("--type", required=True, choices=["excel", "csv", "json"], help="Tipo de archivo")
    parser.add_argument("--collection", choices=VALID_COLLECTIONS, help="Colección destino (solo para JSON de una colección)")
    parser.add_argument("--key", default=None, help="Campo clave para upsert en JSON de colección única")
    parser.add_argument("--dry-run", action="store_true", help="Solo simular, no escribir en la base")
    args = parser.parse_args()

    path = args.file
    if not os.path.exists(path):
        sys.exit(f"No existe el archivo: {path}")

    to_db = not args.dry_run

    if args.type == "excel":
        rows = _rows_from_excel(path)
        asyncio.run(import_diseases_tabular(rows, to_db))

    elif args.type == "csv":
        rows = _rows_from_csv(path)
        asyncio.run(import_diseases_tabular(rows, to_db))

    else:  # json
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            if not args.collection:
                sys.exit("Para JSON de colección única indica --collection y --key")
            key = args.key or ("name" if args.collection != "treatments" else "disease_name")
            asyncio.run(import_json_collection(args.collection, data, key, to_db))
        elif isinstance(data, dict):
            asyncio.run(import_json_full(data, to_db))
        else:
            sys.exit("JSON no reconocido")

    print("Importación finalizada.")


if __name__ == "__main__":
    main()
