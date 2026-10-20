"""Vista: ventana de inicio de sesión (Tkinter). No contiene SQL."""
import tkinter as tk
from tkinter import messagebox, ttk

from dominio.excepciones.regla_dominio_error import ReglaDominioError


class LoginVista:

    def __init__(self, autenticacion_controlador):
        self.controlador = autenticacion_controlador
        self.sesion = None

    def mostrar(self):
        """Muestra el login. Devuelve la Sesion si ingresó, o None si cerró la ventana."""
        raiz = tk.Tk()
        raiz.title("Ingreso - Gestión de Proveedores y Productos")
        raiz.resizable(False, False)

        marco = ttk.Frame(raiz, padding=24)
        marco.grid()

        ttk.Label(marco, text="Iniciar sesión", font=("Segoe UI", 16, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 16))

        ttk.Label(marco, text="Usuario:").grid(row=1, column=0, sticky="e", pady=4)
        entrada_usuario = ttk.Entry(marco, width=28)
        entrada_usuario.grid(row=1, column=1, pady=4, padx=(8, 0))

        ttk.Label(marco, text="Contraseña:").grid(row=2, column=0, sticky="e", pady=4)
        entrada_clave = ttk.Entry(marco, width=28, show="*")
        entrada_clave.grid(row=2, column=1, pady=4, padx=(8, 0))

        def ingresar(_evento=None):
            try:
                self.sesion = self.controlador.iniciar_sesion(
                    entrada_usuario.get(), entrada_clave.get())
            except ReglaDominioError as error:
                messagebox.showwarning("Ingreso", str(error), parent=raiz)
                entrada_clave.delete(0, tk.END)
                return
            except Exception as error:  # fallo de conexión, etc.
                messagebox.showerror("Error", f"No se pudo ingresar:\n{error}", parent=raiz)
                return
            raiz.destroy()

        ttk.Button(marco, text="Ingresar", command=ingresar).grid(
            row=3, column=0, columnspan=2, pady=(16, 0))
        raiz.bind("<Return>", ingresar)

        entrada_usuario.focus()
        raiz.mainloop()
        return self.sesion
