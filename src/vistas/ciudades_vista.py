"""Vista: CRUD de ciudades (Tkinter). No contiene SQL."""
from vistas.crud_base import Campo, Columna, CrudVista


class CiudadesVista:

    def __init__(self, ciudad_controlador):
        self.controlador = ciudad_controlador

    def construir(self, contenedor):
        c = self.controlador

        def cargar():
            return [{"id": x.id_ciudad, "nombre": x.nombre, "departamento": x.departamento}
                    for x in c.listar()]

        CrudVista(
            contenedor,
            subtitulo="Ciudades de Colombia donde se ubican los proveedores.",
            columnas=[Columna("id", "Id", 60, True),
                      Columna("nombre", "Nombre", 260),
                      Columna("departamento", "Departamento", 260)],
            campos=[Campo("nombre", "Nombre", obligatorio=True),
                    Campo("departamento", "Departamento", obligatorio=True)],
            cargar=cargar,
            crear=lambda v: c.crear(v["nombre"], v["departamento"]),
            modificar=lambda i, v: c.modificar(i, v["nombre"], v["departamento"]),
            eliminar=c.eliminar,
            texto_nuevo="Nueva ciudad",
            texto_editar="Editar ciudad",
            tiene_estado=False,
        ).construir()
