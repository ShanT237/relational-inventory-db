import re
import shutil
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from dominio.entidades.reporte import Reporte
from servicios.generador_pdf import generar_pdf

try:
    from pypdf import PdfReader
except ImportError:          # el texto del PDF solo se verifica si pypdf está instalado
    PdfReader = None

AHORA = datetime(2026, 10, 25, 14, 30, 5)


def _reporte(filas, **extra):
    return Reporte(clave="prueba", titulo="Reporte de prueba",
                   filtros=[("Proveedor", "Lácteos del Año (900123456-7)")],
                   columnas=["Código", "Descripción"], filas=filas, **extra)


class GeneradorPdfTest(unittest.TestCase):

    def setUp(self):
        self.carpeta = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.carpeta, ignore_errors=True)

    def _texto(self, ruta):
        return "\n".join(p.extract_text() for p in PdfReader(str(ruta)).pages)

    def test_crea_un_pdf_valido_con_nombre_de_clave_y_fecha(self):
        ruta = generar_pdf(_reporte([("A-1", "Leche")]), "María (mperez)",
                           carpeta=self.carpeta, ahora=AHORA)
        self.assertEqual(ruta.name, "prueba_20261025_143005.pdf")
        self.assertTrue(ruta.read_bytes().startswith(b"%PDF"))

    def test_crea_la_carpeta_si_no_existe(self):
        destino = self.carpeta / "nueva" / "reportes"
        ruta = generar_pdf(_reporte([("A-1", "x")]), "u", carpeta=destino, ahora=AHORA)
        self.assertTrue(ruta.exists())

    def test_texto_con_caracteres_de_marcado_no_rompe_el_pdf(self):
        ruta = generar_pdf(_reporte([("A&B", "<b>Dulces</b> & <S.A.>")]), "u",
                           carpeta=self.carpeta, ahora=AHORA)
        self.assertTrue(ruta.read_bytes().startswith(b"%PDF"))

    @unittest.skipIf(PdfReader is None, "pypdf no está instalado")
    def test_tildes_y_enie_se_leen_bien(self):
        ruta = generar_pdf(_reporte([("A-1", "Ácido úrico ñandú öü")]), "María Núñez (mnunez)",
                           carpeta=self.carpeta, ahora=AHORA)
        texto = self._texto(ruta)
        for esperado in ("Ácido úrico ñandú öü", "Lácteos del Año", "Gestión de Proveedores",
                         "María Núñez (mnunez)"):
            self.assertIn(esperado, texto)

    @unittest.skipIf(PdfReader is None, "pypdf no está instalado")
    def test_pie_con_fecha_hora_usuario_y_numero_de_pagina(self):
        filas = [(f"A-{i}", "x") for i in range(150)]
        ruta = generar_pdf(_reporte(filas), "mperez", carpeta=self.carpeta, ahora=AHORA)
        paginas = PdfReader(str(ruta)).pages
        self.assertGreater(len(paginas), 1)
        ultima = paginas[-1].extract_text()
        self.assertIn(f"Página {len(paginas)} de {len(paginas)}", ultima)
        self.assertIn("Generado el 25/10/2026 a las 14:30:05 por mperez", ultima)
        self.assertIn("Código", ultima)           # la cabecera de la tabla se repite

    @unittest.skipIf(PdfReader is None, "pypdf no está instalado")
    def test_sin_filas_muestra_un_mensaje_y_none_se_ve_como_raya(self):
        vacio = generar_pdf(_reporte([]), "u", carpeta=self.carpeta, ahora=AHORA)
        self.assertIn("Sin registros para los filtros aplicados.", self._texto(vacio))
        con_none = Reporte("nulos", "T", [], ["A", "B"], [("x", None)])
        ruta = generar_pdf(con_none, "u", carpeta=self.carpeta, ahora=AHORA)
        texto = self._texto(ruta)
        self.assertIn("—", texto)
        self.assertIn("Sin filtros.", texto)

    def test_clave_con_caracteres_raros_no_afecta_el_nombre_del_archivo(self):
        reporte = Reporte("a/b c", "T", [], ["A"], [("x",)])
        ruta = generar_pdf(reporte, "u", carpeta=self.carpeta, ahora=AHORA)
        self.assertTrue(re.fullmatch(r"a_b_c_\d{8}_\d{6}\.pdf", ruta.name))


if __name__ == "__main__":
    unittest.main()
