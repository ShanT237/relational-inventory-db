"""Tema visual compartido por todas las ventanas (Tkinter/ttk).
Para cambiar los colores de toda la aplicación basta con editar las constantes."""
import tkinter as tk
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
FAMILIA = "Segoe UI"
FUENTE = (FAMILIA, 10)
FUENTE_B = (FAMILIA, 10, "bold")
FUENTE_PEQ_B = (FAMILIA, 9, "bold")
FUENTE_SECCION = (FAMILIA, 12, "bold")
FUENTE_TITULO = (FAMILIA, 20, "bold")


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
                     font=(FAMILIA, 18, "bold"))
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
