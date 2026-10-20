"""Entidad Categoria (fila de la tabla categoria)."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Categoria:
    id_categoria: Optional[int]   # None mientras la categoría no se ha guardado
    nombre: str
    descripcion: Optional[str]
    estado: bool = True           # True = activa, False = inactiva