"""Vista: pantalla de filtros de un reporte en PDF (Tkinter). No contiene SQL.

Cada reporte del menú «Reportes» abre esta misma pantalla con sus propios filtros
(listas desplegables). Al generar, el PDF se guarda en la carpeta reportes/ y se abre."""
import os
import subprocess
import sys
from dataclasses import dataclass
from tkinter import messagebox, ttk
from typing import Callable, List

from dominio.excepciones.regla_dominio_error import ReglaDominioError
from vistas import estilos as e


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
        self.combos = {}        # clave del filtro -> (combobox, {texto: valor})

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
            self.combos[filtro.clave] = (combo, a_valor)

        self.lbl_mensaje = ttk.Label(cuerpo, text="", style="Error.Tarjeta.TLabel",
                                     wraplength=420, justify="left")
        self.lbl_mensaje.pack(anchor="w", pady=(14, 0))
        self.btn_generar = ttk.Button(cuerpo, text="Generar PDF", style="Primario.TButton",
                                      command=self._generar)
        self.btn_generar.pack(fill="x", pady=(8, 0))

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

    def _generar(self):
        filtros = {clave: a_valor.get(combo.get())     # sin elegir -> None
                   for clave, (combo, a_valor) in self.combos.items()}
        self._mensaje("")
        self.btn_generar.state(["disabled"])
        self.ventana.update_idletasks()
        try:
            ruta = self.controlador.generar(self.definicion.clave, filtros)
        except ReglaDominioError as error:
            self._mensaje(str(error), error=True)
            return
        except Exception as error:
            messagebox.showerror("Reportes", f"No se pudo generar el PDF:\n{error}",
                                 parent=self.ventana)
            return
        finally:
            self.btn_generar.state(["!disabled"])
        if abrir_archivo(ruta):
            self._mensaje(f"PDF generado: {ruta.name}\nCarpeta: {ruta.parent}")
        else:
            self._mensaje(f"PDF generado, pero no se pudo abrir automáticamente.\n{ruta}")
