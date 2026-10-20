"""Entidad Ciudad (fila de la tabla ciudad)."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Ciudad:
    id_ciudad: Optional[int]   # None mientras la ciudad no se ha guardado
    nombre: str
    departamento: str