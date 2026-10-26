"""Reporte listo para convertirse en PDF: título, filtros aplicados y tabla de datos."""
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple


@dataclass
class Reporte:
    clave: str                                  # identifica el reporte; va en el nombre del archivo
    titulo: str
    filtros: List[Tuple[str, str]]              # [(etiqueta, valor)] elegidos por el usuario
    columnas: List[str]
    filas: List[Sequence]                       # un valor por columna; None se muestra como «—»
    anchos: Optional[List[float]] = None        # peso relativo de cada columna (None = iguales)
    a_la_derecha: Tuple[int, ...] = ()          # índices de las columnas alineadas a la derecha
