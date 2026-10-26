"""
Generación masiva de conocimiento médico con IA.

Usa un LLM (Google Gemini o OpenAI) para generar o enriquecer enfermedades,
síntomas y tratamientos en el formato JSON que usa MIMETIC, y los guarda en
MongoDB (idempotente) o en un archivo JSON de salida.

Uso:
    python ai_generate_knowledge.py --diseases "Dengue, Malaria, Fiebre Amarilla, Chikungunya"
    python ai_generate_knowledge.py --file lista_enfermedades.txt --to json --out salida.json
    python ai_generate_knowledge.py --help

Variables de entorno (.env):
    AI_PROVIDER          = gemini | openai   (default: gemini)
    GEMINI_API_KEY       = tu clave de Gemini
    OPENAI_API_KEY       = tu clave de OpenAI
    OPENAI_MODEL         = gpt-4o (default)
    TOGETHER_API_KEY     = opcional, si se usa una API compatible con OpenAI
    MONGODB_URL          = conexión MongoDB (usa app.config si no se define)
"""
import argparse
import asyncio
import json
import os
import re

from dotenv import load_dotenv

load_dotenv()


def _load_db():
    """Devuelve un cliente MongoDB listo (motor async)."""
    from motor.motor_asyncio import AsyncIOMotorClient
    from app.config import MONGODB_URL, MONGODB_DB_NAME
    client = AsyncIOMotorClient(MONGODB_URL)
    return client, client[MONGODB_DB_NAME]


def _read_llm(provider: str, prompt: str) -> str:
    """Llama al LLM y devuelve el texto de respuesta."""
    if provider == "openai":
        import httpx
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("TOGETHER_API_KEY")
        base = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        model = os.getenv("OPENAI_MODEL", "gpt-4o")
        if not api_key:
            raise SystemExit("Falta OPENAI_API_KEY (o TOGETHER_API_KEY) en .env")
        resp = httpx.post(
            f"{base}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "Eres un experto médico que genera contenido clínico en español. Responde solo con JSON válido."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.4,
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    # Gemini
    import httpx
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    if not api_key:
        raise SystemExit("Falta GEMINI_API_KEY en .env (o usa AI_PROVIDER=openai)")
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/{model}"
           f":generateContent?key={api_key}")
    resp = httpx.post(
        url,
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.4},
        },
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise SystemExit("Respuesta inesperada de Gemini: " + json.dumps(data, ensure_ascii=False)[:500])


def _extract_json(text: str):
    """Extrae un JSON de la respuesta (tolera bloques ```json```)."""
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        text = m.group(1)
    else:
        # primer objeto JSON
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start:end + 1]
    return json.loads(text)


def build_prompt(diseases: list[str]) -> str:
    ejemplo = {
        "name": "Influenza (Gripe)",
        "description": "Infección viral respiratoria aguda causada por el virus de la influenza",
        "symptoms": ["fiebre", "tos", "dolor de cabeza", "fatiga", "dolor de garganta"],
        "severity": "moderate",
    }
    return f"""
Genera una base de conocimiento médico para las siguientes enfermedades:
{diseases}

Devuelve SOLO un objeto JSON con tres claves: "symptoms", "diseases" y "treatments".

- "symptoms": lista de objetos {{"name", "description", "category"}}. Los nombres deben ser
  los mismos que se usan dentro de cada enfermedad (en minúsculas y canónicos).
  Categorías válidas: generales, respiratorio, neurologico, digestivo, cardiovascular,
  musculoesqueletico, dermatologico, oftalmologico, otologico, urinario, endocrino.

- "diseases": lista de objetos {{"name", "description", "symptoms" (lista de strings que
  deben existir en "symptoms"), "severity"}} donde severity ∈ mild|moderate|high|critical.

- "treatments": lista de objetos por enfermedad con el siguiente formato exacto:
  {{
    "disease_name": str,
    "medicines": [
      {{
        "name": str, "patient_summary": str, "dosage_mg_kg": str|null,
        "max_daily_dose": str, "frequency": str, "duration": str, "route": "Oral",
        "contraindications": {{"conditions": [], "allergies": [], "comorbidities": []}},
        "adjustments": {{"renal": str, "hepatic": str, "pediatric": str,
                          "geriatric": str, "pregnancy": str}},
        "interactions_warning": str, "monitoring": str, "dosage": str
      }}
    ],
    "alternative_medicines": [],
    "non_pharmacological_treatments": [],
    "general_recommendations": str,
    "source": "Generado con IA"
  }}

Ejemplo de disease:
{json.dumps(ejemplo, ensure_ascii=False)}

Toda la información debe estar en español y ser clínicamente coherente.
No inventes enfermedades fuera de la lista dada.
"""


