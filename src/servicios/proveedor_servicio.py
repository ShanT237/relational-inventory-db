"""Servicio: reglas del negocio de los proveedores."""
import re

from dominio.entidades.proveedor import Proveedor
from dominio.excepciones.regla_dominio_error import ReglaDominioError

_NIT = re.compile(r"^[0-9][0-9.\-]*$")
_TELEFONO = re.compile(r"^[0-9+\-() ]+$")
_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ProveedorServicio:

    def __init__(self, proveedor_repositorio):
        self.proveedor_repositorio = proveedor_repositorio

    def listar(self):
        return self.proveedor_repositorio.listar()

    def crear(self, nit, nombre, id_ciudad, direccion, telefono, correo, estado):
        proveedor = self._validar(None, nit, nombre, id_ciudad, direccion,
                                  telefono, correo, estado)
        self.proveedor_repositorio.insertar(proveedor)

    def modificar(self, id_proveedor, nit, nombre, id_ciudad, direccion,
                  telefono, correo, estado):
        proveedor = self._validar(id_proveedor, nit, nombre, id_ciudad, direccion,
                                  telefono, correo, estado)
        self.proveedor_repositorio.actualizar(proveedor)

    def eliminar(self, id_proveedor):
        if self.proveedor_repositorio.tiene_productos(id_proveedor):
            raise ReglaDominioError(
                "No se puede eliminar: el proveedor tiene productos asignados. "
                "Puedes desmarcar «Activo» para desactivarlo.")
        self.proveedor_repositorio.eliminar(id_proveedor)

    def _validar(self, id_proveedor, nit, nombre, id_ciudad, direccion,
                 telefono, correo, estado):
        nit = (nit or "").strip()
        nombre = (nombre or "").strip()
        direccion = (direccion or "").strip() or None
        telefono = (telefono or "").strip() or None
        correo = (correo or "").strip() or None

        if not nit:
            raise ReglaDominioError("El NIT es obligatorio.")
        if len(nit) > 20:
            raise ReglaDominioError("El NIT admite máximo 20 caracteres.")
        if not _NIT.match(nit):
            raise ReglaDominioError(
                "El NIT solo admite números, puntos y guion (ej. 900123456-7).")
        if not nombre:
            raise ReglaDominioError("El nombre es obligatorio.")
        if len(nombre) > 200:
            raise ReglaDominioError("El nombre admite máximo 200 caracteres.")
        if id_ciudad is None:
            raise ReglaDominioError("Selecciona la ciudad del proveedor.")
        if direccion is not None and len(direccion) > 200:
            raise ReglaDominioError("La dirección admite máximo 200 caracteres.")
        if telefono is not None:
            if len(telefono) > 20:
                raise ReglaDominioError("El teléfono admite máximo 20 caracteres.")
            if not _TELEFONO.match(telefono):
                raise ReglaDominioError("El teléfono solo admite números y + - ( ).")
        if correo is not None:
            if len(correo) > 100:
                raise ReglaDominioError("El correo admite máximo 100 caracteres.")
            if not _CORREO.match(correo):
                raise ReglaDominioError("El correo no tiene un formato válido.")
        if self.proveedor_repositorio.existe_nit(nit, id_proveedor or 0):
            raise ReglaDominioError("Ya existe un proveedor con ese NIT.")
        return Proveedor(id_proveedor, nit, nombre, int(id_ciudad), direccion,
                         telefono, correo, bool(estado))
