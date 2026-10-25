"""Controlador: acceso administrativo a la bitácora."""


class BitacoraControlador:

    def __init__(self, bitacora_servicio, sesion):
        self.bitacora_servicio = bitacora_servicio
        self.sesion = sesion

    def listar_usuarios(self):
        return self.bitacora_servicio.listar_usuarios(self.sesion)

    def listar(self, nombre_usuario=None, desde=None, hasta=None):
        return self.bitacora_servicio.listar(
            self.sesion, nombre_usuario, desde, hasta)
