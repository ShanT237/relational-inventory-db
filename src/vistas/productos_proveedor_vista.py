"""Vista: transacción 'Productos por proveedor' (Tkinter). No contiene SQL.

Asigna a cada proveedor los productos que ofrece, con su precio y días de entrega."""
from vistas.crud_base import Campo, Columna, CrudVista


def _moneda(valor):
    """1500.5 -> '$ 1.500,50' (formato colombiano)."""
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"$ {texto}"


class ProductosProveedorVista:

    def __init__(self, proveedor_producto_controlador, proveedor_controlador,
                 producto_controlador):
        self.controlador = proveedor_producto_controlador
        self.proveedor_controlador = proveedor_controlador
        self.producto_controlador = producto_controlador

    def construir(self, contenedor):
        c = self.controlador

        def cargar():
            return [{"id": (x.id_proveedor, x.id_producto),   # llave compuesta
                     "id_proveedor": x.id_proveedor, "id_producto": x.id_producto,
                     "proveedor": x.proveedor, "producto": f"{x.codigo} · {x.producto}",
                     "precio": f"{x.precio_unitario:.2f}",
                     "precio_texto": _moneda(x.precio_unitario),
                     "dias_entrega": str(x.dias_entrega), "estado": x.estado,
                     "estado_texto": "Activo" if x.estado else "Inactivo",
                     "oferta": f"{x.proveedor} — {x.producto}"}
                    for x in c.listar()]

        def proveedores():
            return [(x.id_proveedor, f"{x.nombre} ({x.nit})" + ("" if x.estado else " (inactivo)"))
                    for x in self.proveedor_controlador.listar()]

        def productos():
            return [(x.id_producto, f"{x.codigo} · {x.nombre}" + ("" if x.estado else " (inactivo)"))
                    for x in self.producto_controlador.listar()]

        def datos(v):
            return v["precio"], v["dias_entrega"], v["estado"]

        CrudVista(
            contenedor,
            subtitulo="Qué productos ofrece cada proveedor, a qué precio y en cuántos días.",
            columnas=[Columna("proveedor", "Proveedor", 200),
                      Columna("producto", "Producto", 230),
                      Columna("precio_texto", "Precio unitario", 120, derecha=True,
                              orden_por="precio"),
                      Columna("dias_entrega", "Entrega (días)", 100, centrado=True),
                      Columna("estado_texto", "Estado", 80, centrado=True)],
            campos=[Campo("id_proveedor", "Proveedor", tipo="combo", opciones=proveedores,
                          obligatorio=True, bloqueado_al_editar=True),
                    Campo("id_producto", "Producto", tipo="combo", opciones=productos,
                          obligatorio=True, bloqueado_al_editar=True),
                    Campo("precio", "Precio unitario (COP)", obligatorio=True),
                    Campo("dias_entrega", "Días de entrega", obligatorio=True),
                    Campo("estado", "Activo", tipo="check")],
            cargar=cargar,
            crear=lambda v: c.crear(v["id_proveedor"], v["id_producto"], *datos(v)),
            modificar=lambda i, v: c.modificar(i[0], i[1], *datos(v)),
            eliminar=lambda i: c.eliminar(i[0], i[1]),
            texto_nuevo="Nueva oferta",
            texto_editar="Editar oferta",
            clave_nombre="oferta",
        ).construir()