def _disease_key_exists(db, names: list[str]) -> dict:
    """Devuelve {name(in minúsculas): _id} para las enfermedades ya existentes."""
    out = {}
    for name in names:
        doc = asyncio.get_event_loop().run_until_complete(
            db.diseases.find_one({"name": name}, {"_id": 1})
        )
        out[name] = str(doc["_id"]) if doc else None
    return out


async def generate(diseases: list[str], provider: str, to_db: bool, out_file: str | None):
    if not diseases:
        raise SystemExit("No se indicaron enfermedades.")
    prompt = build_prompt(diseases)
    print(f"[IA] Consultando LLM ({provider}) por {len(diseases)} enfermedades...")
    raw = _read_llm(provider, prompt)
    data = _extract_json(raw)

    symptoms = data.get("symptoms", [])
    diseases_data = data.get("diseases", [])
    treatments = data.get("treatments", [])

    if out_file:
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[OK] Guardado en {out_file}")

    if to_db:
        client, db = _load_db()
        try:
            for s in symptoms:
                await db.symptoms.update_one({"name": s["name"]}, {"$set": s}, upsert=True)
            print(f"[DB] Sincronizados {len(symptoms)} síntomas")
            for d in diseases_data:
                await db.diseases.update_one({"name": d["name"]}, {"$set": d}, upsert=True)
            print(f"[DB] Sincronizadas {len(diseases_data)} enfermedades")
            for t in treatments:
                await db.treatments.update_one(
                    {"disease_name": t["disease_name"]}, {"$set": t}, upsert=True
                )
            print(f"[DB] Sincronizados {len(treatments)} tratamientos")
        finally:
            client.close()
        print("[OK] Base actualizada")

    print(f"Resumen: {len(symptoms)} síntomas, {len(diseases_data)} enfermedades, {len(treatments)} tratamientos")


def main():
    parser = argparse.ArgumentParser(description="Generación masiva de conocimiento médico con IA")
    parser.add_argument("--diseases", help="Lista separada por comas de enfermedades")
    parser.add_argument("--file", help="Archivo de texto con una enfermedad por línea")
    parser.add_argument("--provider", choices=["gemini", "openai"], default=os.getenv("AI_PROVIDER", "gemini"))
    parser.add_argument("--to-json", dest="to_json", action="store_true", help="Guardar también como JSON")
    parser.add_argument("--out", default="ai_generated_knowledge.json", help="Archivo JSON de salida")
    parser.add_argument("--dry-run", action="store_true", help="No escribir en la base (solo generar/salvar)")
    args = parser.parse_args()

    diseases = []
    if args.diseases:
        diseases = [d.strip() for d in args.diseases.split(",") if d.strip()]
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            diseases += [line.strip() for line in f if line.strip()]
    diseases = list(dict.fromkeys(diseases))  # dedupe preservando orden

    if not diseases:
        parser.error("Debes indicar --diseases o --file")

    to_db = not args.dry_run
    if args.to_json:
        out_file = args.out
    else:
        out_file = args.out if args.dry_run else None

    asyncio.run(generate(diseases, args.provider, to_db, out_file))


if __name__ == "__main__":
    main()
