"""Vista base reutilizable para los CRUD (Tkinter). No contiene SQL.

Cada módulo (ciudades, categorías, proveedores, productos) solo declara sus
columnas, sus campos y qué hacer al cargar/crear/modificar/eliminar; el diseño y
el comportamiento (búsqueda, filtro, orden, formulario) viven aquí.
La pantalla se dibuja DENTRO de un contenedor (no abre ventanas nuevas)."""
import re
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
    derecha: bool = False                # alinear a la derecha (precios, cantidades)
    orden_por: Optional[str] = None      # clave del dict por la que se ordena (si difiere)


@dataclass
class Campo:
    clave: str
    etiqueta: str
    tipo: str = "texto"            # texto | area | combo | combo_texto | check
    opciones: Optional[Callable] = None   # combo: [(id, texto)]; combo_texto: [texto]
    obligatorio: bool = False
    bloqueado_al_editar: bool = False     # se elige al crear y luego no se puede cambiar
    max_largo: int = 0                    # 0 = sin límite; si no, no deja escribir más caracteres
    solo_digitos: bool = False            # solo deja escribir números
    ayuda: str = ""                       # texto pequeño bajo el campo (formato esperado, ejemplo)


_NUMERO = re.compile(r"^-?\d+(\.\d+)?$")


def _clave_orden(valor):
    """Números primero (ordenados como número), luego texto (sin distinguir mayúsculas)."""
    texto = "" if valor is None else str(valor)
    if _NUMERO.match(texto):
        return (0, float(texto), "")
    return (1, 0.0, texto.lower())


def _iid(id_fila):
    """Identificador de fila en la tabla. El id puede ser un número o una tupla
    (llave compuesta, p. ej. proveedor + producto)."""
    if isinstance(id_fila, tuple):
        return "-".join(str(x) for x in id_fila)
    return str(id_fila)


