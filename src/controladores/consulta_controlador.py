"""Controlador: consultas disponibles para cualquier usuario autenticado."""


class ConsultaControlador:

    def __init__(self, consulta_servicio, sesion):
        self.consulta_servicio = consulta_servicio
        self.sesion = sesion

    def ejecutar(self, identificador):
        return self.consulta_servicio.ejecutar(self.sesion, identificador)
