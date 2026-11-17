"""Tema visual compartido por todas las ventanas (Tkinter/ttk).
Para cambiar los colores de toda la aplicación basta con editar las constantes."""
import tkinter as tk
import re
from tkinter import font as tkfont
from tkinter import ttk

# --- Paleta ---
FONDO = "#F1F5F9"
TARJETA = "#FFFFFF"
OSCURO = "#0F172A"
OSCURO_2 = "#1E293B"
PRIMARIO = "#2563EB"
PRIMARIO_HOVER = "#1D4ED8"
PELIGRO = "#DC2626"
PELIGRO_HOVER = "#B91C1C"
EXITO = "#16A34A"
TEXTO = "#0F172A"
SUAVE = "#64748B"
BORDE = "#E2E8F0"
BORDE_FUERTE = "#CBD5E1"
FILA_IMPAR = "#F8FAFC"
SELECCION = "#DBEAFE"

# --- Tipografías ---
# Son fuentes con nombre: se crean en aplicar_tema() y se agrandan o achican en vivo
# cuando cambia el tamaño de la ventana (ver configurar_ventana).
FAMILIA = "Segoe UI"
FUENTE = "FuenteBase"
FUENTE_B = "FuenteNegrita"
FUENTE_PEQ_B = "FuentePequenaNegrita"
FUENTE_MINI = "FuenteMini"
FUENTE_SECCION = "FuenteSeccion"
FUENTE_TITULO = "FuenteTitulo"
FUENTE_ENCABEZADO = "FuenteEncabezado"
FUENTE_MENU_MARCA = "FuenteMenuMarca"
FUENTE_LOGIN_MARCA = "FuenteLoginMarca"

_GEOMETRIA = re.compile(r"^(\d+)x(\d+)([+-]-?\d+)([+-]-?\d+)$")

_TAMANOS_BASE = {            # nombre: (tamaño en puntos, negrita)
    FUENTE: (10, False), FUENTE_B: (10, True), FUENTE_PEQ_B: (9, True),
    FUENTE_MINI: (8, False), FUENTE_SECCION: (12, True), FUENTE_TITULO: (20, True),
    FUENTE_ENCABEZADO: (18, True), FUENTE_MENU_MARCA: (16, True),
    FUENTE_LOGIN_MARCA: (24, True),
}
_fuentes = {}


def _crear_fuentes(raiz):
    for nombre, (tamano, negrita) in _TAMANOS_BASE.items():
        _fuentes[nombre] = tkfont.Font(
            root=raiz, name=nombre, exists=False, family=FAMILIA, size=tamano,
            weight="bold" if negrita else "normal")


def _boton(estilo, nombre, normal, hover, texto, apagado, texto_apagado, **extra):
    estilo.configure(nombre, background=normal, foreground=texto, bordercolor=normal,
                     lightcolor=normal, darkcolor=normal, relief="flat", borderwidth=0,
                     focusthickness=0, focuscolor=normal, font=FUENTE_B, **extra)
    estilo.map(nombre,
               background=[("disabled", apagado), ("active", hover)],
               bordercolor=[("disabled", apagado), ("active", hover)],
               lightcolor=[("disabled", apagado), ("active", hover)],
               darkcolor=[("disabled", apagado), ("active", hover)],
               foreground=[("disabled", texto_apagado)])