class CrudVista:

    def __init__(self, contenedor, subtitulo, columnas, campos, cargar, crear,
                 modificar, eliminar, texto_nuevo, texto_editar,
                 tiene_estado=True, clave_nombre="nombre"):
        """cargar() -> lista de dicts con la clave 'id' (y 'estado' si tiene_estado).
        crear(valores) / modificar(id, valores) / eliminar(id) llaman al controlador."""
        self.contenedor = contenedor
        self.ventana = contenedor.winfo_toplevel()   # solo para cuadros de diálogo
        self.subtitulo = subtitulo
        self.columnas = columnas
        self.campos = campos
        self.cargar = cargar
        self.crear = crear
        self.modificar = modificar
        self.eliminar = eliminar
        self.texto_nuevo = texto_nuevo
        self.texto_editar = texto_editar
        self.tiene_estado = tiene_estado
        self.clave_nombre = clave_nombre

        self.id_seleccionado = None   # None = se está creando un registro nuevo
        self.filas = []
        self.filas_por_iid = {}
        self.orden = None             # (clave de columna, descendente)
        self.campos_widgets = {}      # clave -> (obtener, asignar, widget)

    # ------------------------------------------------------------------ pantalla
    def construir(self):
        """Dibuja la pantalla dentro del contenedor."""
        ttk.Label(self.contenedor, text=self.subtitulo, style="Suave.TLabel").pack(
            anchor="w", pady=(0, 12))
        cuerpo = ttk.Frame(self.contenedor)
        cuerpo.pack(fill="both", expand=True)
        cuerpo.columnconfigure(0, weight=1)
        cuerpo.columnconfigure(1, weight=0, minsize=350)
        cuerpo.rowconfigure(0, weight=1)
        self._construir_tabla(cuerpo)
        self._construir_formulario(cuerpo)
        self._recargar()
        self._nuevo()

    # -------------------------------------------------------------------- tabla
    def _construir_tabla(self, cuerpo):
        izquierda = e.tarjeta(cuerpo)
        izquierda.grid(row=0, column=0, sticky="nsew")

        barra = ttk.Frame(izquierda, style="Tarjeta.TFrame", padding=(16, 14, 16, 10))
        barra.pack(fill="x")
        ttk.Label(barra, text="Buscar", style="Campo.Tarjeta.TLabel").pack(side="left")
        self.var_buscar = tk.StringVar()
        self.entrada_buscar = ttk.Entry(barra, textvariable=self.var_buscar, width=24)
        self.entrada_buscar.pack(side="left", padx=(8, 16))
        self.var_buscar.trace_add("write", lambda *_: self._pintar())

        self.var_estado = tk.StringVar(value="Todos")
        if self.tiene_estado:
            ttk.Label(barra, text="Mostrar", style="Campo.Tarjeta.TLabel").pack(side="left")
            filtro = ttk.Combobox(barra, textvariable=self.var_estado, state="readonly",
                                  values=("Todos", "Activos", "Inactivos"), width=10)
            filtro.pack(side="left", padx=(8, 0))
            filtro.bind("<<ComboboxSelected>>", lambda _ev: self._pintar())

        self.lbl_conteo = ttk.Label(barra, text="", style="Suave.Tarjeta.TLabel")
        self.lbl_conteo.pack(side="right")

        marco = tk.Frame(izquierda, bg=e.TARJETA)
        marco.pack(fill="both", expand=True, padx=1, pady=(0, 1))
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(0, weight=1)
        self.tabla = ttk.Treeview(marco, columns=[c.clave for c in self.columnas],
                                  show="headings", selectmode="browse")
        ultima = len(self.columnas) - 1
        for i, c in enumerate(self.columnas):
            self.tabla.heading(c.clave, text=c.titulo,
                               command=lambda k=c.clave: self._ordenar(k))
            # Las columnas conservan su ancho; solo la última se estira. Si no caben
            # en la pantalla, aparece la barra horizontal.
            self.tabla.column(c.clave, width=c.ancho, minwidth=c.ancho if i == ultima else 50,
                              stretch=(i == ultima),
                              anchor="center" if c.centrado else ("e" if c.derecha else "w"))
        scroll = ttk.Scrollbar(marco, orient="vertical", command=self.tabla.yview)
        scroll_h = ttk.Scrollbar(marco, orient="horizontal", command=self.tabla.xview)

        def mover_horizontal(primero, ultimo):
            scroll_h.set(primero, ultimo)
            if float(primero) <= 0.0 and float(ultimo) >= 1.0:
                scroll_h.grid_remove()          # todo cabe: se oculta
            else:
                scroll_h.grid()

        self.tabla.configure(yscrollcommand=scroll.set, xscrollcommand=mover_horizontal)
        self.tabla.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")
        scroll_h.grid(row=1, column=0, sticky="ew")
        self.tabla.tag_configure("par", background=e.TARJETA)
        self.tabla.tag_configure("impar", background=e.FILA_IMPAR)
        self.tabla.tag_configure("inactivo", foreground="#94A3B8")
        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar)

    # --------------------------------------------------------------- formulario
    def _construir_formulario(self, cuerpo):
        derecha = e.tarjeta(cuerpo)
        derecha.grid(row=0, column=1, sticky="nsew", padx=(16, 0))
        contenido = ttk.Frame(derecha, style="Tarjeta.TFrame", padding=(20, 18))
        contenido.pack(fill="both", expand=True)

        # Arriba: título del modo. Abajo (fijos): mensaje y botones. En medio: campos
        # con desplazamiento, para que los botones nunca queden fuera de la pantalla.
        self.lbl_modo = ttk.Label(contenido, text="", style="Seccion.Tarjeta.TLabel")
        self.lbl_modo.pack(anchor="w", side="top")

        fila = ttk.Frame(contenido, style="Tarjeta.TFrame")
        fila.pack(fill="x", side="bottom")
        fila.columnconfigure((0, 1), weight=1, uniform="b")
        ttk.Button(fila, text="Nuevo", command=self._nuevo).grid(
            row=0, column=0, sticky="ew", padx=(0, 4))
        self.btn_eliminar = ttk.Button(fila, text="Eliminar", style="Peligro.TButton",
                                       command=self._eliminar)
        self.btn_eliminar.grid(row=0, column=1, sticky="ew", padx=(4, 0))

        self.btn_guardar = ttk.Button(contenido, text="Guardar", style="Primario.TButton",
                                      command=self._guardar)
        self.btn_guardar.pack(fill="x", side="bottom", pady=(10, 8))

        self.lbl_mensaje = ttk.Label(contenido, text="", style="Error.Tarjeta.TLabel",
                                     wraplength=290, justify="left")
        self.lbl_mensaje.pack(anchor="w", side="bottom", pady=(8, 0))

        zona = tk.Frame(contenido, bg=e.TARJETA)
        zona.pack(fill="both", expand=True, side="top")
        lienzo = tk.Canvas(zona, bg=e.TARJETA, highlightthickness=0, borderwidth=0)
        barra = ttk.Scrollbar(zona, orient="vertical", command=lienzo.yview)
        lienzo.configure(yscrollcommand=barra.set)
        marco = ttk.Frame(lienzo, style="Tarjeta.TFrame")
        id_marco = lienzo.create_window((0, 0), window=marco, anchor="nw")
        lienzo.pack(side="left", fill="both", expand=True)

        def ajustar(_ev=None):
            lienzo.configure(scrollregion=lienzo.bbox("all"))
            lienzo.itemconfigure(id_marco, width=lienzo.winfo_width())
            necesita = marco.winfo_reqheight() > lienzo.winfo_height()
            if necesita and not barra.winfo_ismapped():
                barra.pack(side="right", fill="y")
            elif not necesita and barra.winfo_ismapped():
                barra.pack_forget()

        marco.bind("<Configure>", ajustar)
        lienzo.bind("<Configure>", ajustar)

        def rueda(ev):
            try:
                if marco.winfo_reqheight() > lienzo.winfo_height():
                    lienzo.yview_scroll(-1 * (ev.delta // 120), "units")
            except tk.TclError:
                pass

        lienzo.bind("<Enter>", lambda _ev: lienzo.bind_all("<MouseWheel>", rueda))
        lienzo.bind("<Leave>", lambda _ev: lienzo.unbind_all("<MouseWheel>"))
        lienzo.bind("<Destroy>", lambda _ev: lienzo.unbind_all("<MouseWheel>"))

        for campo in self.campos:
            if campo.tipo != "check":
                texto = campo.etiqueta + (" *" if campo.obligatorio else "")
                ttk.Label(marco, text=texto, style="Campo.Tarjeta.TLabel").pack(
                    anchor="w", pady=(10, 4))
            self.campos_widgets[campo.clave] = self._crear_widget(marco, campo)
            if campo.ayuda:
                ttk.Label(marco, text=campo.ayuda, style="Suave.Tarjeta.TLabel",
                          font=(e.FAMILIA, 8), wraplength=290, justify="left").pack(
                    anchor="w", pady=(3, 0))

    def _crear_widget(self, padre, campo):
        """Crea el control del campo y devuelve (obtener, asignar, widget)."""
        if campo.tipo == "area":
            marco_area = tk.Frame(padre, bg=e.TARJETA)
            marco_area.pack(fill="x")
            w = tk.Text(marco_area, height=5, wrap="word", relief="flat", bg=e.TARJETA,
                        fg=e.TEXTO, font=e.FUENTE, padx=8, pady=6, highlightthickness=1,
                        highlightbackground=e.BORDE_FUERTE, highlightcolor=e.PRIMARIO,
                        insertbackground=e.TEXTO)
            barra_area = ttk.Scrollbar(marco_area, orient="vertical", command=w.yview)
            w.configure(yscrollcommand=barra_area.set)
            w.pack(side="left", fill="x", expand=True)
            barra_area.pack(side="right", fill="y")
            w.bind("<Control-s>", self._guardar)

            contador = ttk.Label(padre, text="", style="Suave.Tarjeta.TLabel")
            contador.pack(anchor="e", pady=(2, 0))

            def ajustar(_evento=None):
                contenido = w.get("1.0", "end-1c")
                if campo.max_largo and len(contenido) > campo.max_largo:
                    w.delete(f"1.0+{campo.max_largo}c", "end")     # no pasa del máximo
                    contenido = w.get("1.0", "end-1c")
                contador.config(text=f"{len(contenido)} / {campo.max_largo}" if campo.max_largo
                                else f"{len(contenido)} caracteres")

            w.bind("<KeyRelease>", ajustar)
            w.bind("<<Paste>>", lambda _ev: w.after_idle(ajustar))

            def asignar(valor):
                w.delete("1.0", "end")
                w.insert("1.0", "" if valor is None else str(valor))
                ajustar()
            return (lambda: w.get("1.0", "end-1c")), asignar, w

        if campo.tipo == "combo":
            pares = campo.opciones() if campo.opciones else []
            a_id = {texto: id_ for id_, texto in pares}
            a_texto = {id_: texto for id_, texto in pares}
            w = ttk.Combobox(padre, state="readonly", values=[t for _, t in pares])
            w.pack(fill="x")
            obtenido = (lambda: a_id.get(w.get())), (lambda valor: w.set(a_texto.get(valor, "")))

        elif campo.tipo == "combo_texto":
            w = ttk.Combobox(padre, values=list(campo.opciones() if campo.opciones else []))
            w.pack(fill="x")
            obtenido = w.get, (lambda valor: w.set("" if valor is None else str(valor)))

        elif campo.tipo == "check":
            variable = tk.BooleanVar(value=True)
            w = ttk.Checkbutton(padre, text=campo.etiqueta, variable=variable,
                                style="Tarjeta.TCheckbutton")
            w.pack(anchor="w", pady=(14, 0))
            obtenido = variable.get, (lambda valor: variable.set(bool(valor)))

        else:
            w = ttk.Entry(padre)
            w.pack(fill="x")
            limitar = bool(campo.max_largo or campo.solo_digitos)
            if limitar:
                def permitido(nuevo):
                    if campo.max_largo and len(nuevo) > campo.max_largo:
                        return False
                    if campo.solo_digitos and nuevo and not re.fullmatch(r"[0-9]+", nuevo):
                        return False
                    return True
                w.configure(validate="key", validatecommand=(w.register(permitido), "%P"))

            def asignar_texto(valor):
                if limitar:
                    w.configure(validate="none")    # al cargar un registro no se valida
                w.delete(0, "end")
                w.insert(0, "" if valor is None else str(valor))
                if limitar:
                    w.configure(validate="key")
            obtenido = w.get, asignar_texto

        # Enter y Ctrl+S guardan cuando el foco está en este campo.
        w.bind("<Return>", self._guardar)
        w.bind("<Control-s>", self._guardar)
        return obtenido[0], obtenido[1], w

    # ----------------------------------------------------------- datos y tabla
    def _recargar(self):
        try:
            self.filas = self.cargar()
        except Exception as error:
            self.filas = []
            messagebox.showerror("Error", f"No se pudieron cargar los datos:\n{error}",
                                 parent=self.ventana)
        self.filas_por_iid = {_iid(f["id"]): f for f in self.filas}
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
            columna = next(c for c in self.columnas if c.clave == clave)
            clave_valor = columna.orden_por or clave
            visibles.sort(key=lambda f: _clave_orden(f.get(clave_valor)), reverse=descendente)

        self.tabla.delete(*self.tabla.get_children())
        for i, f in enumerate(visibles):
            etiquetas = ["par" if i % 2 == 0 else "impar"]
            if not f.get("estado", True):
                etiquetas.append("inactivo")
            self.tabla.insert("", "end", iid=_iid(f["id"]), tags=etiquetas,
                              values=[str(f.get(c.clave, "")).replace("\n", " ")
                                      for c in self.columnas])
        if self.id_seleccionado is not None and self.tabla.exists(_iid(self.id_seleccionado)):
            self.tabla.selection_set(_iid(self.id_seleccionado))

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
    @staticmethod
    def _habilitar(widget, habilitado):
        try:
            widget.state(["!disabled"] if habilitado else ["disabled"])   # widgets ttk
        except AttributeError:
            widget.configure(state="normal" if habilitado else "disabled")

    def _mensaje(self, texto, error=False):
        self.lbl_mensaje.config(
            text=texto, style="Error.Tarjeta.TLabel" if error else "Exito.Tarjeta.TLabel")
        if texto and not error:
            self.lbl_mensaje.after(3500, self._borrar_mensaje, texto)

    def _borrar_mensaje(self, texto):
        if self.lbl_mensaje.winfo_exists() and self.lbl_mensaje.cget("text") == texto:
            self.lbl_mensaje.config(text="")

    def _nuevo(self, limpiar_mensaje=True):
        self.id_seleccionado = None
        for campo in self.campos:
            _, asignar, widget = self.campos_widgets[campo.clave]
            if campo.bloqueado_al_editar:
                self._habilitar(widget, True)
            asignar(True if campo.tipo == "check" else "")
        self.tabla.selection_remove(self.tabla.selection())
        self.lbl_modo.config(text=self.texto_nuevo)
        self.btn_eliminar.state(["disabled"])
        if limpiar_mensaje:
            self.lbl_mensaje.config(text="")
        self.campos_widgets[self.campos[0].clave][2].focus_set()

    def _al_seleccionar(self, _evento=None):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        fila = self.filas_por_iid.get(seleccion[0])
        if fila is None:
            return
        id_fila = fila["id"]
        if id_fila == self.id_seleccionado:
            return
        self.id_seleccionado = id_fila
        for campo in self.campos:
            _, asignar, widget = self.campos_widgets[campo.clave]
            if campo.bloqueado_al_editar:
                self._habilitar(widget, True)      # se habilita solo para poder asignar
            asignar(fila.get(campo.clave))
            if campo.bloqueado_al_editar:
                self._habilitar(widget, False)
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
            return "break"
        except Exception as error:
            messagebox.showerror("Error", f"No se pudo guardar:\n{error}", parent=self.ventana)
            return "break"
        self._recargar()
        self._nuevo(limpiar_mensaje=False)
        self._mensaje(texto)
        return "break"

    def _eliminar(self):
        if self.id_seleccionado is None:
            self._mensaje("Selecciona un registro de la tabla.", error=True)
            return
        nombre = self.filas_por_iid.get(_iid(self.id_seleccionado), {}).get(
            self.clave_nombre, "")
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
