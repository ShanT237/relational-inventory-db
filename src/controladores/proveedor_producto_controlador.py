"""Controlador: recibe las acciones de la vista de transacciones y las pasa al servicio."""


class ProveedorProductoControlador:

    def __init__(self, proveedor_producto_servicio):
        self.servicio = proveedor_producto_servicio

    def listar(self):
        return self.servicio.listar()

    def crear(self, id_proveedor, id_producto, precio, dias_entrega, estado):
        self.servicio.crear(id_proveedor, id_producto, precio, dias_entrega, estado)

    def modificar(self, id_proveedor, id_producto, precio, dias_entrega, estado):
        self.servicio.modificar(id_proveedor, id_producto, precio, dias_entrega, estado)

    def eliminar(self, id_proveedor, id_producto):
        self.servicio.eliminar(id_proveedor, id_producto)
