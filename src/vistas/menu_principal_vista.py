"""Vista: ventana principal con el menú. Las opciones dependen del rol."""
import tkinter as tk
from tkinter import messagebox, ttk
from vistas.ciudades_vista import CiudadesVista
from vistas.categorias_vista import CategoriasVista


class MenuPrincipalVista:

    def __init__(self, autenticacion_controlador, ciudad_controlador,
                 categoria_controlador, sesion):
        self.controlador = autenticacion_controlador
        self.ciudad_controlador = ciudad_controlador
        self.categoria_controlador = categoria_controlador
        self.sesion = sesion
        self.volver_al_login = False

    def mostrar(self):
        """Muestra el menú. Devuelve True si el usuario pidió 'Cerrar sesión'
        (volver al login) o False si pidió salir de la aplicación."""
        sesion = self.sesion
        raiz = tk.Tk()
        raiz.title("Gestión de Proveedores y Productos")
        raiz.geometry("900x560")

        def pendiente(nombre):
            # Aquí se irá conectando cada vista real.
            return lambda: messagebox.showinfo(
                "En construcción", f"«{nombre}» aún no está implementado.", parent=raiz)

        def terminar(volver):
            self.volver_al_login = volver
            try:
                self.controlador.cerrar_sesion(sesion)  # registra la salida en la bitácora
            except Exception as error:
                messagebox.showerror("Bitácora", f"No se pudo registrar la salida:\n{error}")
            raiz.destroy()

        barra = tk.Menu(raiz)

        if sesion.puede_modificar():
            m = tk.Menu(barra, tearoff=0)
            m.add_command(label="Ciudades", command=lambda: CiudadesVista(
                raiz, self.ciudad_controlador).mostrar())
            m.add_command(label="Categorías", command=lambda: CategoriasVista(
                raiz, self.categoria_controlador).mostrar())
            for nombre in ("Proveedores", "Productos"):
                m.add_command(label=nombre, command=pendiente(nombre))
            barra.add_cascade(label="Entidades", menu=m)

            m = tk.Menu(barra, tearoff=0)
            m.add_command(label="Productos por proveedor",
                          command=pendiente("Productos por proveedor"))
            barra.add_cascade(label="Transacciones", menu=m)

        m = tk.Menu(barra, tearoff=0)
        for nombre in ("Proveedores con ciudad y productos",
                       "Productos con categoría y proveedores",
                       "Bitácora de ingresos con usuario y rol",
                       "Proveedores con precio sobre el promedio",
                       "Productos sin proveedor"):
            m.add_command(label=nombre, command=pendiente(nombre))
        barra.add_cascade(label="Consultas", menu=m)

        if sesion.puede_modificar():
            m = tk.Menu(barra, tearoff=0)
            for nombre in ("Productos de un proveedor",
                           "Proveedores por ciudad",
                           "Proveedores de un producto",
                           "Productos de una categoría",
                           "Cantidad de productos por categoría"):
                m.add_command(label=nombre, command=pendiente(nombre))
            barra.add_cascade(label="Reportes", menu=m)

        if sesion.es_administrador():
            m = tk.Menu(barra, tearoff=0)
            m.add_command(label="Gestión de usuarios", command=pendiente("Gestión de usuarios"))
            m.add_command(label="Bitácora de entrada y salida", command=pendiente("Bitácora"))
            barra.add_cascade(label="Auditoría", menu=m)

        m = tk.Menu(barra, tearoff=0)
        m.add_command(label="Cerrar sesión", command=lambda: terminar(True))
        m.add_command(label="Salir", command=lambda: terminar(False))
        barra.add_cascade(label="Sesión", menu=m)

        raiz.config(menu=barra)

        ttk.Label(raiz, text=f"Bienvenido, {sesion.nombre_completo}",
                  font=("Segoe UI", 18, "bold")).pack(pady=(60, 8))
        ttk.Label(raiz, text=f"Rol: {sesion.rol}", font=("Segoe UI", 12)).pack()

        raiz.protocol("WM_DELETE_WINDOW", lambda: terminar(False))  # cerrar con la X
        raiz.mainloop()
        return self.volver_al_login
