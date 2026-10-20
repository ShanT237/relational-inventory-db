"""Controlador: recibe las acciones de la vista de categorías y las pasa al servicio."""


class CategoriaControlador:

    def __init__(self, categoria_servicio):
        self.categoria_servicio = categoria_servicio

    def listar(self):
        return self.categoria_servicio.listar()

    def crear(self, nombre, descripcion, estado):
        self.categoria_servicio.crear(nombre, descripcion, estado)

    def modificar(self, id_categoria, nombre, descripcion, estado):
        self.categoria_servicio.modificar(id_categoria, nombre, descripcion, estado)

    def eliminar(self, id_categoria):
        self.categoria_servicio.eliminar(id_categoria)