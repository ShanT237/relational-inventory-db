"""Conexión a SQL Server con pyodbc."""
import pyodbc

from configuracion import configuracion


def obtener_conexion():
    """Abre y devuelve una conexión nueva."""
    cadena = (
        f"DRIVER={{{configuracion.DRIVER}}};"
        f"SERVER={configuracion.SERVIDOR};"
        f"DATABASE={configuracion.BASE_DATOS};"
        "TrustServerCertificate=yes;"
    )
    if configuracion.USUARIO:
        cadena += f"UID={configuracion.USUARIO};PWD={configuracion.CLAVE};"
    else:
        cadena += "Trusted_Connection=yes;"
    return pyodbc.connect(cadena)