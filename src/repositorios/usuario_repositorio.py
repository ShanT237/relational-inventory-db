"""Repositorio: acceso a la tabla usuario."""
from dominio.entidades.usuario import Usuario
from repositorios.conexion_sqlserver import obtener_conexion


class UsuarioRepositorio:

    def obtener_por_nombre_usuario(self, nombre_usuario):
        """Devuelve el Usuario (con su rol) o None si no existe."""
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute(
                """SELECT u.id_usuario, u.nombre_usuario, u.nombre, u.apellido,
                          u.contrasena_hash, u.estado, r.nombre AS rol
                   FROM usuario u
                   JOIN rol r ON r.id_rol = u.id_rol
                   WHERE u.nombre_usuario = ?""",
                nombre_usuario,
            )
            fila = cur.fetchone()
            if fila is None:
                return None
            return Usuario(
                id_usuario=fila.id_usuario,
                nombre_usuario=fila.nombre_usuario,
                nombre=fila.nombre,
                apellido=fila.apellido,
                contrasena_hash=fila.contrasena_hash,
                estado=bool(fila.estado),
                rol=fila.rol,
            )
        finally:
            con.close()
