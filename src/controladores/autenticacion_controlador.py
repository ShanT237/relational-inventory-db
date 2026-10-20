"""Controlador: recibe las acciones de las vistas y las pasa al servicio."""


class AutenticacionControlador:

    def __init__(self, autenticacion_servicio):
        self.autenticacion_servicio = autenticacion_servicio

    def iniciar_sesion(self, nombre_usuario, contrasena):
        return self.autenticacion_servicio.iniciar_sesion(nombre_usuario.strip(), contrasena)

    def cerrar_sesion(self, sesion):
        self.autenticacion_servicio.cerrar_sesion(sesion)
