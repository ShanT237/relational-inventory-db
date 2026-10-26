"""Servicio: reglas del negocio de los proveedores."""
from dominio.entidades.proveedor import Proveedor
from dominio.excepciones.regla_dominio_error import ReglaDominioError
from servicios import validaciones as v
from servicios.permisos import requiere_modificar


class ProveedorServicio:

    def __init__(self, proveedor_repositorio):
        self.proveedor_repositorio = proveedor_repositorio

    def listar(self, sesion):
        requiere_modificar(sesion)
        return self.proveedor_repositorio.listar()

    def crear(self, sesion, nit, nombre, id_ciudad, direccion, telefono, correo, estado):
        requiere_modificar(sesion)
        proveedor = self._validar(None, nit, nombre, id_ciudad, direccion,
                                  telefono, correo, estado)
        self.proveedor_repositorio.insertar(proveedor)

    def modificar(self, sesion, id_proveedor, nit, nombre, id_ciudad, direccion,
                  telefono, correo, estado):
        requiere_modificar(sesion)
        proveedor = self._validar(id_proveedor, nit, nombre, id_ciudad, direccion,
                                  telefono, correo, estado)
        self.proveedor_repositorio.actualizar(proveedor)

    def eliminar(self, sesion, id_proveedor):
        requiere_modificar(sesion)
        if self.proveedor_repositorio.tiene_productos(id_proveedor):
            raise ReglaDominioError(
                "No se puede eliminar: el proveedor tiene productos asignados. "
                "Puedes desmarcar «Activo» para desactivarlo.")
        self.proveedor_repositorio.eliminar(id_proveedor)

    def _validar(self, id_proveedor, nit, nombre, id_ciudad, direccion,
                 telefono, correo, estado):
        nit = v.nit(nit)
        nombre = v.texto(nombre, "El nombre", minimo=3, maximo=200)
        v.seleccion(id_ciudad, "La ciudad del proveedor")
        direccion = v.texto(direccion, "La dirección", minimo=5, maximo=200)
        telefono = v.telefono(telefono)
        correo = v.correo(correo)
        if self.proveedor_repositorio.existe_nit(nit, id_proveedor or 0):
            raise ReglaDominioError("Ya existe un proveedor con ese NIT.")
        return Proveedor(id_proveedor, nit, nombre, int(id_ciudad), direccion,
                         telefono, correo, bool(estado))
