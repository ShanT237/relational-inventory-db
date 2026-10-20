"""Entidad Proveedor (fila de la tabla proveedor)."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Proveedor:
    id_proveedor: Optional[int]   # None mientras el proveedor no se ha guardado
    nit: str
    nombre: str
    id_ciudad: int
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    estado: bool = True           # True = activo, False = inactivo
    ciudad: Optional[str] = None  # "Ciudad (Departamento)", solo para mostrar en tablas
