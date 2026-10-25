"""Servicio: autorización y ejecución de consultas de solo lectura."""
from dominio.excepciones.regla_dominio_error import ReglaDominioError
from servicios.permisos import requiere_sesion


class ConsultaServicio:

    def __init__(self, consulta_repositorio):
        self.consulta_repositorio = consulta_repositorio

    def ejecutar(self, sesion, identificador):
        requiere_sesion(sesion)
        try:
            return self.consulta_repositorio.ejecutar(identificador)
        except ValueError as error:
            raise ReglaDominioError(str(error)) from error
