"""Vista: CRUD de categorías (Tkinter). No contiene SQL."""
from vistas.crud_base import Campo, Columna, CrudVista


class CategoriasVista:

    def __init__(self, padre, categoria_controlador):
        self.padre = padre
        self.controlador = categoria_controlador

    def mostrar(self):
        c = self.controlador

        def cargar():
            return [{"id": x.id_categoria, "nombre": x.nombre,
                     "descripcion": x.descripcion or "", "estado": x.estado,
                     "estado_texto": "Activa" if x.estado else "Inactiva"}
                    for x in c.listar()]

        CrudVista(
            self.padre,
            titulo="Categorías",
            subtitulo="Familias en las que se clasifican los productos.",
            columnas=[Columna("id", "Id", 60, True),
                      Columna("nombre", "Nombre", 200),
                      Columna("descripcion", "Descripción", 320),
                      Columna("estado_texto", "Estado", 90, True)],
            campos=[Campo("nombre", "Nombre", obligatorio=True),
                    Campo("descripcion", "Descripción", tipo="area"),
                    Campo("estado", "Activa", tipo="check")],
            cargar=cargar,
            crear=lambda v: c.crear(v["nombre"], v["descripcion"], v["estado"]),
            modificar=lambda i, v: c.modificar(i, v["nombre"], v["descripcion"], v["estado"]),
            eliminar=c.eliminar,
            texto_nuevo="Nueva categoría",
            texto_editar="Editar categoría",
            tamano=(1050, 640),
        ).mostrar()
