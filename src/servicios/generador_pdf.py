"""Módulo común de reportes en PDF (reportlab).

Cada PDF lleva: encabezado con el nombre de la aplicación, título, filtros aplicados,
tabla de datos y pie con fecha, hora, usuario y número de página ("Página x de y").
Usa las fuentes estándar de PDF (Helvetica), que incluyen tildes, ñ y diéresis."""
import re
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from dominio.entidades.reporte import Reporte

NOMBRE_APLICACION = "Sistema de Gestión de Proveedores y Productos"
# Carpeta <raíz del proyecto>/reportes (este archivo está en <raíz>/src/servicios/)
CARPETA_REPORTES = Path(__file__).resolve().parents[2] / "reportes"

_TINTA = colors.HexColor("#0F172A")
_AZUL = colors.HexColor("#2563EB")
_GRIS = colors.HexColor("#64748B")
_BORDE = colors.HexColor("#CBD5E1")
_FILA_IMPAR = colors.HexColor("#F8FAFC")
_MARGEN = 1.5 * cm
_PAGINA = landscape(A4)

_TITULO = ParagraphStyle("titulo", fontName="Helvetica-Bold", fontSize=16, leading=20,
                         textColor=_TINTA, spaceAfter=6)
_SUBTITULO = ParagraphStyle("subtitulo", fontName="Helvetica-Bold", fontSize=9, leading=12,
                            textColor=_GRIS, spaceAfter=2)
_FILTRO = ParagraphStyle("filtro", fontName="Helvetica", fontSize=10, leading=14,
                         textColor=_TINTA)
_CELDA = ParagraphStyle("celda", fontName="Helvetica", fontSize=8.5, leading=11,
                        textColor=_TINTA)
_CELDA_DERECHA = ParagraphStyle("celda_derecha", parent=_CELDA, alignment=2)
_CABECERA = ParagraphStyle("cabecera", parent=_CELDA, fontName="Helvetica-Bold",
                           textColor=colors.white)
_CABECERA_DERECHA = ParagraphStyle("cabecera_derecha", parent=_CABECERA, alignment=2)


class _LienzoNumerado(canvas.Canvas):
    """Lienzo que dibuja el pie de página al final, cuando ya se sabe el total de páginas."""
    pie = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._estados = []

    def showPage(self):
        self._estados.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._estados)
        for estado in self._estados:
            self.__dict__.update(estado)
            self._dibujar_pie(total)
            super().showPage()
        super().save()

    def _dibujar_pie(self, total):
        ancho, _ = _PAGINA
        self.saveState()
        self.setStrokeColor(_BORDE)
        self.line(_MARGEN, 1.3 * cm, ancho - _MARGEN, 1.3 * cm)
        self.setFont("Helvetica", 8)
        self.setFillColor(_GRIS)
        self.drawString(_MARGEN, 0.8 * cm, self.pie)
        self.drawRightString(ancho - _MARGEN, 0.8 * cm, f"Página {self._pageNumber} de {total}")
        self.restoreState()


def _lienzo_con_pie(texto_pie):
    class Lienzo(_LienzoNumerado):
        pie = texto_pie
    return Lienzo


def _encabezado(lienzo, _doc):
    ancho, alto = _PAGINA
    lienzo.saveState()
    lienzo.setFillColor(_AZUL)
    lienzo.rect(0, alto - 0.45 * cm, ancho, 0.45 * cm, stroke=0, fill=1)
    lienzo.setFillColor(_TINTA)
    lienzo.setFont("Helvetica-Bold", 11)
    lienzo.drawString(_MARGEN, alto - 1.15 * cm, NOMBRE_APLICACION)
    lienzo.setFillColor(_GRIS)
    lienzo.setFont("Helvetica", 9)
    lienzo.drawRightString(ancho - _MARGEN, alto - 1.15 * cm,
                           "Bases de Datos I · Universidad del Quindío")
    lienzo.setStrokeColor(_BORDE)
    lienzo.line(_MARGEN, alto - 1.45 * cm, ancho - _MARGEN, alto - 1.45 * cm)
    lienzo.restoreState()


def _texto(valor):
    if valor is None:
        return "—"
    if hasattr(valor, "strftime"):
        return valor.strftime("%d/%m/%Y %H:%M:%S")
    return str(valor)


def _celda(valor, estilo):
    # Paragraph interpreta marcado XML: se escapan &, < y > para que no rompan el PDF.
    return Paragraph(escape(_texto(valor)).replace("\n", "<br/>"), estilo)


def _tabla(reporte, ancho_util):
    if not reporte.filas:
        mensaje = Table([[Paragraph("Sin registros para los filtros aplicados.", _FILTRO)]],
                        colWidths=[ancho_util])
        mensaje.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.5, _BORDE),
                                     ("TOPPADDING", (0, 0), (-1, -1), 10),
                                     ("BOTTOMPADDING", (0, 0), (-1, -1), 10)]))
        return mensaje

    derecha = set(reporte.a_la_derecha)
    datos = [[_celda(c, _CABECERA_DERECHA if i in derecha else _CABECERA)
              for i, c in enumerate(reporte.columnas)]]
    for fila in reporte.filas:
        datos.append([_celda(v, _CELDA_DERECHA if i in derecha else _CELDA)
                      for i, v in enumerate(fila)])

    pesos = reporte.anchos or [1] * len(reporte.columnas)
    anchos = [ancho_util * p / sum(pesos) for p in pesos]
    tabla = Table(datos, colWidths=anchos, repeatRows=1)    # la cabecera se repite en cada página
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), _AZUL),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, _FILA_IMPAR]),
        ("LINEBELOW", (0, 0), (-1, -1), 0.25, _BORDE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return tabla


def generar_pdf(reporte: Reporte, usuario: str, carpeta=None, ahora=None) -> Path:
    """Crea el PDF del reporte en 'carpeta' (por defecto <raíz>/reportes) y devuelve su ruta."""
    ahora = ahora or datetime.now()
    carpeta = Path(carpeta) if carpeta else CARPETA_REPORTES
    carpeta.mkdir(parents=True, exist_ok=True)
    clave = re.sub(r"[^A-Za-z0-9_-]", "_", reporte.clave)
    ruta = carpeta / f"{clave}_{ahora:%Y%m%d_%H%M%S}.pdf"

    ancho, _ = _PAGINA
    ancho_util = ancho - 2 * _MARGEN
    historia = [Paragraph(escape(reporte.titulo), _TITULO),
                Paragraph("FILTROS APLICADOS", _SUBTITULO)]
    if reporte.filtros:
        for etiqueta, valor in reporte.filtros:
            historia.append(Paragraph(f"<b>{escape(etiqueta)}:</b> {escape(str(valor))}", _FILTRO))
    else:
        historia.append(Paragraph("Sin filtros.", _FILTRO))
    historia += [Spacer(1, 12), _tabla(reporte, ancho_util)]

    pie = f"Generado el {ahora:%d/%m/%Y} a las {ahora:%H:%M:%S} por {usuario}"
    documento = SimpleDocTemplate(
        str(ruta), pagesize=_PAGINA, leftMargin=_MARGEN, rightMargin=_MARGEN,
        topMargin=2.2 * cm, bottomMargin=1.9 * cm,
        title=reporte.titulo, author=usuario, subject=NOMBRE_APLICACION)
    documento.build(historia, onFirstPage=_encabezado, onLaterPages=_encabezado,
                    canvasmaker=_lienzo_con_pie(pie))
    return ruta
