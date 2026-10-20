"""Entidad Producto (fila de la tabla producto)."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Producto:
    id_producto: Optional[int]    # None mientras el producto no se ha guardado
    codigo: str
    nombre: str
    id_categoria: int
    descripcion: Optional[str] = None
    unidad_medida: Optional[str] = None
    estado: bool = True           # True = activo, False = inactivo
    categoria: Optional[str] = None  # nombre de la categoría, solo para mostrar en tablas
