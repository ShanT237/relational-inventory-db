"""Controlador: recibe las acciones de la vista de proveedores y las pasa al servicio."""


class ProveedorControlador:

    def __init__(self, proveedor_servicio):
        self.proveedor_servicio = proveedor_servicio

    def listar(self):
        return self.proveedor_servicio.listar()

    def crear(self, nit, nombre, id_ciudad, direccion, telefono, correo, estado):
        self.proveedor_servicio.crear(nit, nombre, id_ciudad, direccion,
                                      telefono, correo, estado)

    def modificar(self, id_proveedor, nit, nombre, id_ciudad, direccion,
                  telefono, correo, estado):
        self.proveedor_servicio.modificar(id_proveedor, nit, nombre, id_ciudad,
                                          direccion, telefono, correo, estado)

    def eliminar(self, id_proveedor):
        self.proveedor_servicio.eliminar(id_proveedor)
