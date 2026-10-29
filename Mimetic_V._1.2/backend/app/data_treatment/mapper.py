"""Servicio de mapeo de columnas a la estructura de MongoDB (``mapper``).

Responsabilidad de la Fase 2: convertir filas tabulares genéricas (que llegan
de un CSV o Excel con nombres de columnas flexibles) en documentos que encajan
exactamente con el esquema usado por la base de datos MIMETIC.

Esquema de destino (coincide con ``seed_data.py`` e ``import_from_excel.py``)
-----------------------------------------------------------------------------
Colección  Clave única      Campos
---------- ---------------- -------------------------------------------------
symptoms   name             name, description, category
diseases   name             name, description, severity, symptoms[]
treatments disease_name     disease_name, medicines[], alternative_medicines[],
                            non_pharmacological_treatments[],
                            general_recommendations, source

Además, se registran **aliases** de columnas para que un archivo con encabezados
en español o con nombres ligeramente distintos siga funcionando automáticamente
(p. ej. ``enfermedad``/``nombre``/``disease`` -> campo ``name``).
"""

from app.data_treatment.cleaner import (
    clean_text,
    clean_list,
    normalize_severity,
    strip_cell,
)

# ---------------------------------------------------------------------------
# Aliases de columnas (mayúsculas + sin acentos, ver _alias_key)
# ---------------------------------------------------------------------------

_COLUMN_ALIASES = {
    # disease name
    "enfermedad": "name",
    "nombre": "name",
    "disease": "name",
    "nombre de la enfermedad": "name",
    # description
    "descripcion": "description",
    "descripcion general": "description",
    "informacion": "description",
    # severity
    "severidad": "severity",
    "gravedad": "severity",
    "nivel": "severity",
    # symptoms list
    "sintomas": "symptoms",
    "sintoma": "symptoms",
    "signos": "symptoms",
    "signos y sintomas": "symptoms",
    "symptoms": "symptoms",
    # treatments / medicines
    "medicamentos": "medicines",
    "medicamento": "medicines",
    "farmacos": "medicines",
    "tratamiento": "medicines",
    # general recommendations
    "recomendaciones": "general_recommendations",
    "recomendaciones generales": "general_recommendations",
    "instructions": "general_recommendations",
    # source
    "fuente": "source",
    "origen": "source",
    "referencia": "source",
    # symptom-only columns
    "nombre del sintoma": "symptom_name",
    "sintoma nombre": "symptom_name",
    "categoria": "category",
    "categoria del sintoma": "category",
}


def _alias_key(header: str) -> str:
    """Clave canónica de un encabezado: mayúsculas y sin acentos/espacios.

    Ejemplo: "Nombre de la Enfermedad" -> "NOMBREDELAENFERMEDAD".
    """
    import unicodedata

    nfkd = unicodedata.normalize("NFKD", str(header))
    ascii_text = "".join(c for c in nfkd if not unicodedata.combining(c))
    return "".join(ascii_text.split()).upper()


# Invertir y precomputar el mapa de aliases con claves canónicas.
_ALIAS_MAP = {_alias_key(k): v for k, v in _COLUMN_ALIASES.items()}

# Claves canónicas que ya son campos del esquema de destino (no son "alias"
# pero deben conservarse cuando el archivo/JSON ya viene con el formato final).
_SCHEMA_DIRECT_KEYS = {
    _alias_key(k)
    for k in (
        "name",
        "description",
        "severity",
        "symptoms",
        "category",
        "disease_name",
        "medicines",
        "alternative_medicines",
        "non_pharmacological_treatments",
        "general_recommendations",
        "source",
        "symptom_name",
    )
}


def map_column_aliases(headers: list) -> dict[str, str]:
    """Resuelve el mapeo de nombres de columna crudos -> campos del esquema.

    Parámetros
    ----------
    headers:
        Lista de encabezados del archivo (los nombres de las columnas).

    Devuelve un diccionario ``{ nombre_columna_original: campo_destino }``.
    Las columnas sobre las que no hay un alias mapeado y que no sean ya un
    campo del esquema se omiten.

    Ejemplo::

        map_column_aliases(["Enfermedad", "Sintomas", "Severidad"])
        # -> {"Enfermedad": "name", "Sintomas": "symptoms", "Severidad": "severity"}
    """
    mapping: dict[str, str] = {}
    for header in headers:
        key = _alias_key(header)
        target = _ALIAS_MAP.get(key)
        if target:
            mapping[str(header)] = target
        elif key in _SCHEMA_DIRECT_KEYS:
            # Conservar la columna tal cual (ya es un campo válido del esquema).
            mapping[str(header)] = str(header)
    return mapping


