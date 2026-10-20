"""Repositorio: acceso a la tabla producto."""
from dominio.entidades.producto import Producto
from repositorios.conexion_sqlserver import obtener_conexion


class ProductoRepositorio:

    def listar(self):
        """Devuelve todos los productos (con su categoría) ordenados por nombre."""
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT pr.id_producto, pr.codigo, pr.nombre, pr.descripcion, "
                "       pr.unidad_medida, pr.estado, pr.id_categoria, "
                "       c.nombre AS categoria "
                "FROM producto pr "
                "JOIN categoria c ON c.id_categoria = pr.id_categoria "
                "ORDER BY pr.nombre")
            return [Producto(f.id_producto, f.codigo, f.nombre, f.id_categoria,
                             f.descripcion, f.unidad_medida, bool(f.estado), f.categoria)
                    for f in cur.fetchall()]
        finally:
            con.close()

    def existe_codigo(self, codigo, excluir_id=0):
        """True si ya hay otro producto con ese código."""
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT COUNT(*) FROM producto WHERE codigo = ? AND id_producto <> ?",
                codigo, excluir_id)
            return cur.fetchone()[0] > 0
        finally:
            con.close()

    def tiene_proveedores(self, id_producto):
        """True si algún proveedor ofrece el producto (proveedor_producto)."""
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute("SELECT COUNT(*) FROM proveedor_producto WHERE id_producto = ?",
                        id_producto)
            return cur.fetchone()[0] > 0
        finally:
            con.close()

    def insertar(self, p):
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO producto (codigo, nombre, descripcion, unidad_medida, "
                "estado, id_categoria) VALUES (?, ?, ?, ?, ?, ?)",
                p.codigo, p.nombre, p.descripcion, p.unidad_medida,
                1 if p.estado else 0, p.id_categoria)
            con.commit()
        finally:
            con.close()

    def actualizar(self, p):
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute(
                "UPDATE producto SET codigo = ?, nombre = ?, descripcion = ?, "
                "unidad_medida = ?, estado = ?, id_categoria = ? WHERE id_producto = ?",
                p.codigo, p.nombre, p.descripcion, p.unidad_medida,
                1 if p.estado else 0, p.id_categoria, p.id_producto)
            con.commit()
        finally:
            con.close()

    def eliminar(self, id_producto):
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute("DELETE FROM producto WHERE id_producto = ?", id_producto)
            con.commit()
        finally:
            con.close()
