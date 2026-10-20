"""Sesión del usuario que ingresó y permisos según su rol."""
from dataclasses import dataclass


class Rol:
    ADMINISTRADOR = "Administrador"
    TRADICIONAL = "Tradicional"
    ESPORADICO = "Esporadico"


@dataclass
class Sesion:
    id_usuario: int
    nombre_usuario: str
    nombre_completo: str
    rol: str
    id_bitacora: int

    def puede_modificar(self):
        """CRUD, transacciones y reportes: Administrador y Tradicional."""
        return self.rol in (Rol.ADMINISTRADOR, Rol.TRADICIONAL)

    def es_administrador(self):
        """Gestión de usuarios y bitácora: solo el Administrador."""
        return self.rol == Rol.ADMINISTRADOR
