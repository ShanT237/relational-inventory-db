import unittest
from decimal import Decimal

from dominio.entidades.sesion import Sesion
from dominio.excepciones.regla_dominio_error import ReglaDominioError
from servicios.reporte_servicio import ReporteServicio


class RepositorioFalso:
    """Guarda con qué argumentos lo llamó el servicio y devuelve datos fijos."""

    def __init__(self):
        self.llamadas = []
        self.proveedor = ("Lácteos del Sur", "900123456-7")
        self.producto = ("LAC-001", "Leche entera")
        self.categoria = ("Lácteos",)
        self.ciudad = ("Armenia", "Quindío")
        self.filas = []

    def obtener_proveedor(self, i): return self.proveedor
    def obtener_producto(self, i): return self.producto
    def obtener_categoria(self, i): return self.categoria
    def obtener_ciudad(self, i): return self.ciudad

    def productos_de_proveedor(self, i): return self.filas
    def proveedores_de_producto(self, i): return self.filas
    def productos_de_categoria(self, i): return self.filas

    def proveedores_por_ubicacion(self, id_ciudad=None, departamento=None):
        self.llamadas.append(("ubicacion", id_ciudad, departamento))
        return self.filas

    def cantidad_por_categoria(self, activo=None):
        self.llamadas.append(("cantidad", activo))
        return self.filas


def _sesion(rol="Tradicional"):
    return Sesion(1, "mperez", "María Pérez", rol, 10)


