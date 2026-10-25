"""Controlador: recibe las acciones de la vista de productos y las pasa al servicio."""


class ProductoControlador:

    def __init__(self, producto_servicio, sesion):
        self.producto_servicio = producto_servicio
        self.sesion = sesion

    def listar(self):
        return self.producto_servicio.listar(self.sesion)

    def crear(self, codigo, nombre, id_categoria, descripcion, unidad_medida, estado):
        self.producto_servicio.crear(self.sesion, codigo, nombre, id_categoria, descripcion,
                                     unidad_medida, estado)

    def modificar(self, id_producto, codigo, nombre, id_categoria, descripcion,
                  unidad_medida, estado):
        self.producto_servicio.modificar(self.sesion, id_producto, codigo, nombre, id_categoria,
                                         descripcion, unidad_medida, estado)

    def eliminar(self, id_producto):
        self.producto_servicio.eliminar(self.sesion, id_producto)
