"""Entidad ProveedorProducto: un producto que ofrece un proveedor (tabla proveedor_producto)."""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class ProveedorProducto:
    id_proveedor: int
    id_producto: int
    precio_unitario: Decimal
    dias_entrega: int = 0
    estado: bool = True            # True = el proveedor ofrece el producto actualmente
    # Solo para mostrar en tablas (vienen del JOIN):
    proveedor: Optional[str] = None
    nit: Optional[str] = None
    producto: Optional[str] = None
    codigo: Optional[str] = None
