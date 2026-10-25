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

    def listar_usuarios(self):
        """Devuelve datos administrativos sin incluir los hashes de contraseña."""
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute(
                """SELECT u.id_usuario, u.nombre_usuario, u.nombre, u.apellido,
                          u.numero_documento, u.id_tipo_documento,
                          td.nombre AS tipo_documento, u.id_rol, r.nombre AS rol,
                          u.estado
                   FROM usuario u
                   JOIN rol r ON r.id_rol = u.id_rol
                   JOIN tipo_documento td
                     ON td.id_tipo_documento = u.id_tipo_documento
                   ORDER BY u.nombre_usuario""")
            return [{
                "id": fila.id_usuario,
                "nombre_usuario": fila.nombre_usuario,
                "nombre": fila.nombre,
                "apellido": fila.apellido,
                "numero_documento": fila.numero_documento,
                "id_tipo_documento": fila.id_tipo_documento,
                "tipo_documento": fila.tipo_documento,
                "id_rol": fila.id_rol,
                "rol": fila.rol,
                "estado": bool(fila.estado),
                "estado_texto": "Activo" if fila.estado else "Inactivo",
            } for fila in cur.fetchall()]
        finally:
            con.close()

    def listar_roles(self):
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute("SELECT id_rol, nombre FROM rol ORDER BY nombre")
            return [(fila.id_rol, fila.nombre) for fila in cur.fetchall()]
        finally:
            con.close()

    def listar_tipos_documento(self):
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT id_tipo_documento, nombre FROM tipo_documento ORDER BY nombre")
            return [(fila.id_tipo_documento, fila.nombre) for fila in cur.fetchall()]
        finally:
            con.close()

    def listar_nombres_usuario(self):
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute("SELECT nombre_usuario FROM usuario ORDER BY nombre_usuario")
            return [fila.nombre_usuario for fila in cur.fetchall()]
        finally:
            con.close()

    def obtener_para_editar(self, id_usuario):
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute(
                """SELECT u.id_usuario, u.nombre_usuario, u.nombre, u.apellido,
                          u.numero_documento, u.id_tipo_documento, u.id_rol,
                          r.nombre AS rol, u.estado
                   FROM usuario u
                   JOIN rol r ON r.id_rol = u.id_rol
                   WHERE u.id_usuario = ?""",
                id_usuario,
            )
            fila = cur.fetchone()
            if fila is None:
                return None
            return {
                "id": fila.id_usuario,
                "nombre_usuario": fila.nombre_usuario,
                "nombre": fila.nombre,
                "apellido": fila.apellido,
                "numero_documento": fila.numero_documento,
                "id_tipo_documento": fila.id_tipo_documento,
                "id_rol": fila.id_rol,
                "rol": fila.rol,
                "estado": bool(fila.estado),
            }
        finally:
            con.close()

    def existe_nombre_usuario(self, nombre_usuario, excluir_id=None):
        return self._existe("nombre_usuario", nombre_usuario, excluir_id)

    def existe_documento(self, numero_documento, excluir_id=None):
        return self._existe("numero_documento", numero_documento, excluir_id)

    def _existe(self, columna, valor, excluir_id):
        if columna not in ("nombre_usuario", "numero_documento"):
            raise ValueError("Columna de búsqueda no permitida.")
        con = obtener_conexion()
        try:
            cur = con.cursor()
            if excluir_id is None:
                cur.execute(f"SELECT COUNT(*) FROM usuario WHERE {columna} = ?", valor)
            else:
                cur.execute(
                    f"SELECT COUNT(*) FROM usuario WHERE {columna} = ? "
                    "AND id_usuario <> ?",
                    valor, excluir_id,
                )
            return cur.fetchone()[0] > 0
        finally:
            con.close()

    def insertar_usuario(self, datos):
        con = obtener_conexion()
        try:
            cur = con.cursor()
            self._bloquear_roles(cur, datos["id_rol"])
            self._validar_unico_administrador(cur, datos["id_rol"])
            cur.execute(
                """INSERT INTO usuario
                       (nombre_usuario, nombre, apellido, contrasena_hash,
                        numero_documento, id_rol, id_tipo_documento, estado, creado_por)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                datos["nombre_usuario"], datos["nombre"], datos["apellido"],
                datos["contrasena_hash"], datos["numero_documento"], datos["id_rol"],
                datos["id_tipo_documento"], 1 if datos["estado"] else 0,
                datos["creado_por"],
            )
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    def actualizar_usuario(self, id_usuario, datos):
        con = obtener_conexion()
        try:
            cur = con.cursor()
            self._bloquear_roles(cur, datos["id_rol"])
            self._validar_unico_administrador(cur, datos["id_rol"], id_usuario)
            columnas = [
                "nombre_usuario = ?", "nombre = ?", "apellido = ?",
                "numero_documento = ?", "id_rol = ?", "id_tipo_documento = ?",
                "estado = ?",
            ]
            valores = [
                datos["nombre_usuario"], datos["nombre"], datos["apellido"],
                datos["numero_documento"], datos["id_rol"],
                datos["id_tipo_documento"], 1 if datos["estado"] else 0,
            ]
            if datos.get("contrasena_hash"):
                columnas.append("contrasena_hash = ?")
                valores.append(datos["contrasena_hash"])
            valores.append(id_usuario)
            cur.execute(
                f"UPDATE usuario SET {', '.join(columnas)} WHERE id_usuario = ?",
                *valores,
            )
            if cur.rowcount == 0:
                raise ValueError("El usuario ya no existe.")
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    @staticmethod
    def _bloquear_roles(cur, id_rol):
        cur.execute("SELECT nombre FROM rol WITH (TABLOCKX, HOLDLOCK) WHERE id_rol = ?",
                    id_rol)
        if cur.fetchone() is None:
            raise ValueError("El rol seleccionado ya no existe.")

    @staticmethod
    def _validar_unico_administrador(cur, id_rol, excluir_id=None):
        cur.execute("SELECT nombre FROM rol WHERE id_rol = ?", id_rol)
        rol = cur.fetchone()
        if rol is None:
            raise ValueError("El rol seleccionado ya no existe.")
        if rol.nombre != "Administrador":
            return
        if excluir_id is None:
            cur.execute("SELECT COUNT(*) FROM usuario WHERE id_rol = ?", id_rol)
        else:
            cur.execute(
                "SELECT COUNT(*) FROM usuario WHERE id_rol = ? AND id_usuario <> ?",
                id_rol, excluir_id,
            )
        if cur.fetchone()[0]:
            raise ValueError("Ya existe un Administrador.")
