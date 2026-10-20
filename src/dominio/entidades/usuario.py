"""Entidad Usuario (fila de la tabla usuario junto con el nombre de su rol)."""
from dataclasses import dataclass


@dataclass
class Usuario:
    id_usuario: int
    nombre_usuario: str
    nombre: str
    apellido: str
    contrasena_hash: str
    estado: bool
    rol: str
