"""Repositorio: acceso a la tabla ciudad."""
from dominio.entidades.ciudad import Ciudad
from repositorios.conexion_sqlserver import obtener_conexion


class CiudadRepositorio:

    def listar(self):
        """Devuelve todas las ciudades ordenadas por departamento y nombre."""
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT id_ciudad, nombre, departamento FROM ciudad "
                "ORDER BY departamento, nombre")
            return [Ciudad(f.id_ciudad, f.nombre, f.departamento) for f in cur.fetchall()]
        finally:
            con.close()

    def existe_duplicada(self, nombre, departamento, excluir_id=0):
        """True si ya hay otra ciudad con ese nombre y departamento."""
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT COUNT(*) FROM ciudad "
                "WHERE nombre = ? AND departamento = ? AND id_ciudad <> ?",
                nombre, departamento, excluir_id)
            return cur.fetchone()[0] > 0
        finally:
            con.close()

    def tiene_proveedores(self, id_ciudad):
        """True si algún proveedor está ubicado en esa ciudad."""
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute("SELECT COUNT(*) FROM proveedor WHERE id_ciudad = ?", id_ciudad)
            return cur.fetchone()[0] > 0
        finally:
            con.close()

    def insertar(self, ciudad):
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute("INSERT INTO ciudad (nombre, departamento) VALUES (?, ?)",
                        ciudad.nombre, ciudad.departamento)
            con.commit()
        finally:
            con.close()

    def actualizar(self, ciudad):
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute("UPDATE ciudad SET nombre = ?, departamento = ? WHERE id_ciudad = ?",
                        ciudad.nombre, ciudad.departamento, ciudad.id_ciudad)
            con.commit()
        finally:
            con.close()

    def eliminar(self, id_ciudad):
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute("DELETE FROM ciudad WHERE id_ciudad = ?", id_ciudad)
            con.commit()
        finally:
            con.close()