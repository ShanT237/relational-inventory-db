"""Controlador: recibe las acciones de la vista de ciudades y las pasa al servicio."""


class CiudadControlador:

    def __init__(self, ciudad_servicio, sesion):
        self.ciudad_servicio = ciudad_servicio
        self.sesion = sesion

    def listar(self):
        return self.ciudad_servicio.listar(self.sesion)

    def crear(self, nombre, departamento):
        self.ciudad_servicio.crear(self.sesion, nombre, departamento)

    def modificar(self, id_ciudad, nombre, departamento):
        self.ciudad_servicio.modificar(self.sesion, id_ciudad, nombre, departamento)

    def eliminar(self, id_ciudad):
        self.ciudad_servicio.eliminar(self.sesion, id_ciudad)