"""Vista: pantalla de filtros de un reporte en PDF (Tkinter). No contiene SQL.

Cada reporte del menú «Reportes» abre esta misma pantalla con sus propios filtros
(listas desplegables). «Generar PDF» muestra el PDF como vista previa dentro de la
misma ventana; «Descargar» abre «Guardar como…», guarda el archivo y lo abre."""
import base64
import os
import shutil
import subprocess
import sys
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Callable, List

from dominio.excepciones.regla_dominio_error import ReglaDominioError
from vistas import estilos as e

try:
    import fitz            # PyMuPDF: convierte las páginas del PDF en imágenes
except ImportError:
    fitz = None

# <raíz del proyecto>/reportes (este archivo está en <raíz>/src/vistas/)
CARPETA_REPORTES = Path(__file__).resolve().parents[2] / "reportes"


@dataclass
class Filtro:
    clave: str                         # nombre del filtro que recibe el servicio
    etiqueta: str
    opciones: Callable                 # devuelve [(valor, texto)]
    valor_inicial: object = None       # valor que aparece elegido al abrir (None = ninguno)


@dataclass
class DefinicionReporte:
    clave: str                         # identifica el reporte en el servicio
    titulo: str
    descripcion: str
    filtros: List[Filtro]


def definiciones(proveedor_controlador, ciudad_controlador, producto_controlador,
                 categoria_controlador):
    """Los 5 reportes, en el orden en que aparecen en el menú."""

    def proveedores():
        return [(x.id_proveedor, f"{x.nombre} ({x.nit})" + ("" if x.estado else " (inactivo)"))
                for x in proveedor_controlador.listar()]

    def ubicaciones():
        ciudades = ciudad_controlador.listar()
        departamentos = sorted({c.departamento for c in ciudades})
        return ([(("departamento", d), f"Departamento: {d}") for d in departamentos]
                + [(("ciudad", c.id_ciudad), f"Ciudad: {c.nombre} ({c.departamento})")
                   for c in ciudades])

    def productos():
        return [(x.id_producto, f"{x.codigo} · {x.nombre}" + ("" if x.estado else " (inactivo)"))
                for x in producto_controlador.listar()]

    def categorias():
        return [(x.id_categoria, x.nombre + ("" if x.estado else " (inactiva)"))
                for x in categoria_controlador.listar()]

    def estados():
        return [("todos", "Todos"), ("activos", "Solo activos"), ("inactivos", "Solo inactivos")]

    return [
        DefinicionReporte("productos_proveedor", "Productos de un proveedor",
                          "PDF filtrado por proveedor.",
                          [Filtro("id_proveedor", "Proveedor", proveedores)]),
        DefinicionReporte("proveedores_ciudad", "Proveedores por ciudad",
                          "PDF filtrado por ciudad o departamento.",
                          [Filtro("ubicacion", "Ciudad o departamento", ubicaciones)]),
        DefinicionReporte("proveedores_producto", "Proveedores de un producto",
                          "PDF con proveedores y precios de un producto.",
                          [Filtro("id_producto", "Producto", productos)]),
        DefinicionReporte("productos_categoria", "Productos de una categoría",
                          "PDF con los productos de una categoría.",
                          [Filtro("id_categoria", "Categoría", categorias)]),
        DefinicionReporte("conteo_categorias", "Cantidad de productos por categoría",
                          "PDF con totales, filtrado por estado.",
                          [Filtro("estado", "Estado de los productos", estados, "todos")]),
    ]


def abrir_archivo(ruta):
    """Abre el archivo con el programa predeterminado del sistema. False si no se pudo."""
    try:
        if sys.platform == "win32":
            os.startfile(ruta)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(ruta)])
        else:
            subprocess.Popen(["xdg-open", str(ruta)])
        return True
    except OSError:
        return False


