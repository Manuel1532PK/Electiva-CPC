"""Servicio de limpieza de valores (``cleaner``).

Responsabilidad de la Fase 2: normalizar los valores crudos que provienen de
archivos externos (CSV / Excel / JSON) para que queden listos para persistir.

Las funciones de este módulo son **funciones puras**: no tocan base de datos,
no hacen I/O y siempre devuelven un valor normalizado. Esto las hace fáciles
de probar y reutilizar.

Reglas generales
----------------
- Un valor que es ``None``, cadena vacía o cadena de espacios se considera
  "en blanco" y se normaliza a ``""`` (string) o a ``[]`` (lista) según el uso.
- Se eliminan espacios al inicio/final (``strip``), se colapsan múltiples
  espacios internos y se normalizan acentos cuando contribuye a la consistencia
  (p. ej. comparaciones de nombres), pero se conserva la cadena original en los
  textos que van a la BD (descripciones, recomendaciones).
- Se colapsan valores duplicados que hayan quedado tras la limpieza.
"""

import unicodedata

# ---------------------------------------------------------------------------
# Utilidades básicas
# ---------------------------------------------------------------------------


def strip_cell(value) -> str:
    """Convierte un valor crudo en texto plano sin espacios sobrantes.

    - ``None`` -> ``""``
    - números (int/float) -> representación de texto
    - cadenas con espacios internos múltiples se colapsan a uno solo

    Ejemplos::

        strip_cell(None)      -> ""
        strip_cell("  hola ")  -> "hola"
        strip_cell("a   b")    -> "a b"
    """
    if value is None:
        return ""
    text = str(value).strip()
    return " ".join(text.split())


def is_blank(value) -> bool:
    """Indica si un valor debe considerarse vacío o corrupto.

    Considera en blanco: ``None``, cadenas de solo espacios, y cadenas cuyo
    texto normalizado sea vacío. Los números ``0`` no se consideran vacíos.
    """
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, tuple, dict, set)):
        return len(value) == 0
    return False


def _collapse_accents(text: str) -> str:
    """Normaliza acentos (NFD) y quita las marcas combinatorias.

    Sirve para comparaciones y claves de deduplicación sin perder el texto
    original. Ejemplo: "pérdida" -> "perdida" (solo para comparar).
    """
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _normalize_key(text: str) -> str:
    """Clave canónica de texto para deduplicar/mapear.

    Combina: minúsculas + colapso de acentos + espacio único. No elimina signos
    de puntuación para no romper nombres como "dolor de cabeza (cefalea)".
    """
    return _collapse_accents(text.lower())


# ---------------------------------------------------------------------------
# Limpieza de texto y listas
# ---------------------------------------------------------------------------


def clean_text(value, preserve_accents: bool = True) -> str:
    """Limpia un valor de texto destinado a la BD.

    Parámetros
    ----------
    value:
        Valor crudo (str, número o ``None``).
    preserve_accents:
        Si ``True`` mantiene los acentos originales (recomendado para datos
        mostrados al usuario). Si ``False``, devuelve texto sin acentos.

    Devuelve siempre un ``str`` (nunca ``None``).
    """
    text = strip_cell(value)
    if not text:
        return ""
    if preserve_accents:
        return text
    return _collapse_accents(text)


def clean_list(value, separators=("|", ",", ";"), lowercase: bool = False) -> list[str]:
    """Limpia y devuelve una lista de elementos no vacíos ni duplicados.

    Parámetros
    ----------
    value:
        Puede ser una lista/tupla real o una cadena con elementos separados
        (por ``|``, ``,`` o ``;``), como suele venir de un Excel/CSV.
    separators:
        Separadores aceptados al explotar una cadena.
    lowercase:
        Si ``True``, normaliza cada elemento a minúsculas y sin acentos.

    Ejemplos::

        clean_list(None)                 -> []
        clean_list("fiebre|tos, fiebre") -> ["fiebre", "tos"]
        clean_list([" a ", "b", "b"])    -> ["a", "b"]
    """
    if is_blank(value):
        return []

    # Pasar a lista real de elementos crudos
    if isinstance(value, str):
        raw_items = [value]
        for sep in separators:
            expanded = []
            for item in raw_items:
                expanded.extend(item.split(sep) if sep in item else [item])
            raw_items = expanded
    else:
        raw_items = list(value)

    cleaned: list[str] = []
    seen: set[str] = set()
    for item in raw_items:
        text = strip_cell(item)
        if not text:
            continue
        key = _normalize_key(text) if lowercase else text.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(text)
    return cleaned


def normalize_number(value, *, default: float | None = None) -> float | None:
    """Convierte un valor a número (``float``) o devuelve ``default``.

    Tolera decimales con coma o punto, quita la moneda ``$`` y los espacios.
    Ejemplos::

        normalize_number("  3.5 ")  -> 3.5
        normalize_number("3,5")     -> 3.5
        normalize_number("$10")     -> 10.0
        normalize_number("abc")     -> None
    """
    if is_blank(value):
        return default
    text = strip_cell(value).replace("$", "").replace(".", "", 0)
    # Reemplazar posible coma decimal por punto (solo la última coma)
    if "," in text and "." in text:
        text = text.replace(",", "")
    elif "," in text:
        text = text.replace(",", ".")
    text = text.replace(" ", "")
    try:
        return float(text)
    except (ValueError, TypeError):
        return default


def normalize_boolean(value) -> bool | None:
    """Interpreta un valor como booleano de forma tolerante.

    Devuelve ``True``/``False`` o ``None`` si el valor está en blanco o es
    desconocido. Acepta: ``1/0``, ``true/false``, ``si/no``, ``sí/n``, etc.
    """
    if is_blank(value):
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    key = _normalize_key(strip_cell(value))
    if key in {"true", "si", "sí", "yes", "y", "1", "active", "activo"}:
        return True
    if key in {"false", "no", "n", "0", "inactive", "inactivo"}:
        return False
    return None


# ---------------------------------------------------------------------------
# Normalización de dominios específicos del dominio médico MIMETIC
# ---------------------------------------------------------------------------

_SEVERITY_ALIASES = {
    "leve": "low",
    "baja": "low",
    "bajo": "low",
    "low": "low",
    "menor": "low",
    "moderado": "moderate",
    "moderada": "moderate",
    "media": "moderate",
    "moderate": "moderate",
    "medium": "moderate",
    "grave": "high",
    "gravedad": "high",
    "severo": "high",
    "severa": "high",
    "alta": "high",
    "alto": "high",
    "critico": "critical",
    "critica": "critical",
    "critical": "critical",
    "urgente": "critical",
    "emergencia": "critical",
}


def normalize_severity(value, default: str = "moderate") -> str:
    """Normaliza la severidad de una enfermedad a uno de los valores del motor.

    El motor de diagnóstico (``app/expert_system/engine.py``) usa por defecto
    ``"moderate"``, ``"low"``, ``"high"`` y ``"critical"``. Esta función
    traduce sinónimos en español/inglés a ese vocabulario canónico.

    Devuelve siempre un string válido dentro del dominio.
    """
    if is_blank(value):
        return default
    key = _normalize_key(strip_cell(value))
    return _SEVERITY_ALIASES.get(key, default)
