import unicodedata
from typing import Any


def normalize_text(text: Any) -> str:
    """Normalización estricta para claves de catálogo.

    Aplica lowercase, recorte de espacios y eliminación de diacríticos
    (tildes/acentos) para que "Vómito", "VOMITO" y "vomito" converjan a un
    único valor canónico ("vomito"). Se usa en inserción, importación y
    deduplicación de datos para evitar colisiones que inflan el catálogo.

    Devuelve siempre una cadena (los valores no textuales se convierten con str).
    """
    if text is None:
        return ""
    s = str(text).strip().lower()
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c))
