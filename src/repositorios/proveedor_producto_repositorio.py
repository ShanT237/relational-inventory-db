"""Repositorio: acceso a la tabla proveedor_producto (llave primaria compuesta)."""
from dominio.entidades.proveedor_producto import ProveedorProducto
from repositorios.conexion_sqlserver import obtener_conexion


class ProveedorProductoRepositorio:

    def listar(self):
        """Devuelve todas las ofertas con el nombre del proveedor y del producto."""
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT pp.id_proveedor, pp.id_producto, pp.precio_unitario, "
                "       pp.dias_entrega, pp.estado, p.nombre AS proveedor, p.nit, "
                "       pr.nombre AS producto, pr.codigo "
                "FROM proveedor_producto pp "
                "JOIN proveedor p  ON p.id_proveedor = pp.id_proveedor "
                "JOIN producto  pr ON pr.id_producto = pp.id_producto "
                "ORDER BY p.nombre, pr.nombre")
            return [ProveedorProducto(f.id_proveedor, f.id_producto, f.precio_unitario,
                                      f.dias_entrega, bool(f.estado), f.proveedor,
                                      f.nit, f.producto, f.codigo)
                    for f in cur.fetchall()]
        finally:
            con.close()

    def existe(self, id_proveedor, id_producto):
        """True si el proveedor ya tiene asignado ese producto."""
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT COUNT(*) FROM proveedor_producto "
                "WHERE id_proveedor = ? AND id_producto = ?", id_proveedor, id_producto)
            return cur.fetchone()[0] > 0
        finally:
            con.close()

    def obtener_estados(self, id_proveedor, id_producto):
        """Devuelve (proveedor_activo, producto_activo), o None si alguno no existe."""
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT p.estado, pr.estado FROM proveedor p, producto pr "
                "WHERE p.id_proveedor = ? AND pr.id_producto = ?",
                id_proveedor, id_producto)
            fila = cur.fetchone()
            return None if fila is None else (bool(fila[0]), bool(fila[1]))
        finally:
            con.close()

    def insertar(self, o):
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO proveedor_producto (id_proveedor, id_producto, "
                "precio_unitario, dias_entrega, estado) VALUES (?, ?, ?, ?, ?)",
                o.id_proveedor, o.id_producto, o.precio_unitario, o.dias_entrega,
                1 if o.estado else 0)
            con.commit()
        finally:
            con.close()

    def actualizar(self, o):
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute(
                "UPDATE proveedor_producto SET precio_unitario = ?, dias_entrega = ?, "
                "estado = ? WHERE id_proveedor = ? AND id_producto = ?",
                o.precio_unitario, o.dias_entrega, 1 if o.estado else 0,
                o.id_proveedor, o.id_producto)
            con.commit()
        finally:
            con.close()

    def eliminar(self, id_proveedor, id_producto):
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute(
                "DELETE FROM proveedor_producto WHERE id_proveedor = ? AND id_producto = ?",
                id_proveedor, id_producto)
            con.commit()
        finally:
            con.close()
