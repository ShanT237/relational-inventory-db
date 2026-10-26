"""Repositorio: consultas de lectura para los reportes en PDF."""
from repositorios.conexion_sqlserver import obtener_conexion


class ReporteRepositorio:

    # ---------------------------------------------- datos de los filtros elegidos
    def obtener_proveedor(self, id_proveedor):
        """(nombre, nit) del proveedor, o None si ya no existe."""
        return self._una_fila(
            "SELECT nombre, nit FROM proveedor WHERE id_proveedor = ?", id_proveedor)

    def obtener_producto(self, id_producto):
        """(codigo, nombre) del producto, o None si ya no existe."""
        return self._una_fila(
            "SELECT codigo, nombre FROM producto WHERE id_producto = ?", id_producto)

    def obtener_categoria(self, id_categoria):
        """(nombre,) de la categoría, o None si ya no existe."""
        return self._una_fila(
            "SELECT nombre FROM categoria WHERE id_categoria = ?", id_categoria)

    def obtener_ciudad(self, id_ciudad):
        """(nombre, departamento) de la ciudad, o None si ya no existe."""
        return self._una_fila(
            "SELECT nombre, departamento FROM ciudad WHERE id_ciudad = ?", id_ciudad)

    # ------------------------------------------------------------- los 5 reportes
    def productos_de_proveedor(self, id_proveedor):
        """codigo, producto, categoria, unidad_medida, precio_unitario, dias_entrega, estado."""
        return self._filas(
            "SELECT pr.codigo, pr.nombre, c.nombre, pr.unidad_medida, "
            "       pp.precio_unitario, pp.dias_entrega, pp.estado "
            "FROM proveedor_producto pp "
            "JOIN producto pr ON pr.id_producto = pp.id_producto "
            "JOIN categoria c ON c.id_categoria = pr.id_categoria "
            "WHERE pp.id_proveedor = ? "
            "ORDER BY pr.nombre", id_proveedor)

    def proveedores_por_ubicacion(self, id_ciudad=None, departamento=None):
        """departamento, ciudad, proveedor, nit, producto, precio_unitario.
        Incluye proveedores sin productos (producto y precio vienen como None)."""
        if id_ciudad is not None:
            condicion, parametro = "c.id_ciudad = ?", id_ciudad
        else:
            condicion, parametro = "c.departamento = ?", departamento
        return self._filas(
            "SELECT c.departamento, c.nombre, p.nombre, p.nit, pr.nombre, pp.precio_unitario "
            "FROM proveedor p "
            "JOIN ciudad c ON c.id_ciudad = p.id_ciudad "
            "LEFT JOIN proveedor_producto pp ON pp.id_proveedor = p.id_proveedor "
            "LEFT JOIN producto pr ON pr.id_producto = pp.id_producto "
            "WHERE " + condicion + " "
            "ORDER BY c.departamento, c.nombre, p.nombre, pr.nombre", parametro)

    def proveedores_de_producto(self, id_producto):
        """proveedor, nit, ciudad, departamento, precio_unitario, dias_entrega, estado."""
        return self._filas(
            "SELECT p.nombre, p.nit, c.nombre, c.departamento, "
            "       pp.precio_unitario, pp.dias_entrega, pp.estado "
            "FROM proveedor_producto pp "
            "JOIN proveedor p ON p.id_proveedor = pp.id_proveedor "
            "JOIN ciudad c ON c.id_ciudad = p.id_ciudad "
            "WHERE pp.id_producto = ? "
            "ORDER BY pp.precio_unitario, p.nombre", id_producto)

    def productos_de_categoria(self, id_categoria):
        """codigo, producto, unidad_medida, descripcion, estado."""
        return self._filas(
            "SELECT codigo, nombre, unidad_medida, descripcion, estado "
            "FROM producto WHERE id_categoria = ? ORDER BY nombre", id_categoria)

    def cantidad_por_categoria(self, activo=None):
        """categoria, cantidad. activo=True/False cuenta solo esos productos; None cuenta todos.
        Las categorías sin productos aparecen con 0."""
        condicion, parametros = "", []
        if activo is not None:
            condicion, parametros = " AND pr.estado = ?", [1 if activo else 0]
        return self._filas(
            "SELECT c.nombre, COUNT(pr.id_producto) "
            "FROM categoria c "
            "LEFT JOIN producto pr ON pr.id_categoria = c.id_categoria" + condicion + " "
            "GROUP BY c.id_categoria, c.nombre ORDER BY c.nombre", *parametros)

    # ------------------------------------------------------------------ privados
    @staticmethod
    def _filas(sql, *parametros):
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute(sql, *parametros)
            return [tuple(fila) for fila in cur.fetchall()]
        finally:
            con.close()

    def _una_fila(self, sql, *parametros):
        filas = self._filas(sql, *parametros)
        return filas[0] if filas else None
