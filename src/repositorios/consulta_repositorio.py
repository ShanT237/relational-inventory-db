"""Repositorio: consultas de lectura para las opciones del menú Consultas."""
from repositorios.conexion_sqlserver import obtener_conexion


class ConsultaRepositorio:
    _CONSULTAS = {
        "proveedores_ciudad_productos": """
            SELECT p.nombre AS proveedor, c.nombre AS ciudad, c.departamento,
                   pr.nombre AS producto, pp.precio_unitario
            FROM proveedor p
            JOIN ciudad c ON c.id_ciudad = p.id_ciudad
            JOIN proveedor_producto pp ON pp.id_proveedor = p.id_proveedor
            JOIN producto pr ON pr.id_producto = pp.id_producto
            ORDER BY p.nombre, pr.nombre
        """,
        "productos_categoria_proveedores": """
            SELECT pr.codigo, pr.nombre AS producto, c.nombre AS categoria,
                   p.nombre AS proveedor, pp.precio_unitario, pp.dias_entrega
            FROM producto pr
            JOIN categoria c ON c.id_categoria = pr.id_categoria
            JOIN proveedor_producto pp ON pp.id_producto = pr.id_producto
            JOIN proveedor p ON p.id_proveedor = pp.id_proveedor
            ORDER BY pr.nombre, p.nombre
        """,
        "bitacora_usuarios_roles": """
            SELECT b.fecha_hora_entrada, b.fecha_hora_salida,
                   u.nombre_usuario, u.nombre, u.apellido, r.nombre AS rol
            FROM bitacora b
            JOIN usuario u ON u.id_usuario = b.id_usuario
            JOIN rol r ON r.id_rol = u.id_rol
            ORDER BY b.fecha_hora_entrada DESC
        """,
        "proveedores_precio_sobre_promedio": """
            SELECT p.nit, p.nombre
            FROM proveedor p
            WHERE p.id_proveedor IN (
                SELECT pp.id_proveedor
                FROM proveedor_producto pp
                WHERE pp.precio_unitario >
                    (SELECT AVG(precio_unitario) FROM proveedor_producto)
            )
            ORDER BY p.nombre
        """,
        "productos_sin_proveedor": """
            SELECT pr.codigo, pr.nombre
            FROM producto pr
            WHERE NOT EXISTS (
                SELECT 1
                FROM proveedor_producto pp
                WHERE pp.id_producto = pr.id_producto
            )
            ORDER BY pr.nombre
        """,
    }

    def ejecutar(self, identificador):
        consulta = self._CONSULTAS.get(identificador)
        if consulta is None:
            raise ValueError("La consulta solicitada no existe.")

        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute(consulta)
            columnas = [columna[0] for columna in cur.description]
            filas = [tuple(fila) for fila in cur.fetchall()]
            return columnas, filas
        finally:
            con.close()
