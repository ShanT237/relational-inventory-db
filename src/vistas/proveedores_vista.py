"""Vista: CRUD de proveedores (Tkinter). No contiene SQL."""
from vistas.crud_base import Campo, Columna, CrudVista


class ProveedoresVista:

    def __init__(self, proveedor_controlador, ciudad_controlador):
        self.controlador = proveedor_controlador
        self.ciudad_controlador = ciudad_controlador

    def construir(self, contenedor):
        c = self.controlador

        def cargar():
            return [{"id": x.id_proveedor, "nit": x.nit, "nombre": x.nombre,
                     "ciudad": x.ciudad, "id_ciudad": x.id_ciudad,
                     "direccion": x.direccion or "", "telefono": x.telefono or "",
                     "correo": x.correo or "", "estado": x.estado,
                     "estado_texto": "Activo" if x.estado else "Inactivo"}
                    for x in c.listar()]

        def ciudades():
            return [(x.id_ciudad, f"{x.nombre} ({x.departamento})")
                    for x in self.ciudad_controlador.listar()]

        def datos(v):
            return (v["nit"], v["nombre"], v["id_ciudad"], v["direccion"],
                    v["telefono"], v["correo"], v["estado"])

        CrudVista(
            contenedor,
            subtitulo="Empresas a las que se pueden hacer pedidos de productos.",
            columnas=[Columna("nit", "NIT", 110),
                      Columna("nombre", "Nombre", 200),
                      Columna("ciudad", "Ciudad", 160),
                      Columna("telefono", "Teléfono", 110),
                      Columna("correo", "Correo", 170),
                      Columna("estado_texto", "Estado", 80, True)],
            campos=[Campo("nit", "NIT", obligatorio=True, max_largo=12,
                          ayuda="9 o 10 dígitos y, si quieres, el dígito de verificación. "
                                "Ej: 900123456-7"),
                    Campo("nombre", "Nombre o razón social", obligatorio=True, max_largo=200),
                    Campo("id_ciudad", "Ciudad", tipo="combo", opciones=ciudades,
                          obligatorio=True),
                    Campo("direccion", "Dirección", obligatorio=True, max_largo=200,
                          ayuda="Ej: Calle 15 # 12-30"),
                    Campo("telefono", "Teléfono", obligatorio=True, solo_digitos=True,
                          max_largo=10, ayuda="10 dígitos, solo números. Ej: 3101234567"),
                    Campo("correo", "Correo electrónico", obligatorio=True, max_largo=100,
                          ayuda="Ej: ventas@empresa.com"),
                    Campo("estado", "Activo", tipo="check")],
            cargar=cargar,
            crear=lambda v: c.crear(*datos(v)),
            modificar=lambda i, v: c.modificar(i, *datos(v)),
            eliminar=c.eliminar,
            texto_nuevo="Nuevo proveedor",
            texto_editar="Editar proveedor",
        ).construir()
