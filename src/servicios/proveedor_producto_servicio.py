"""Servicio: reglas del negocio de las ofertas (qué producto vende cada proveedor)."""
import re
from decimal import Decimal

from dominio.entidades.proveedor_producto import ProveedorProducto
from dominio.excepciones.regla_dominio_error import ReglaDominioError

_PRECIO = re.compile(r"^\d{1,10}([.,]\d{1,2})?$")   # DECIMAL(12,2), sin separador de miles
_ENTERO = re.compile(r"^\d{1,5}$")
_MAX_DIAS = 32767                                    # SMALLINT


class ProveedorProductoServicio:

    def __init__(self, proveedor_producto_repositorio):
        self.repositorio = proveedor_producto_repositorio

    def listar(self):
        return self.repositorio.listar()

    def crear(self, id_proveedor, id_producto, precio, dias_entrega, estado):
        if id_proveedor is None:
            raise ReglaDominioError("Selecciona el proveedor.")
        if id_producto is None:
            raise ReglaDominioError("Selecciona el producto.")
        oferta = self._armar(id_proveedor, id_producto, precio, dias_entrega, estado)
        if self.repositorio.existe(id_proveedor, id_producto):
            raise ReglaDominioError(
                "Ese proveedor ya ofrece ese producto. Selecciónalo en la tabla "
                "para modificar su precio o su tiempo de entrega.")
        self._validar_activos(oferta)
        self.repositorio.insertar(oferta)

    def modificar(self, id_proveedor, id_producto, precio, dias_entrega, estado):
        oferta = self._armar(id_proveedor, id_producto, precio, dias_entrega, estado)
        self._validar_activos(oferta)
        self.repositorio.actualizar(oferta)

    def eliminar(self, id_proveedor, id_producto):
        self.repositorio.eliminar(id_proveedor, id_producto)

    # ------------------------------------------------------------------ privados
    def _armar(self, id_proveedor, id_producto, precio, dias_entrega, estado):
        return ProveedorProducto(int(id_proveedor), int(id_producto),
                                 self._leer_precio(precio),
                                 self._leer_dias(dias_entrega), bool(estado))

    @staticmethod
    def _leer_precio(texto):
        texto = (str(texto) if texto is not None else "").replace("$", "").strip()
        if not texto:
            raise ReglaDominioError("El precio unitario es obligatorio.")
        if not _PRECIO.match(texto):
            raise ReglaDominioError(
                "El precio debe ser un número con hasta 2 decimales (ej. 1500 o 1500,50), "
                "sin separador de miles.")
        valor = Decimal(texto.replace(",", "."))
        if valor <= 0:
            raise ReglaDominioError("El precio debe ser mayor que 0.")
        return valor

    @staticmethod
    def _leer_dias(texto):
        texto = (str(texto) if texto is not None else "").strip()
        if not texto:
            raise ReglaDominioError("Los días de entrega son obligatorios (0 si es inmediata).")
        if not _ENTERO.match(texto) or int(texto) > _MAX_DIAS:
            raise ReglaDominioError(
                f"Los días de entrega deben ser un número entero entre 0 y {_MAX_DIAS}.")
        return int(texto)

    def _validar_activos(self, oferta):
        """Una oferta solo puede estar activa si su proveedor y su producto lo están."""
        estados = self.repositorio.obtener_estados(oferta.id_proveedor, oferta.id_producto)
        if estados is None:
            raise ReglaDominioError("El proveedor o el producto ya no existe.")
        proveedor_activo, producto_activo = estados
        if oferta.estado and not proveedor_activo:
            raise ReglaDominioError(
                "El proveedor está inactivo: no se puede dejar activa esta oferta.")
        if oferta.estado and not producto_activo:
            raise ReglaDominioError(
                "El producto está inactivo: no se puede dejar activa esta oferta.")