def aplicar_tema(raiz):
    """Configura los estilos ttk. Se llama una vez por cada ventana raíz (tk.Tk)."""
    _crear_fuentes(raiz)
    estilo = ttk.Style(raiz)
    estilo.theme_use("clam")
    raiz.configure(background=FONDO)
    raiz.option_add("*TCombobox*Listbox.font", FUENTE)
    raiz.option_add("*TCombobox*Listbox.selectBackground", PRIMARIO)
    raiz.option_add("*TCombobox*Listbox.selectForeground", "#FFFFFF")

    estilo.configure(".", background=FONDO, foreground=TEXTO, font=FUENTE)

    # Marcos y etiquetas
    estilo.configure("TFrame", background=FONDO)
    estilo.configure("Tarjeta.TFrame", background=TARJETA)
    estilo.configure("TLabel", background=FONDO, foreground=TEXTO)
    estilo.configure("Tarjeta.TLabel", background=TARJETA)
    estilo.configure("Campo.Tarjeta.TLabel", foreground=SUAVE, font=FUENTE_PEQ_B)
    estilo.configure("Seccion.Tarjeta.TLabel", font=FUENTE_SECCION)
    estilo.configure("Suave.TLabel", foreground=SUAVE)
    estilo.configure("Suave.Tarjeta.TLabel", foreground=SUAVE)
    estilo.configure("Error.Tarjeta.TLabel", foreground=PELIGRO)
    estilo.configure("Exito.Tarjeta.TLabel", foreground=EXITO)
    estilo.configure("Pagina.TLabel", font=FUENTE_TITULO)
    estilo.configure("Encabezado.TLabel", background=OSCURO, foreground="#FFFFFF",
                     font=FUENTE_ENCABEZADO)
    estilo.configure("EncabezadoSub.TLabel", background=OSCURO, foreground="#94A3B8")

    # Botones
    _boton(estilo, "TButton", BORDE, BORDE_FUERTE, TEXTO, "#F1F5F9", "#94A3B8",
           padding=(14, 9))
    _boton(estilo, "Primario.TButton", PRIMARIO, PRIMARIO_HOVER, "#FFFFFF", "#93C5FD",
           "#FFFFFF", padding=(14, 10))
    _boton(estilo, "Peligro.TButton", "#FEE2E2", "#FECACA", PELIGRO, "#F1F5F9",
           "#94A3B8", padding=(14, 9))
    _boton(estilo, "Lateral.TButton", OSCURO, OSCURO_2, "#CBD5E1", OSCURO, "#475569",
           padding=(22, 12), anchor="w")
    estilo.map("Lateral.TButton", foreground=[("active", "#FFFFFF")])
    _boton(estilo, "LateralActivo.TButton", PRIMARIO, PRIMARIO, "#FFFFFF", PRIMARIO,
           "#FFFFFF", padding=(22, 12), anchor="w")

    # Campos de entrada
    campo = dict(fieldbackground=TARJETA, foreground=TEXTO, bordercolor=BORDE_FUERTE,
                 lightcolor=BORDE_FUERTE, darkcolor=BORDE_FUERTE, padding=(8, 7),
                 insertcolor=TEXTO)
    estilo.configure("TEntry", **campo)
    estilo.map("TEntry", bordercolor=[("focus", PRIMARIO)],
               lightcolor=[("focus", PRIMARIO)], darkcolor=[("focus", PRIMARIO)])
    estilo.configure("TCombobox", background=TARJETA, arrowcolor=SUAVE, **campo)
    estilo.map("TCombobox",
               fieldbackground=[("disabled", FILA_IMPAR), ("readonly", TARJETA)],
               foreground=[("disabled", SUAVE)],
               selectbackground=[("readonly", TARJETA)],
               selectforeground=[("readonly", TEXTO)],
               bordercolor=[("focus", PRIMARIO)],
               lightcolor=[("focus", PRIMARIO)], darkcolor=[("focus", PRIMARIO)])
    estilo.configure("Tarjeta.TCheckbutton", background=TARJETA, foreground=TEXTO,
                     focuscolor=TARJETA)
    estilo.map("Tarjeta.TCheckbutton", background=[("active", TARJETA)])

    # Tabla
    estilo.configure("Treeview", background=TARJETA, fieldbackground=TARJETA,
                     foreground=TEXTO, rowheight=34, borderwidth=0, font=FUENTE)
    estilo.map("Treeview", background=[("selected", SELECCION)],
               foreground=[("selected", TEXTO)])
    estilo.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
    estilo.configure("Treeview.Heading", background=FILA_IMPAR, foreground=SUAVE,
                     font=FUENTE_B, padding=(10, 9), relief="flat", borderwidth=0,
                     lightcolor=FILA_IMPAR, darkcolor=FILA_IMPAR, bordercolor=BORDE)
    estilo.map("Treeview.Heading", background=[("active", BORDE)])

    estilo.configure("Vertical.TScrollbar", background=BORDE_FUERTE, troughcolor=TARJETA,
                     bordercolor=TARJETA, lightcolor=BORDE_FUERTE, darkcolor=BORDE_FUERTE,
                     arrowcolor=SUAVE, relief="flat", arrowsize=14)
    estilo.map("Vertical.TScrollbar", background=[("active", "#94A3B8")])
    estilo.configure("Horizontal.TScrollbar", background=BORDE_FUERTE, troughcolor=TARJETA,
                     bordercolor=TARJETA, lightcolor=BORDE_FUERTE, darkcolor=BORDE_FUERTE,
                     arrowcolor=SUAVE, relief="flat", arrowsize=14)
    estilo.map("Horizontal.TScrollbar", background=[("active", "#94A3B8")])


def tarjeta(padre, **opciones):
    """Panel blanco con borde fino (se ve como una 'tarjeta')."""
    return tk.Frame(padre, bg=TARJETA, highlightthickness=1, highlightbackground=BORDE,
                    highlightcolor=BORDE, **opciones)


