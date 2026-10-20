"""Datos de conexión a SQL Server.
Por defecto sirve para SQL Server Express instalado en el mismo equipo.
Si tu equipo es distinto, crea configuracion_local.py (no se sube a Git)."""
import os

DRIVER = os.getenv("BD_DRIVER", "ODBC Driver 18 for SQL Server")
SERVIDOR = os.getenv("BD_SERVIDOR", r"localhost\SQLEXPRESS")
BASE_DATOS = os.getenv("BD_NOMBRE", "proveedores_db")
USUARIO = os.getenv("BD_USUARIO", "")   # vacío = autenticación de Windows
CLAVE = os.getenv("BD_CLAVE", "")

try:
    from configuracion.configuracion_local import *   # sobrescribe lo de arriba
except ImportError:
    pass