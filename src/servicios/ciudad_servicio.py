"""Servicio: reglas del negocio de las ciudades."""
from dominio.entidades.ciudad import Ciudad
from dominio.excepciones.regla_dominio_error import ReglaDominioError


class CiudadServicio:

    def __init__(self, ciudad_repositorio):
        self.ciudad_repositorio = ciudad_repositorio

    def listar(self):
        return self.ciudad_repositorio.listar()

    def crear(self, nombre, departamento):
        ciudad = self._validar(None, nombre, departamento)
        self.ciudad_repositorio.insertar(ciudad)

    def modificar(self, id_ciudad, nombre, departamento):
        ciudad = self._validar(id_ciudad, nombre, departamento)
        self.ciudad_repositorio.actualizar(ciudad)

    def eliminar(self, id_ciudad):
        if self.ciudad_repositorio.tiene_proveedores(id_ciudad):
            raise ReglaDominioError(
                "No se puede eliminar: hay proveedores ubicados en esta ciudad.")
        self.ciudad_repositorio.eliminar(id_ciudad)

    def _validar(self, id_ciudad, nombre, departamento):
        nombre = (nombre or "").strip()
        departamento = (departamento or "").strip()
        if not nombre or not departamento:
            raise ReglaDominioError("El nombre y el departamento son obligatorios.")
        if len(nombre) > 50 or len(departamento) > 50:
            raise ReglaDominioError("El nombre y el departamento admiten máximo 50 caracteres.")
        if self.ciudad_repositorio.existe_duplicada(nombre, departamento, id_ciudad or 0):
            raise ReglaDominioError("Esa ciudad ya está registrada en ese departamento.")
        return Ciudad(id_ciudad, nombre, departamento)