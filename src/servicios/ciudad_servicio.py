"""Servicio: reglas del negocio de las ciudades."""
from dominio.entidades.ciudad import Ciudad
from dominio.excepciones.regla_dominio_error import ReglaDominioError
from servicios import validaciones as v
from servicios.permisos import requiere_modificar


class CiudadServicio:

    def __init__(self, ciudad_repositorio):
        self.ciudad_repositorio = ciudad_repositorio

    def listar(self, sesion):
        requiere_modificar(sesion)
        return self.ciudad_repositorio.listar()

    def crear(self, sesion, nombre, departamento):
        requiere_modificar(sesion)
        ciudad = self._validar(None, nombre, departamento)
        self.ciudad_repositorio.insertar(ciudad)

    def modificar(self, sesion, id_ciudad, nombre, departamento):
        requiere_modificar(sesion)
        ciudad = self._validar(id_ciudad, nombre, departamento)
        self.ciudad_repositorio.actualizar(ciudad)

    def eliminar(self, sesion, id_ciudad):
        requiere_modificar(sesion)
        if self.ciudad_repositorio.tiene_proveedores(id_ciudad):
            raise ReglaDominioError(
                "No se puede eliminar: hay proveedores ubicados en esta ciudad.")
        self.ciudad_repositorio.eliminar(id_ciudad)

    def _validar(self, id_ciudad, nombre, departamento):
        nombre = v.solo_letras(nombre, "El nombre de la ciudad", minimo=3, maximo=50)
        departamento = v.solo_letras(departamento, "El departamento", minimo=3, maximo=50)
        if self.ciudad_repositorio.existe_duplicada(nombre, departamento, id_ciudad or 0):
            raise ReglaDominioError("Esa ciudad ya está registrada en ese departamento.")
        return Ciudad(id_ciudad, nombre, departamento)
