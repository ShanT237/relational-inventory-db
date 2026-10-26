"""Validaciones de autorización compartidas por los servicios."""
from dominio.excepciones.regla_dominio_error import ReglaDominioError


def requiere_sesion(sesion):
    if sesion is None:
        raise ReglaDominioError("Debes iniciar sesión para realizar esta operación.")


def requiere_modificar(sesion):
    requiere_sesion(sesion)
    if not sesion.puede_modificar():
        raise ReglaDominioError("Tu rol no tiene permiso para modificar la información.")


def requiere_administrador(sesion):
    requiere_sesion(sesion)
    if not sesion.es_administrador():
        raise ReglaDominioError("Esta operación está disponible solo para el Administrador.")
