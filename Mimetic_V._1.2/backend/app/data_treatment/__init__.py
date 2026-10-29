"""Motor de limpieza y mapeo de datos para el entrenamiento del sistema experto.

Este paquete agrupa los servicios de la "Fase 2" del plan de desarrollo de
MIMETIC: leer un archivo externo (CSV / Excel / JSON), limpiar los valores
nulos o corruptos y mapear la información a la estructura exacta que usa la
base de datos MongoDB (colecciones ``symptoms``, ``diseases`` y ``treatments``).

Diseño
------
- ``cleaner`` : normaliza valores escalares y listas (nulos, espacios,
  duplicados, tipos).
- ``mapper``  : convierte filas tabulares genéricas en documentos con el
  esquema de la BD.
- ``pipeline``: orquesta el flujo completo lectura -> limpieza -> mapeo
  -> validación, devolviendo también un reporte para previsualización.

El paquete depende únicamente de la librería estándar de Python, por lo que
puede ejecutarse de forma aislada (utilidades, tests e importación batch) sin
necesidad de conectar a MongoDB.
"""

from app.data_treatment.cleaner import (
    clean_text,
    clean_list,
    is_blank,
    normalize_boolean,
    normalize_number,
    normalize_severity,
    strip_cell,
)
from app.data_treatment.mapper import (
    map_symptom,
    map_disease,
    map_treatment,
    map_tabular_rows,
    map_column_aliases,
)
from app.data_treatment.pipeline import (
    DataTreatmentResult,
    RawRow,
    process_rows,
    process_json,
    process_payload,
)

__all__ = [
    # cleaner
    "clean_text",
    "clean_list",
    "is_blank",
    "normalize_boolean",
    "normalize_number",
    "normalize_severity",
    "strip_cell",
    # mapper
    "map_symptom",
    "map_disease",
    "map_treatment",
    "map_tabular_rows",
    "map_column_aliases",
    # pipeline
    "DataTreatmentResult",
    "RawRow",
    "process_rows",
    "process_json",
    "process_payload",
]
