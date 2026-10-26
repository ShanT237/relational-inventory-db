"""Datos de conexión a SQL Server.
Orden de prioridad (gana el último): valores por defecto < archivo .env (en la raíz del
proyecto) < variables de entorno < configuracion_local.py.
Lo normal es configurar todo en .env (ver .env.example); ni .env ni
configuracion_local.py se suben a Git."""
import os
from pathlib import Path


def _cargar_env():
    """Lee <raíz>/.env (líneas CLAVE=valor) sin pisar variables que ya estén definidas."""
    ruta = Path(__file__).resolve().parents[2] / ".env"
    if not ruta.is_file():
        return
    for linea in ruta.read_text(encoding="utf-8-sig").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        os.environ.setdefault(clave.strip(), valor.strip().strip('"').strip("'"))


_cargar_env()

DRIVER = os.getenv("BD_DRIVER", "ODBC Driver 18 for SQL Server")
SERVIDOR = os.getenv("BD_SERVIDOR", r"localhost\SQLEXPRESS")
BASE_DATOS = os.getenv("BD_NOMBRE", "proveedores_db")
USUARIO = os.getenv("BD_USUARIO", "")   # vacío = autenticación de Windows
CLAVE = os.getenv("BD_CLAVE") or os.getenv("MSSQL_SA_PASSWORD", "")

try:
    from configuracion.configuracion_local import *   # sobrescribe lo de arriba
except ImportError:
    pass