class ReporteServicioTest(unittest.TestCase):

    def setUp(self):
        self.repo = RepositorioFalso()
        self.creados = []
        self.servicio = ReporteServicio(self.repo, self._generador)

    def _generador(self, reporte, usuario):
        self.creados.append((reporte, usuario))
        return "ruta.pdf"

    # ------------------------------------------------------------- permisos
    def test_esporadico_no_puede_generar_reportes(self):
        with self.assertRaises(ReglaDominioError):
            self.servicio.generar(_sesion("Esporadico"), "conteo_categorias", {"estado": "todos"})
        self.assertEqual(self.creados, [])

    def test_sin_sesion_no_genera(self):
        with self.assertRaises(ReglaDominioError):
            self.servicio.generar(None, "conteo_categorias", {"estado": "todos"})

    def test_reporte_inexistente(self):
        with self.assertRaisesRegex(ReglaDominioError, "no existe"):
            self.servicio.construir(_sesion(), "otro", {})

    # ----------------------------------------------------------- generación
    def test_generar_pasa_el_reporte_y_el_usuario_al_generador(self):
        ruta = self.servicio.generar(_sesion("Administrador"), "conteo_categorias",
                                     {"estado": "todos"})
        self.assertEqual(ruta, "ruta.pdf")
        reporte, usuario = self.creados[0]
        self.assertEqual(reporte.clave, "conteo_categorias")
        self.assertEqual(usuario, "María Pérez (mperez)")

    # ------------------------------------------------- filtros obligatorios
    def test_cada_reporte_exige_su_filtro(self):
        casos = {"productos_proveedor": "Selecciona el proveedor.",
                 "proveedores_ciudad": "Selecciona la ciudad o el departamento.",
                 "proveedores_producto": "Selecciona el producto.",
                 "productos_categoria": "Selecciona la categoría.",
                 "conteo_categorias": "Selecciona el estado de los productos."}
        for clave, mensaje in casos.items():
            with self.subTest(clave):
                with self.assertRaisesRegex(ReglaDominioError, mensaje):
                    self.servicio.construir(_sesion(), clave, {})

    def test_filtro_que_ya_no_existe_en_la_base(self):
        self.repo.proveedor = None
        with self.assertRaisesRegex(ReglaDominioError, "ya no existe"):
            self.servicio.construir(_sesion(), "productos_proveedor", {"id_proveedor": 99})

    # --------------------------------------------------------------- contenido
    def test_productos_de_proveedor_da_formato_a_precio_y_estado(self):
        self.repo.filas = [("LAC-001", "Leche", "Lácteos", "litro", Decimal("1500.5"), 3, True),
                           ("LAC-002", "Queso", "Lácteos", "kg", Decimal("12000"), 0, False)]
        r = self.servicio.construir(_sesion(), "productos_proveedor", {"id_proveedor": 1})
        self.assertEqual(r.filtros, [("Proveedor", "Lácteos del Sur (900123456-7)")])
        self.assertEqual(r.filas[0], ("LAC-001", "Leche", "Lácteos", "litro", "$ 1.500,50", 3,
                                      "Activo"))
        self.assertEqual(r.filas[1][4:], ("$ 12.000,00", 0, "Inactivo"))
        self.assertTrue(all(len(f) == len(r.columnas) for f in r.filas))

    def test_proveedores_por_ciudad_y_por_departamento(self):
        self.servicio.construir(_sesion(), "proveedores_ciudad", {"ubicacion": ("ciudad", 7)})
        r = self.servicio.construir(_sesion(), "proveedores_ciudad",
                                    {"ubicacion": ("departamento", "Quindío")})
        self.assertEqual(self.repo.llamadas, [("ubicacion", 7, None),
                                              ("ubicacion", None, "Quindío")])
        self.assertEqual(r.filtros, [("Departamento", "Quindío")])

    def test_ubicacion_con_formato_invalido(self):
        for malo in ("Quindío", ("region", "x"), ("ciudad",)):
            with self.subTest(malo):
                with self.assertRaises(ReglaDominioError):
                    self.servicio.construir(_sesion(), "proveedores_ciudad", {"ubicacion": malo})

    def test_proveedor_sin_productos_se_indica_en_el_reporte(self):
        self.repo.filas = [("Quindío", "Armenia", "Café SAS", "900111222", None, None)]
        r = self.servicio.construir(_sesion(), "proveedores_ciudad", {"ubicacion": ("ciudad", 1)})
        self.assertEqual(r.filtros, [("Ciudad", "Armenia (Quindío)")])
        self.assertEqual(r.filas[0][4:], ("Sin productos asignados", None))

    def test_proveedores_de_un_producto_incluye_ciudad_y_precio(self):
        self.repo.filas = [("Lácteos del Sur", "900123456-7", "Armenia", "Quindío",
                            Decimal("1500"), 2, True)]
        r = self.servicio.construir(_sesion(), "proveedores_producto", {"id_producto": 1})
        self.assertEqual(r.filtros, [("Producto", "LAC-001 · Leche entera")])
        self.assertEqual(r.filas[0], ("Lácteos del Sur", "900123456-7", "Armenia (Quindío)",
                                      "$ 1.500,00", 2, "Activo"))

    def test_productos_de_una_categoria(self):
        self.repo.filas = [("LAC-001", "Leche", "litro", "Leche entera pasteurizada", False)]
        r = self.servicio.construir(_sesion(), "productos_categoria", {"id_categoria": 1})
        self.assertEqual(r.filtros, [("Categoría", "Lácteos")])
        self.assertEqual(r.filas[0][-1], "Inactivo")

    def test_conteo_por_estado_agrega_total_y_traduce_el_filtro(self):
        self.repo.filas = [("Lácteos", 4), ("Granos", 0), ("Bebidas", 6)]
        casos = {"todos": None, "activos": True, "inactivos": False}
        for estado, esperado in casos.items():
            with self.subTest(estado):
                self.repo.llamadas.clear()
                r = self.servicio.construir(_sesion(), "conteo_categorias", {"estado": estado})
                self.assertEqual(self.repo.llamadas, [("cantidad", esperado)])
                self.assertEqual(r.filas[-1], ("TOTAL", 10))
                self.assertIn(("Granos", 0), r.filas)

    def test_conteo_sin_categorias_no_agrega_total(self):
        r = self.servicio.construir(_sesion(), "conteo_categorias", {"estado": "todos"})
        self.assertEqual(r.filas, [])

    def test_estado_desconocido_se_rechaza(self):
        with self.assertRaises(ReglaDominioError):
            self.servicio.construir(_sesion(), "conteo_categorias", {"estado": "borrados"})

    def test_filtros_none_no_rompe(self):
        with self.assertRaises(ReglaDominioError):
            self.servicio.construir(_sesion(), "productos_proveedor", None)


if __name__ == "__main__":
    unittest.main()
