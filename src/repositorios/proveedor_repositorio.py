"""Repositorio: acceso a la tabla proveedor."""
from dominio.entidades.proveedor import Proveedor
from repositorios.conexion_sqlserver import obtener_conexion


class ProveedorRepositorio:

    def listar(self):
        """Devuelve todos los proveedores (con su ciudad) ordenados por nombre."""
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT p.id_proveedor, p.nit, p.nombre, p.direccion, p.estado, "
                "       p.telefono, p.correo, p.id_ciudad, c.nombre AS ciudad, "
                "       c.departamento "
                "FROM proveedor p "
                "JOIN ciudad c ON c.id_ciudad = p.id_ciudad "
                "ORDER BY p.nombre")
            return [Proveedor(f.id_proveedor, f.nit, f.nombre, f.id_ciudad,
                              f.direccion, f.telefono, f.correo, bool(f.estado),
                              f"{f.ciudad} ({f.departamento})")
                    for f in cur.fetchall()]
        finally:
            con.close()

    def existe_nit(self, nit, excluir_id=0):
        """True si ya hay otro proveedor con ese NIT."""
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT COUNT(*) FROM proveedor WHERE nit = ? AND id_proveedor <> ?",
                nit, excluir_id)
            return cur.fetchone()[0] > 0
        finally:
            con.close()

    def tiene_productos(self, id_proveedor):
        """True si el proveedor tiene productos asignados (proveedor_producto)."""
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute("SELECT COUNT(*) FROM proveedor_producto WHERE id_proveedor = ?",
                        id_proveedor)
            return cur.fetchone()[0] > 0
        finally:
            con.close()

    def insertar(self, p):
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO proveedor (nit, nombre, direccion, estado, telefono, "
                "correo, id_ciudad) VALUES (?, ?, ?, ?, ?, ?, ?)",
                p.nit, p.nombre, p.direccion, 1 if p.estado else 0,
                p.telefono, p.correo, p.id_ciudad)
            con.commit()
        finally:
            con.close()

    def actualizar(self, p):
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute(
                "UPDATE proveedor SET nit = ?, nombre = ?, direccion = ?, estado = ?, "
                "telefono = ?, correo = ?, id_ciudad = ? WHERE id_proveedor = ?",
                p.nit, p.nombre, p.direccion, 1 if p.estado else 0,
                p.telefono, p.correo, p.id_ciudad, p.id_proveedor)
            con.commit()
        finally:
            con.close()

    def eliminar(self, id_proveedor):
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute("DELETE FROM proveedor WHERE id_proveedor = ?", id_proveedor)
            con.commit()
        finally:
            con.close()
