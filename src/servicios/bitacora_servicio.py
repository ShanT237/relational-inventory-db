"""Servicio: consulta administrativa de entradas y salidas."""
from datetime import date
import re

from dominio.excepciones.regla_dominio_error import ReglaDominioError
from servicios.permisos import requiere_administrador


class BitacoraServicio:

    def __init__(self, bitacora_repositorio, usuario_repositorio):
        self.bitacora_repositorio = bitacora_repositorio
        self.usuario_repositorio = usuario_repositorio

    def listar_usuarios(self, sesion):
        requiere_administrador(sesion)
        return self.usuario_repositorio.listar_nombres_usuario()

    def listar(self, sesion, nombre_usuario=None, desde=None, hasta=None):
        requiere_administrador(sesion)
        desde = self._leer_fecha(desde, "inicial")
        hasta = self._leer_fecha(hasta, "final")
        if desde and hasta and desde > hasta:
            raise ReglaDominioError("La fecha inicial no puede ser posterior a la fecha final.")
        return self.bitacora_repositorio.listar(nombre_usuario, desde, hasta)

    @staticmethod
    def _leer_fecha(valor, etiqueta):
        if valor is None:
            return None
        if not isinstance(valor, str):
            raise ReglaDominioError(
                f"La fecha {etiqueta} debe tener el formato AAAA-MM-DD.")
        valor = valor.strip()
        if not valor:
            return None
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", valor):
            raise ReglaDominioError(
                f"La fecha {etiqueta} debe tener el formato AAAA-MM-DD.")
        try:
            return date.fromisoformat(valor)
        except ValueError as error:
            raise ReglaDominioError(
                f"La fecha {etiqueta} debe tener el formato AAAA-MM-DD.") from error
