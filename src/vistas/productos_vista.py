"""Vista: CRUD de productos (Tkinter). No contiene SQL."""
from vistas.crud_base import Campo, Columna, CrudVista

UNIDADES = ("unidad", "kg", "g", "libra", "litro", "ml", "caja", "paquete", "docena")


class ProductosVista:

    def __init__(self, producto_controlador, categoria_controlador):
        self.controlador = producto_controlador
        self.categoria_controlador = categoria_controlador

    def construir(self, contenedor):
        c = self.controlador

        def cargar():
            return [{"id": x.id_producto, "codigo": x.codigo, "nombre": x.nombre,
                     "categoria": x.categoria, "id_categoria": x.id_categoria,
                     "descripcion": x.descripcion or "",
                     "unidad_medida": x.unidad_medida or "", "estado": x.estado,
                     "estado_texto": "Activo" if x.estado else "Inactivo"}
                    for x in c.listar()]

        def categorias():
            return [(x.id_categoria, x.nombre + ("" if x.estado else " (inactiva)"))
                    for x in self.categoria_controlador.listar()]

        def datos(v):
            return (v["codigo"], v["nombre"], v["id_categoria"], v["descripcion"],
                    v["unidad_medida"], v["estado"])

        CrudVista(
            contenedor,
            subtitulo="Catálogo de productos que se pueden adquirir con los proveedores.",
            columnas=[Columna("codigo", "Código", 100),
                      Columna("nombre", "Nombre", 220),
                      Columna("categoria", "Categoría", 150),
                      Columna("unidad_medida", "Unidad", 80, True),
                      Columna("estado_texto", "Estado", 80, True)],
            campos=[Campo("codigo", "Código", obligatorio=True, max_largo=30,
                          ayuda="Letras, números y guion, sin espacios. Ej: LAC-001"),
                    Campo("nombre", "Nombre", obligatorio=True, max_largo=200),
                    Campo("id_categoria", "Categoría", tipo="combo", opciones=categorias,
                          obligatorio=True),
                    Campo("unidad_medida", "Unidad de medida", tipo="combo_texto",
                          opciones=lambda: UNIDADES, obligatorio=True),
                    Campo("descripcion", "Descripción", tipo="area", obligatorio=True,
                          max_largo=250),
                    Campo("estado", "Activo", tipo="check")],
            cargar=cargar,
            crear=lambda v: c.crear(*datos(v)),
            modificar=lambda i, v: c.modificar(i, *datos(v)),
            eliminar=c.eliminar,
            texto_nuevo="Nuevo producto",
            texto_editar="Editar producto",
            clave_nombre="nombre",
        ).construir()
