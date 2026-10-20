"""Controlador: recibe las acciones de la vista de productos y las pasa al servicio."""


class ProductoControlador:

    def __init__(self, producto_servicio):
        self.producto_servicio = producto_servicio

    def listar(self):
        return self.producto_servicio.listar()

    def crear(self, codigo, nombre, id_categoria, descripcion, unidad_medida, estado):
        self.producto_servicio.crear(codigo, nombre, id_categoria, descripcion,
                                     unidad_medida, estado)

    def modificar(self, id_producto, codigo, nombre, id_categoria, descripcion,
                  unidad_medida, estado):
        self.producto_servicio.modificar(id_producto, codigo, nombre, id_categoria,
                                         descripcion, unidad_medida, estado)

    def eliminar(self, id_producto):
        self.producto_servicio.eliminar(id_producto)
