"""Controlador: recibe las acciones de la vista de transacciones y las pasa al servicio."""


class ProveedorProductoControlador:

    def __init__(self, proveedor_producto_servicio, sesion):
        self.servicio = proveedor_producto_servicio
        self.sesion = sesion

    def listar(self):
        return self.servicio.listar(self.sesion)

    def crear(self, id_proveedor, id_producto, precio, dias_entrega, estado):
        self.servicio.crear(
            self.sesion, id_proveedor, id_producto, precio, dias_entrega, estado)

    def modificar(self, id_proveedor, id_producto, precio, dias_entrega, estado):
        self.servicio.modificar(
            self.sesion, id_proveedor, id_producto, precio, dias_entrega, estado)

    def eliminar(self, id_proveedor, id_producto):
        self.servicio.eliminar(self.sesion, id_proveedor, id_producto)
