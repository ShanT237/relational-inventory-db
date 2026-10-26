"""Controlador: recibe las acciones de la vista de categorías y las pasa al servicio."""


class CategoriaControlador:

    def __init__(self, categoria_servicio, sesion):
        self.categoria_servicio = categoria_servicio
        self.sesion = sesion

    def listar(self):
        return self.categoria_servicio.listar(self.sesion)

    def crear(self, nombre, descripcion, estado):
        self.categoria_servicio.crear(self.sesion, nombre, descripcion, estado)

    def modificar(self, id_categoria, nombre, descripcion, estado):
        self.categoria_servicio.modificar(
            self.sesion, id_categoria, nombre, descripcion, estado)

    def eliminar(self, id_categoria):
        self.categoria_servicio.eliminar(self.sesion, id_categoria)