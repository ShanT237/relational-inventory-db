"""Controlador: recibe las acciones de la vista de proveedores y las pasa al servicio."""


class ProveedorControlador:

    def __init__(self, proveedor_servicio, sesion):
        self.proveedor_servicio = proveedor_servicio
        self.sesion = sesion

    def listar(self):
        return self.proveedor_servicio.listar(self.sesion)

    def crear(self, nit, nombre, id_ciudad, direccion, telefono, correo, estado):
        self.proveedor_servicio.crear(self.sesion, nit, nombre, id_ciudad, direccion,
                                      telefono, correo, estado)

    def modificar(self, id_proveedor, nit, nombre, id_ciudad, direccion,
                  telefono, correo, estado):
        self.proveedor_servicio.modificar(self.sesion, id_proveedor, nit, nombre, id_ciudad,
                                          direccion, telefono, correo, estado)

    def eliminar(self, id_proveedor):
        self.proveedor_servicio.eliminar(self.sesion, id_proveedor)
