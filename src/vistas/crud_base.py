"""Vista base reutilizable para los CRUD (Tkinter). No contiene SQL.

Cada módulo (ciudades, categorías, proveedores, productos) solo declara sus
columnas, sus campos y qué hacer al cargar/crear/modificar/eliminar; el diseño y
el comportamiento (búsqueda, filtro, orden, formulario) viven aquí."""
import tkinter as tk
from dataclasses import dataclass
from tkinter import messagebox, ttk
from typing import Callable, Optional

from dominio.excepciones.regla_dominio_error import ReglaDominioError
from vistas import estilos as e


@dataclass
class Columna:
    clave: str
    titulo: str
    ancho: int = 120
    centrado: bool = False


@dataclass
class Campo:
    clave: str
    etiqueta: str
    tipo: str = "texto"            # texto | area | combo | combo_texto | check
    opciones: Optional[Callable] = None   # combo: [(id, texto)]; combo_texto: [texto]
    obligatorio: bool = False


def _clave_orden(valor):
    texto = "" if valor is None else str(valor)
    return (0, int(texto), "") if texto.isdigit() else (1, 0, texto.lower())


class CrudVista:

    def __init__(self, padre, titulo, subtitulo, columnas, campos, cargar, crear,
                 modificar, eliminar, texto_nuevo, texto_editar, tamano=(1100, 680),
                 tiene_estado=True, clave_nombre="nombre"):
        """cargar() -> lista de dicts con la clave 'id' (y 'estado' si tiene_estado).
        crear(valores) / modificar(id, valores) / eliminar(id) llaman al controlador."""
        self.padre = padre
        self.titulo = titulo
        self.subtitulo = subtitulo
        self.columnas = columnas
        self.campos = campos
        self.cargar = cargar
        self.crear = crear
        self.modificar = modificar
        self.eliminar = eliminar
        self.texto_nuevo = texto_nuevo
        self.texto_editar = texto_editar
        self.tamano = tamano
        self.tiene_estado = tiene_estado
        self.clave_nombre = clave_nombre

        self.id_seleccionado = None   # None = se está creando un registro nuevo
        self.filas = []
        self.filas_por_id = {}
        self.orden = None             # (clave de columna, descendente)
        self.campos_widgets = {}      # clave -> (obtener, asignar, widget)

    # ------------------------------------------------------------------ ventana
    def mostrar(self):
        v = tk.Toplevel(self.padre)
        self.ventana = v
        v.title(self.titulo)
        v.configure(bg=e.FONDO)
        v.minsize(900, 560)
        e.centrar(v, self.tamano[0], self.tamano[1], self.padre)
        v.transient(self.padre)
        v.grab_set()

        self._construir_encabezado()
        cuerpo = ttk.Frame(v, padding=20)
        cuerpo.pack(fill="both", expand=True)
        cuerpo.columnconfigure(0, weight=1)
        cuerpo.columnconfigure(1, weight=0, minsize=370)
        cuerpo.rowconfigure(0, weight=1)
        self._construir_tabla(cuerpo)
        self._construir_formulario(cuerpo)

        v.bind("<Escape>", lambda _ev: v.destroy())
        v.bind("<Control-s>", lambda _ev: self._guardar())
        v.bind("<Return>", self._al_enter)

        self._recargar()
        self._nuevo()

    def _construir_encabezado(self):
        franja = tk.Frame(self.ventana, bg=e.OSCURO)
        franja.pack(fill="x")
        interior = tk.Frame(franja, bg=e.OSCURO)
        interior.pack(fill="x", padx=24, pady=16)
        ttk.Label(interior, text=self.titulo, style="Encabezado.TLabel").pack(anchor="w")
        ttk.Label(interior, text=self.subtitulo, style="EncabezadoSub.TLabel").pack(
            anchor="w", pady=(2, 0))

    # -------------------------------------------------------------------- tabla
    def _construir_tabla(self, cuerpo):
        izquierda = e.tarjeta(cuerpo)
        izquierda.grid(row=0, column=0, sticky="nsew")

        barra = ttk.Frame(izquierda, style="Tarjeta.TFrame", padding=(16, 14, 16, 10))
        barra.pack(fill="x")
        ttk.Label(barra, text="Buscar", style="Campo.Tarjeta.TLabel").pack(side="left")
        self.var_buscar = tk.StringVar()
        self.entrada_buscar = ttk.Entry(barra, textvariable=self.var_buscar, width=28)
        self.entrada_buscar.pack(side="left", padx=(8, 16))
        self.var_buscar.trace_add("write", lambda *_: self._pintar())

        self.var_estado = tk.StringVar(value="Todos")
        if self.tiene_estado:
            ttk.Label(barra, text="Mostrar", style="Campo.Tarjeta.TLabel").pack(side="left")
            filtro = ttk.Combobox(barra, textvariable=self.var_estado, state="readonly",
                                  values=("Todos", "Activos", "Inactivos"), width=11)
            filtro.pack(side="left", padx=(8, 0))
            filtro.bind("<<ComboboxSelected>>", lambda _ev: self._pintar())

        self.lbl_conteo = ttk.Label(barra, text="", style="Suave.Tarjeta.TLabel")
        self.lbl_conteo.pack(side="right")

        marco = tk.Frame(izquierda, bg=e.TARJETA)
        marco.pack(fill="both", expand=True, padx=1, pady=(0, 1))
        self.tabla = ttk.Treeview(marco, columns=[c.clave for c in self.columnas],
                                  show="headings", selectmode="browse")
        for c in self.columnas:
            self.tabla.heading(c.clave, text=c.titulo,
                               command=lambda k=c.clave: self._ordenar(k))
            self.tabla.column(c.clave, width=c.ancho, minwidth=50,
                              anchor="center" if c.centrado else "w")
        scroll = ttk.Scrollbar(marco, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.tabla.tag_configure("par", background=e.TARJETA)
        self.tabla.tag_configure("impar", background=e.FILA_IMPAR)
        self.tabla.tag_configure("inactivo", foreground="#94A3B8")
        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar)

    # --------------------------------------------------------------- formulario
    def _construir_formulario(self, cuerpo):
        derecha = e.tarjeta(cuerpo)
        derecha.grid(row=0, column=1, sticky="nsew", padx=(16, 0))
        contenido = ttk.Frame(derecha, style="Tarjeta.TFrame", padding=22)
        contenido.pack(fill="both", expand=True)

        self.lbl_modo = ttk.Label(contenido, text="", style="Seccion.Tarjeta.TLabel")
        self.lbl_modo.pack(anchor="w")

        for campo in self.campos:
            if campo.tipo != "check":
                texto = campo.etiqueta + (" *" if campo.obligatorio else "")
                ttk.Label(contenido, text=texto, style="Campo.Tarjeta.TLabel").pack(
                    anchor="w", pady=(12, 4))
            self.campos_widgets[campo.clave] = self._crear_widget(contenido, campo)

        self.lbl_mensaje = ttk.Label(contenido, text="", style="Error.Tarjeta.TLabel",
                                     wraplength=310, justify="left")
        self.lbl_mensaje.pack(anchor="w", pady=(14, 0))

        self.btn_guardar = ttk.Button(contenido, text="Guardar", style="Primario.TButton",
                                      command=self._guardar)
        self.btn_guardar.pack(fill="x", pady=(14, 8))
        fila = ttk.Frame(contenido, style="Tarjeta.TFrame")
        fila.pack(fill="x")
        fila.columnconfigure((0, 1), weight=1, uniform="b")
        ttk.Button(fila, text="Nuevo", command=self._nuevo).grid(
            row=0, column=0, sticky="ew", padx=(0, 4))
        self.btn_eliminar = ttk.Button(fila, text="Eliminar", style="Peligro.TButton",
                                       command=self._eliminar)
        self.btn_eliminar.grid(row=0, column=1, sticky="ew", padx=(4, 0))

    def _crear_widget(self, padre, campo):
        """Crea el control del campo y devuelve (obtener, asignar, widget)."""
        if campo.tipo == "area":
            w = tk.Text(padre, height=4, wrap="word", relief="flat", bg=e.TARJETA,
                        fg=e.TEXTO, font=e.FUENTE, padx=8, pady=6, highlightthickness=1,
                        highlightbackground=e.BORDE_FUERTE, highlightcolor=e.PRIMARIO,
                        insertbackground=e.TEXTO)
            w.pack(fill="x")

            def asignar(valor):
                w.delete("1.0", "end")
                w.insert("1.0", "" if valor is None else str(valor))
            return (lambda: w.get("1.0", "end-1c")), asignar, w

        if campo.tipo == "combo":
            pares = campo.opciones() if campo.opciones else []
            a_id = {texto: id_ for id_, texto in pares}
            a_texto = {id_: texto for id_, texto in pares}
            w = ttk.Combobox(padre, state="readonly", values=[t for _, t in pares])
            w.pack(fill="x")
            return ((lambda: a_id.get(w.get())),
                    (lambda valor: w.set(a_texto.get(valor, ""))), w)

        if campo.tipo == "combo_texto":
            w = ttk.Combobox(padre, values=list(campo.opciones() if campo.opciones else []))
            w.pack(fill="x")
            return w.get, (lambda valor: w.set("" if valor is None else str(valor))), w

        if campo.tipo == "check":
            variable = tk.BooleanVar(value=True)
            w = ttk.Checkbutton(padre, text=campo.etiqueta, variable=variable,
                                style="Tarjeta.TCheckbutton")
            w.pack(anchor="w", pady=(16, 0))
            return variable.get, (lambda valor: variable.set(bool(valor))), w

        w = ttk.Entry(padre)
        w.pack(fill="x")

        def asignar_texto(valor):
            w.delete(0, "end")
            w.insert(0, "" if valor is None else str(valor))
        return w.get, asignar_texto, w

    # ----------------------------------------------------------- datos y tabla
    def _recargar(self):
        try:
            self.filas = self.cargar()
        except Exception as error:
            self.filas = []
            messagebox.showerror("Error", f"No se pudieron cargar los datos:\n{error}",
                                 parent=self.ventana)
        self.filas_por_id = {f["id"]: f for f in self.filas}
        self._pintar()

    def _pintar(self):
        texto = self.var_buscar.get().strip().lower()
        filtro = self.var_estado.get() if self.tiene_estado else "Todos"
        visibles = []
        for f in self.filas:
            activo = f.get("estado", True)
            if filtro == "Activos" and not activo:
                continue
            if filtro == "Inactivos" and activo:
                continue
            if texto and not any(texto in str(f.get(c.clave, "")).lower()
                                 for c in self.columnas):
                continue
            visibles.append(f)
        if self.orden:
            clave, descendente = self.orden
            visibles.sort(key=lambda f: _clave_orden(f.get(clave)), reverse=descendente)

        self.tabla.delete(*self.tabla.get_children())
        for i, f in enumerate(visibles):
            etiquetas = ["par" if i % 2 == 0 else "impar"]
            if not f.get("estado", True):
                etiquetas.append("inactivo")
            self.tabla.insert("", "end", iid=str(f["id"]), tags=etiquetas,
                              values=[f.get(c.clave, "") for c in self.columnas])
        if self.id_seleccionado is not None and self.tabla.exists(str(self.id_seleccionado)):
            self.tabla.selection_set(str(self.id_seleccionado))

        for c in self.columnas:
            flecha = ""
            if self.orden and self.orden[0] == c.clave:
                flecha = "  ▼" if self.orden[1] else "  ▲"
            self.tabla.heading(c.clave, text=c.titulo + flecha)
        self.lbl_conteo.config(text=f"{len(visibles)} de {len(self.filas)} registros")

    def _ordenar(self, clave):
        descendente = bool(self.orden and self.orden[0] == clave and not self.orden[1])
        self.orden = (clave, descendente)
        self._pintar()

    # ----------------------------------------------------------------- acciones
    def _mensaje(self, texto, error=False):
        self.lbl_mensaje.config(
            text=texto, style="Error.Tarjeta.TLabel" if error else "Exito.Tarjeta.TLabel")
        if texto and not error:
            self.ventana.after(3500, self._borrar_mensaje, texto)

    def _borrar_mensaje(self, texto):
        if self.ventana.winfo_exists() and self.lbl_mensaje.cget("text") == texto:
            self.lbl_mensaje.config(text="")

    def _nuevo(self, limpiar_mensaje=True):
        self.id_seleccionado = None
        for campo in self.campos:
            _, asignar, _ = self.campos_widgets[campo.clave]
            asignar(True if campo.tipo == "check" else "")
        self.tabla.selection_remove(self.tabla.selection())
        self.lbl_modo.config(text=self.texto_nuevo)
        self.btn_eliminar.state(["disabled"])
        if limpiar_mensaje:
            self.lbl_mensaje.config(text="")
        primero = self.campos_widgets[self.campos[0].clave][2]
        primero.focus_set()

    def _al_seleccionar(self, _evento=None):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        id_fila = int(seleccion[0])
        if id_fila == self.id_seleccionado:
            return
        fila = self.filas_por_id.get(id_fila)
        if fila is None:
            return
        self.id_seleccionado = id_fila
        for campo in self.campos:
            self.campos_widgets[campo.clave][1](fila.get(campo.clave))
        self.lbl_modo.config(text=self.texto_editar)
        self.btn_eliminar.state(["!disabled"])
        self.lbl_mensaje.config(text="")

    def _guardar(self, _evento=None):
        valores = {clave: obtener() for clave, (obtener, _a, _w) in self.campos_widgets.items()}
        try:
            if self.id_seleccionado is None:
                self.crear(valores)
                texto = "Registro creado correctamente."
            else:
                self.modificar(self.id_seleccionado, valores)
                texto = "Cambios guardados correctamente."
        except ReglaDominioError as error:
            self._mensaje(str(error), error=True)
            return
        except Exception as error:
            messagebox.showerror("Error", f"No se pudo guardar:\n{error}", parent=self.ventana)
            return
        self._recargar()
        self._nuevo(limpiar_mensaje=False)
        self._mensaje(texto)

    def _eliminar(self):
        if self.id_seleccionado is None:
            self._mensaje("Selecciona un registro de la tabla.", error=True)
            return
        nombre = self.filas_por_id.get(self.id_seleccionado, {}).get(self.clave_nombre, "")
        if not messagebox.askyesno(
                "Eliminar", f"¿Eliminar «{nombre}»?\nEsta acción no se puede deshacer.",
                parent=self.ventana):
            return
        try:
            self.eliminar(self.id_seleccionado)
        except ReglaDominioError as error:
            self._mensaje(str(error), error=True)
            return
        except Exception as error:
            messagebox.showerror("Error", f"No se pudo eliminar:\n{error}", parent=self.ventana)
            return
        self._recargar()
        self._nuevo(limpiar_mensaje=False)
        self._mensaje("Registro eliminado.")

    def _al_enter(self, evento):
        # Enter guarda, salvo en el buscador, la tabla, los botones o el cuadro de texto.
        if evento.widget in (self.entrada_buscar, self.tabla):
            return
        if isinstance(evento.widget, (tk.Text, ttk.Button)):
            return
        self._guardar()