def centrar(ventana, ancho, alto, padre=None):
    """Fija el tamaño de la ventana y la centra (sobre el padre, si lo hay)."""
    ventana.update_idletasks()
    ancho = min(ancho, ventana.winfo_screenwidth() - 40)
    alto = min(alto, ventana.winfo_screenheight() - 100)
    if padre is not None and padre.winfo_viewable():
        x = padre.winfo_rootx() + (padre.winfo_width() - ancho) // 2
        y = padre.winfo_rooty() + (padre.winfo_height() - alto) // 2
    else:
        x = (ventana.winfo_screenwidth() - ancho) // 2
        y = (ventana.winfo_screenheight() - alto) // 2
    ventana.geometry(f"{ancho}x{alto}+{max(x, 0)}+{max(y, 0)}")


# Tamaño y estado (normal o maximizada) de la última ventana, para que la siguiente
# (login -> menú -> login) se abra igual y no vuelva al tamaño por defecto.
_VENTANA = {"maximizada": False, "geometria": None}
TAMANO_MINIMO = (1000, 620)     # mismo mínimo para el login y el menú
TAMANO_INICIAL = (1100, 680)
_FACTOR_MAXIMO = 1.5


def _geometria_dentro_de_pantalla(raiz, geometria):
    """'ANCHOxALTO+X+Y' -> la misma, pero sin que la ventana se salga de la pantalla."""
    coincidencia = _GEOMETRIA.match(geometria)
    if coincidencia is None:
        return geometria
    ancho, alto = int(coincidencia.group(1)), int(coincidencia.group(2))
    x_texto, y_texto = coincidencia.group(3), coincidencia.group(4)
    # '+-1025' -> -1025 ; '-50' -> -50 ; '+100' -> 100
    x = int(x_texto.replace("+-", "-").replace("+", ""))
    y = int(y_texto.replace("+-", "-").replace("+", ""))
    pantalla_w, pantalla_h = raiz.winfo_screenwidth(), raiz.winfo_screenheight()
    ancho, alto = min(ancho, pantalla_w - 20), min(alto, pantalla_h - 80)
    x = max(0, min(x, pantalla_w - ancho - 10))
    y = max(0, min(y, pantalla_h - alto - 60))
    return f"{ancho}x{alto}+{x}+{y}"


def configurar_ventana(raiz, ancho=None, alto=None, minimo=None, al_escalar=None):
    """Hace la ventana redimensionable, la abre con el mismo tamaño y estado (normal o
    maximizada) que tenía la ventana anterior y escala letras y filas según su tamaño.
    al_escalar(factor) se llama cada vez que cambia la escala (para ajustes propios)."""
    ancho, alto = (ancho or TAMANO_INICIAL[0]), (alto or TAMANO_INICIAL[1])
    minimo = minimo or TAMANO_MINIMO
    raiz.resizable(True, True)
    raiz.minsize(*minimo)
    if _VENTANA["geometria"]:
        raiz.geometry(_geometria_dentro_de_pantalla(raiz, _VENTANA["geometria"]))
    else:
        centrar(raiz, ancho, alto)
    if _VENTANA["maximizada"]:
        raiz.state("zoomed")

    escala = {"factor": None, "pendiente": None}

    def aplicar_escala():
        escala["pendiente"] = None
        factor = min(raiz.winfo_width() / minimo[0], raiz.winfo_height() / minimo[1])
        factor = round(max(1.0, min(factor, _FACTOR_MAXIMO)) * 20) / 20   # pasos de 0.05
        if factor == escala["factor"]:
            return
        escala["factor"] = factor
        for nombre, (tamano, _negrita) in _TAMANOS_BASE.items():
            _fuentes[nombre].configure(size=max(1, round(tamano * factor)))
        ttk.Style(raiz).configure("Treeview", rowheight=round(34 * factor))
        if al_escalar:
            al_escalar(factor)

    def al_cambiar(evento):
        if evento.widget is not raiz:
            return
        estado = raiz.state()
        if estado == "zoomed":
            _VENTANA["maximizada"] = True
        elif estado == "normal":
            _VENTANA["maximizada"] = False
            _VENTANA["geometria"] = raiz.geometry()
        if escala["pendiente"] is None:                 # una sola vez por ráfaga de eventos
            escala["pendiente"] = raiz.after(60, aplicar_escala)

    raiz.bind("<Configure>", al_cambiar, add="+")
    raiz.after_idle(aplicar_escala)