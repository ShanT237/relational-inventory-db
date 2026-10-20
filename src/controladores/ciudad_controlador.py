"""Controlador: recibe las acciones de la vista de ciudades y las pasa al servicio."""


class CiudadControlador:

    def __init__(self, ciudad_servicio):
        self.ciudad_servicio = ciudad_servicio

    def listar(self):
        return self.ciudad_servicio.listar()

    def crear(self, nombre, departamento):
        self.ciudad_servicio.crear(nombre, departamento)

    def modificar(self, id_ciudad, nombre, departamento):
        self.ciudad_servicio.modificar(id_ciudad, nombre, departamento)

    def eliminar(self, id_ciudad):
        self.ciudad_servicio.eliminar(id_ciudad)    