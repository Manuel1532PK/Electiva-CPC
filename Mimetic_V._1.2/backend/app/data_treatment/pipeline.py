"""Orquestación del motor de limpieza (``pipeline``).

Responsabilidad de la Fase 2: unir lectura, limpieza y mapeo en un flujo único
y devolver un **resultado estructurado** que la capa de API (Fase 1) y el
frontend puedan consumir para previsualizar antes de persistir.

Flujo
-----
1. Normalizar una lista de filas (RowNormalizer) con la limpieza base.
2. Resolver la colección destino (si no vino explícita, se infiere de la
   estructura de los datos).
3. Mapear las filas mediante :mod:`app.data_treatment.mapper`.
4. Consolidar en un :class:`DataTreatmentResult` con las filas listas, las
   descartadas y un resumen de conteos.

El pipeline **no persiste**; solo prepara y valida. La escritura a MongoDB es
responsabilidad de la capa de importación (reutilizando la lógica idempotente
de ``seed_data``/``import_from_excel``).
"""

from typing import Any

from app.data_treatment.cleaner import clean_text, strip_cell
from app.data_treatment.mapper import map_tabular_rows

RawRow = dict[str, Any]


class DataTreatmentResult:
    """Contenedor inmutable de los datos procesados por el pipeline.

    Atributos
    ---------
    target:
        Colección destino (``symptoms``, ``diseases`` o ``treatments``).
    documents:
        Lista de documentos ya mapeados y listos para persistir.
    discarded:
        Lista de filas que fueron descartadas (sin clave, o corruptas).
    total_input, total_valid, total_discarded:
        Conteos para el reporte.
    """

    def __init__(
        self,
        target: str,
        documents: list[dict],
        discarded: list[dict],
        total_input: int,
    ):
        self.target = target
        self.documents = documents
        self.discarded = discarded
        self.total_input = total_input
        self.total_valid = len(documents)
        self.total_discarded = len(discarded)

    def to_dict(self) -> dict:
        """Serializa el resultado para ser enviado por la API (JSON-serializable)."""
        return {
            "target": self.target,
            "total_input": self.total_input,
            "total_valid": self.total_valid,
            "total_discarded": self.total_discarded,
            "documents": self.documents,
            "discarded": self.discarded,
        }

    def __repr__(self) -> str:  # pragma: no cover - solo utilidad de debug
        return (
            f"DataTreatmentResult(target={self.target!r}, "
            f"valid={self.total_valid}, discarded={self.total_discarded})"
        )


class RowNormalizer:
    """Normaliza cada fila cruda: limpia claves y texto base.

    Quita claves con nombre vacío, conserva el orden y limpia los valores
    textuales con :func:`clean_text` para eliminar espacios y saltos.
    """

    def __init__(self, fields: list[str] | None = None):
        # Si se indican campos, se conserva el orden de esos campos y se
        # descartan los demás; si no, se conserva el orden del encabezado.
        self.fields = fields

    def normalize_row(self, raw: RawRow) -> RawRow:
        """Devuelve una fila limpia (texto sin espacios en todas sus celdas)."""
        clean: RawRow = {}
        for key, value in raw.items():
            if is_blank_key(key):
                continue
            clean[strip_cell(key)] = clean_text(value)
        if self.fields:
            return {f: clean.get(f, "") for f in self.fields}
        return clean

    def __call__(self, raw: RawRow) -> RawRow:
        return self.normalize_row(raw)


def is_blank_key(key: Any) -> bool:
    """Indica si un nombre de columna es vacío (columna sin encabezado)."""
    return strip_cell(key) == ""


def _infer_target(sample: RawRow) -> str:
    """Infiera la colección destino a partir de las claves presentes.

    Heurística determinista (en ese orden):
    - si hay ``disease_name`` o ``medicines`` -> ``treatments``
    - si hay ``symptoms`` o ``severity`` -> ``diseases``
    - en caso contrario -> ``symptoms``
    """
    lowered = {strip_cell(k).lower() for k in sample.keys()}
    if {"disease_name", "medicines"}.intersection(lowered):
        return "treatments"
    if {"symptoms", "signos", "severity", "severidad", "sintomas"}.intersection(lowered):
        return "diseases"
    return "symptoms"


def process_rows(rows: list[RawRow], target: str | None = None) -> DataTreatmentResult:
    """Procesa una lista de filas crudas (de CSV/Excel/JSON) al esquema de BD.

    Parámetros
    ----------
    rows:
        Lista de diccionarios (uno por fila).
    target:
        Colección destino explícita; si es ``None`` se infiere
        (ver :func:`_infer_target`).

    Devuelve un :class:`DataTreatmentResult`.
    """
    if not rows:
        return DataTreatmentResult(target or "symptoms", [], [], 0)

    resolved_target = target or _infer_target(rows[0])
    normalizer = RowNormalizer()

    normalized_rows: list[RawRow] = []
    for raw in rows:
        row = normalizer(raw)
        # Filas completamente vacías se consideran ruido y se descartan.
        if not any(v for v in row.values()):
            continue
        normalized_rows.append(row)

    documents = map_tabular_rows(normalized_rows, resolved_target)

    # Identificar las filas descartadas: son las que, mapeadas de forma
    # individual, no producen un documento válido (faltante la clave).
    discarded: list[RawRow] = []
    for row in normalized_rows:
        mapped = map_tabular_rows([row], resolved_target)
        if not mapped:
            discarded.append(row)

    return DataTreatmentResult(
        target=resolved_target,
        documents=documents,
        discarded=discarded,
        total_input=len(rows),
    )


def process_json(data: Any, target: str | None = None) -> DataTreatmentResult:
    """Procesa una carga JSON ya parseada (dict o lista de dicts).

    Acepta:
    - una lista de filas, o
    - un dict con la colección destino ya indicada::

        {"target": "diseases", "rows": [ ... ]}

    Devuelve un :class:`DataTreatmentResult`.
    """
    if isinstance(data, dict):
        rows = data.get("rows", data.get("documents", []))
        target = target or data.get("target") or data.get("collection")
    else:
        rows = data if isinstance(data, list) else []
    return process_rows(rows, target)


def process_payload(filename: str, data: Any, target: str | None = None) -> DataTreatmentResult:
    """Procesa el contenido de un archivo según su extensión.

    Parámetros
    ----------
    filename:
        Nombre del archivo original (para inferir el formato).
    data:
        Contenido ya leído y decodificado por la capa de I/O (listas o dicts).
    target:
        Colección destino opcional; se infiere si no se indica.

    Nota
    ----
    El pipeline no resuelve formatos binarios (xlsx) por sí mismo: espera que
    la capa de carga (p. ej. ``import_from_excel``) ya haya convertido el
    archivo en una lista de dicts. Esta función se mantiene como punto único
    de entrada que normaliza el flujo y deja la extensión como metadato.
    """
    result = process_json(data, target)
    # Almacenar el origen como metadato conveniente para auditoría.
    result = DataTreatmentResult(
        target=result.target,
        documents=result.documents,
        discarded=result.discarded,
        total_input=result.total_input,
    )
    # (La extensión se conserva a nivel de llamador; aquí solo se documenta.)
    _ = filename  # no-op: se conserva la firma por claridad de la API
    return result