# ---------------------------------------------------------------------------
# Mapeo de documentos individuales
# ---------------------------------------------------------------------------


def map_symptom(row: dict) -> dict:
    """Convierte una fila/objeto en un documento de la colección ``symptoms``.

    Espera (con alias o directo) las claves ``symptom_name``/``name``,
    ``description`` y ``category``.

    Devuelve un dict con el esquema: ``{name, description, category}``.
    """
    raw_name = row.get("symptom_name") or row.get("name")
    name = clean_text(raw_name)
    description = clean_text(row.get("description"))
    category = clean_text(row.get("category") or "generales")
    return {
        "name": name,
        "description": description,
        "category": category,
    }


def map_disease(row: dict) -> dict:
    """Convierte una fila/objeto en un documento de la colección ``diseases``.

    Espera (con alias o directo) ``name``, ``description``, ``severity`` y
    ``symptoms`` (cadena separada o lista).

    Devuelve un dict con el esquema::

        {name, description, severity, symptoms: [...]}
    """
    name = clean_text(row.get("name"))
    description = clean_text(row.get("description"))
    severity = normalize_severity(row.get("severity"))
    symptoms = clean_list(row.get("symptoms"))
    return {
        "name": name,
        "description": description,
        "severity": severity,
        "symptoms": symptoms,
    }


def map_treatment(row: dict) -> dict:
    """Convierte una fila/objeto en un documento de la colección ``treatments``.

    Espera (con alias o directo) ``disease_name``, ``medicines``,
    ``alternative_medicines``, ``non_pharmacological_treatments``,
    ``general_recommendations`` y ``source``.

    Devuelve un dict con el esquema completo de la colección.
    """
    disease_name = clean_text(row.get("disease_name") or row.get("name"))
    medicines = clean_list(row.get("medicines"))
    alternatives = clean_list(row.get("alternative_medicines"))
    non_pharma = clean_list(row.get("non_pharmacological_treatments"))
    general = clean_text(row.get("general_recommendations"))
    source = clean_text(row.get("source") or "Importado desde archivo")

    # Los medicamentos en tabla plana pueden venir como texto libre; el motor
    # de tratamientos espera una lista de dicts. Convertimos cada ítem en un
    # dict con la forma mínima que espera ``app/expert_system/engine.py``.
    medicines_normalized = [{"name": m} for m in medicines]

    return {
        "disease_name": disease_name,
        "medicines": medicines_normalized,
        "alternative_medicines": alternatives,
        "non_pharmacological_treatments": non_pharma,
        "general_recommendations": general,
        "source": source,
    }


# ---------------------------------------------------------------------------
# Mapeo batch de filas tabulares
# ---------------------------------------------------------------------------


def map_tabular_rows(rows: list[dict], target: str) -> list[dict]:
    """Mapea una lista de filas tabulares a documentos de una colección.

    Parámetros
    ----------
    rows:
        Lista de diccionarios, una por fila del archivo. Se resuelven aliases
        de columna automáticamente (ver :func:`map_column_aliases`).
    target:
        Colección destino: ``"symptoms"``, ``"diseases"`` o ``"treatments"``.

    Devuelve una lista de documentos normalizados. Las filas sin un valor clave
    (p. ej. enfermedad sin nombre) se descartan y no se incluyen.
    """
    out: list[dict] = []
    if not rows:
        return out

    # Resolver aliases una sola vez a partir del primer diccionario
    # (asumimos que todas las filas usan los mismos encabezados).
    sample_headers = list(rows[0].keys())
    alias_map = map_column_aliases(sample_headers)

    for row in rows:
        # Normalizar la fila: renombrar columnas según alias y quedarnos
        # solo con las que son relevantes para la colección destino.
        normalized: dict = {}
        for original, field in alias_map.items():
            normalized[field] = row.get(original)

        if target == "symptoms":
            doc = map_symptom(normalized)
            if not doc["name"]:
                continue
        elif target == "diseases":
            doc = map_disease(normalized)
            if not doc["name"]:
                continue
        elif target == "treatments":
            doc = map_treatment(normalized)
            if not doc["disease_name"]:
                continue
        else:
            raise ValueError(f"Colección destino no soportada: {target}")

        out.append(doc)

    return out