class ReportesVista:

    def __init__(self, reporte_controlador, definicion):
        self.controlador = reporte_controlador
        self.definicion = definicion
        self.combos = {}            # clave del filtro -> (combobox, {texto: valor})
        self.ruta_previa = None     # PDF temporal que se está mostrando (None = ninguno)
        self.lienzo = None
        self.imagenes = []          # referencias a las imágenes (si no, Tk las borra)
        self._ancho_dibujado = 0
        self._pendiente = None

    def construir(self, contenedor):
        self.ventana = contenedor.winfo_toplevel()    # solo para cuadros de diálogo
        ttk.Label(contenedor, text=self.definicion.titulo, style="Pagina.TLabel").pack(anchor="w")
        ttk.Label(contenedor, text=f"{self.definicion.descripcion} Elige los filtros y "
                                   "genera el reporte.", style="Suave.TLabel").pack(
            anchor="w", pady=(4, 16))

        tarjeta = e.tarjeta(contenedor)
        tarjeta.pack(anchor="w")
        cuerpo = ttk.Frame(tarjeta, style="Tarjeta.TFrame", padding=(26, 22))
        cuerpo.pack()
        ttk.Label(cuerpo, text="Filtros", style="Seccion.Tarjeta.TLabel").pack(anchor="w")

        for filtro in self.definicion.filtros:
            ttk.Label(cuerpo, text=filtro.etiqueta + " *", style="Campo.Tarjeta.TLabel").pack(
                anchor="w", pady=(14, 4))
            combo, a_valor = self._crear_combo(cuerpo, filtro)
            # Si cambia un filtro, la vista previa ya no corresponde: se quita.
            combo.bind("<<ComboboxSelected>>", lambda _ev: self._limpiar_vista_previa())
            self.combos[filtro.clave] = (combo, a_valor)

        self.lbl_mensaje = ttk.Label(cuerpo, text="", style="Error.Tarjeta.TLabel",
                                     wraplength=420, justify="left")
        self.lbl_mensaje.pack(anchor="w", pady=(14, 0))
        self.btn_generar = ttk.Button(cuerpo, text="Generar PDF", style="Primario.TButton",
                                      command=self._generar)
        self.btn_generar.pack(fill="x", pady=(8, 0))

        # Zona de la vista previa: ocupa el resto de la ventana, debajo de los filtros
        self.zona_previa = ttk.Frame(contenedor)
        self.zona_previa.pack(fill="both", expand=True, pady=(16, 0))

    def _crear_combo(self, padre, filtro):
        try:
            pares = filtro.opciones()
        except Exception as error:
            pares = []
            messagebox.showerror(
                "Reportes", f"No se pudieron cargar las opciones de «{filtro.etiqueta}»:\n{error}",
                parent=self.ventana)
        a_valor = {texto: valor for valor, texto in pares}
        combo = ttk.Combobox(padre, state="readonly", width=52, values=[t for _, t in pares])
        combo.pack(fill="x")
        if filtro.valor_inicial is not None:
            texto = next((t for v, t in pares if v == filtro.valor_inicial), "")
            combo.set(texto)
        return combo, a_valor

    def _mensaje(self, texto, error=False):
        self.lbl_mensaje.config(
            text=texto, style="Error.Tarjeta.TLabel" if error else "Exito.Tarjeta.TLabel")

    # ------------------------------------------------------------- vista previa
    def _limpiar_vista_previa(self):
        if self._pendiente is not None:
            self.zona_previa.after_cancel(self._pendiente)
            self._pendiente = None
        self.ruta_previa = None
        self.lienzo = None
        self.imagenes = []
        for widget in self.zona_previa.winfo_children():
            widget.destroy()

    def _mostrar_vista_previa(self, ruta):
        """Dibuja el PDF dentro de la ventana y el botón «Descargar»."""
        self._limpiar_vista_previa()
        self.ruta_previa = ruta

        barra = ttk.Frame(self.zona_previa)
        barra.pack(fill="x", pady=(0, 8))
        ttk.Label(barra, text="Vista previa", style="Pagina.TLabel",
                  font=e.FUENTE_SECCION).pack(side="left")
        self.btn_descargar = ttk.Button(barra, text="Descargar", style="Primario.TButton",
                                        command=self._descargar)
        self.btn_descargar.pack(side="right")

        marco = e.tarjeta(self.zona_previa)
        marco.pack(fill="both", expand=True)
        self.lienzo = tk.Canvas(marco, bg="#475569", highlightthickness=0, borderwidth=0)
        scroll = ttk.Scrollbar(marco, orient="vertical", command=self.lienzo.yview)
        self.lienzo.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.lienzo.pack(side="left", fill="both", expand=True)

        def rueda(ev):
            if self.lienzo is not None:
                self.lienzo.yview_scroll(-1 * (ev.delta // 120), "units")

        self.lienzo.bind("<Enter>", lambda _ev: self.lienzo.bind_all("<MouseWheel>", rueda))
        self.lienzo.bind("<Leave>", lambda _ev: self.lienzo.unbind_all("<MouseWheel>"))
        self.lienzo.bind("<Destroy>", lambda _ev: self.lienzo.unbind_all("<MouseWheel>"))
        self.lienzo.bind("<Configure>", self._al_cambiar_tamano)

        self.zona_previa.update_idletasks()
        self._dibujar_paginas()

    def _al_cambiar_tamano(self, _evento=None):
        """Si cambia el ancho de la ventana, se vuelve a dibujar el PDF ajustado."""
        if self._pendiente is not None:
            self.zona_previa.after_cancel(self._pendiente)
        self._pendiente = self.zona_previa.after(250, self._redibujar)

    def _redibujar(self):
        self._pendiente = None
        if self.lienzo is not None and self.lienzo.winfo_exists():
            if abs(self.lienzo.winfo_width() - self._ancho_dibujado) > 20:
                self._dibujar_paginas()

    def _dibujar_paginas(self):
        """Convierte cada página del PDF en imagen, ajustada al ancho disponible."""
        if fitz is None:
            self._mensaje("Falta la librería PyMuPDF. Instálala con: pip install pymupdf",
                          error=True)
            return
        lienzo = self.lienzo
        self._ancho_dibujado = lienzo.winfo_width()
        ancho = max(self._ancho_dibujado - 40, 300)
        lienzo.delete("all")
        self.imagenes = []
        y = 20
        documento = fitz.open(str(self.ruta_previa))
        try:
            for pagina in documento:
                zoom = ancho / pagina.rect.width
                pix = pagina.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
                imagen = tk.PhotoImage(data=base64.b64encode(pix.tobytes("png")))
                self.imagenes.append(imagen)
                lienzo.create_image((self._ancho_dibujado - pix.width) // 2, y,
                                    anchor="nw", image=imagen)
                y += pix.height + 20
        finally:
            documento.close()
        lienzo.configure(scrollregion=(0, 0, self._ancho_dibujado, y))
        lienzo.yview_moveto(0)

    # ------------------------------------------------------------------ acciones
    def _generar(self):
        filtros = {clave: a_valor.get(combo.get())     # sin elegir -> None
                   for clave, (combo, a_valor) in self.combos.items()}
        self._mensaje("")
        self._limpiar_vista_previa()
        self.btn_generar.state(["disabled"])
        self.ventana.update_idletasks()
        try:
            ruta = self.controlador.previsualizar(self.definicion.clave, filtros)
        except ReglaDominioError as error:
            self._mensaje(str(error), error=True)
            return
        except Exception as error:
            messagebox.showerror("Reportes", f"No se pudo generar el PDF:\n{error}",
                                 parent=self.ventana)
            return
        finally:
            self.btn_generar.state(["!disabled"])
        self._mostrar_vista_previa(ruta)

    def _descargar(self):
        """«Guardar como…»: copia el PDF de la vista previa donde elija el usuario."""
        if self.ruta_previa is None:
            return
        CARPETA_REPORTES.mkdir(parents=True, exist_ok=True)
        destino = filedialog.asksaveasfilename(
            parent=self.ventana, title="Guardar reporte como…",
            defaultextension=".pdf", filetypes=[("Archivo PDF", "*.pdf")],
            initialdir=str(CARPETA_REPORTES), initialfile=self.ruta_previa.name)
        if not destino:                      # canceló el cuadro
            return
        try:
            shutil.copyfile(self.ruta_previa, destino)
        except OSError as error:
            messagebox.showerror("Reportes", f"No se pudo guardar el PDF:\n{error}",
                                 parent=self.ventana)
            return
        destino = Path(destino)
        if abrir_archivo(destino):
            self._mensaje(f"PDF guardado: {destino.name}\nCarpeta: {destino.parent}")
        else:
            self._mensaje(f"PDF guardado, pero no se pudo abrir automáticamente.\n{destino}")