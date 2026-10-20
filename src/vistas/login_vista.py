"""Vista: ventana de inicio de sesión (Tkinter). No contiene SQL."""
import tkinter as tk
from tkinter import messagebox, ttk

from dominio.excepciones.regla_dominio_error import ReglaDominioError
from vistas import estilos as e


class LoginVista:

    def __init__(self, autenticacion_controlador):
        self.controlador = autenticacion_controlador
        self.sesion = None

    def mostrar(self):
        """Muestra el login. Devuelve la Sesion si ingresó, o None si cerró la ventana."""
        raiz = tk.Tk()
        raiz.title("Ingreso - Gestión de Proveedores y Productos")
        e.aplicar_tema(raiz)
        raiz.resizable(False, False)
        e.centrar(raiz, 800, 480)

        # Panel izquierdo (marca)
        lateral = tk.Frame(raiz, bg=e.OSCURO, width=310)
        lateral.pack(side="left", fill="y")
        lateral.pack_propagate(False)
        tk.Frame(lateral, bg=e.PRIMARIO, width=48, height=5).pack(
            anchor="w", padx=36, pady=(110, 18))
        tk.Label(lateral, text="Gestión de\nProveedores\ny Productos", bg=e.OSCURO,
                 fg="#FFFFFF", font=(e.FAMILIA, 24, "bold"), justify="left").pack(
            anchor="w", padx=36)
        tk.Label(lateral, text="Bases de Datos I\nUniversidad del Quindío", bg=e.OSCURO,
                 fg="#94A3B8", font=e.FUENTE, justify="left").pack(
            anchor="w", padx=36, pady=(16, 0))

        # Panel derecho (formulario)
        derecha = tk.Frame(raiz, bg=e.TARJETA)
        derecha.pack(side="left", fill="both", expand=True)
        marco = ttk.Frame(derecha, style="Tarjeta.TFrame")
        marco.place(relx=0.5, rely=0.5, anchor="center", width=320)

        ttk.Label(marco, text="Bienvenido", style="Seccion.Tarjeta.TLabel",
                  font=(e.FAMILIA, 20, "bold")).pack(anchor="w")
        ttk.Label(marco, text="Ingresa tus credenciales para continuar.",
                  style="Suave.Tarjeta.TLabel").pack(anchor="w", pady=(2, 18))

        ttk.Label(marco, text="Usuario", style="Campo.Tarjeta.TLabel").pack(anchor="w", pady=(0, 4))
        entrada_usuario = ttk.Entry(marco)
        entrada_usuario.pack(fill="x")

        ttk.Label(marco, text="Contraseña", style="Campo.Tarjeta.TLabel").pack(
            anchor="w", pady=(14, 4))
        entrada_clave = ttk.Entry(marco, show="•")
        entrada_clave.pack(fill="x")

        mostrar_clave = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            marco, text="Mostrar contraseña", variable=mostrar_clave,
            style="Tarjeta.TCheckbutton",
            command=lambda: entrada_clave.config(show="" if mostrar_clave.get() else "•"),
        ).pack(anchor="w", pady=(10, 0))

        mensaje = ttk.Label(marco, text="", style="Error.Tarjeta.TLabel",
                            wraplength=320, justify="left")
        mensaje.pack(anchor="w", pady=(10, 0))

        def ingresar(_evento=None):
            mensaje.config(text="")
            try:
                self.sesion = self.controlador.iniciar_sesion(
                    entrada_usuario.get(), entrada_clave.get())
            except ReglaDominioError as error:
                mensaje.config(text=str(error))
                entrada_clave.delete(0, tk.END)
                entrada_clave.focus_set()
                return
            except Exception as error:  # fallo de conexión, etc.
                messagebox.showerror("Error", f"No se pudo ingresar:\n{error}", parent=raiz)
                return
            raiz.destroy()

        ttk.Button(marco, text="Ingresar", style="Primario.TButton", command=ingresar).pack(
            fill="x", pady=(14, 0))
        raiz.bind("<Return>", ingresar)

        entrada_usuario.focus_set()
        raiz.mainloop()
        return self.sesion
