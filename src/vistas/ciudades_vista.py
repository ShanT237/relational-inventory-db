"""Vista: CRUD de ciudades (Tkinter). No contiene SQL."""
import tkinter as tk
from tkinter import messagebox, ttk

from dominio.excepciones.regla_dominio_error import ReglaDominioError


class CiudadesVista:

    def __init__(self, padre, ciudad_controlador):
        self.padre = padre
        self.controlador = ciudad_controlador
        self.id_seleccionado = None   # None = se está creando una ciudad nueva

    def mostrar(self):
        ventana = tk.Toplevel(self.padre)
        ventana.title("Ciudades")
        ventana.geometry("620x440")
        ventana.transient(self.padre)
        ventana.grab_set()

        # --- Formulario ---
        formulario = ttk.LabelFrame(ventana, text="Datos de la ciudad", padding=12)
        formulario.pack(fill="x", padx=12, pady=(12, 6))

        ttk.Label(formulario, text="Nombre:").grid(row=0, column=0, sticky="e", pady=4)
        entrada_nombre = ttk.Entry(formulario, width=30)
        entrada_nombre.grid(row=0, column=1, padx=8)

        ttk.Label(formulario, text="Departamento:").grid(row=1, column=0, sticky="e", pady=4)
        entrada_departamento = ttk.Entry(formulario, width=30)
        entrada_departamento.grid(row=1, column=1, padx=8)

        # --- Tabla ---
        marco_tabla = ttk.Frame(ventana)
        marco_tabla.pack(fill="both", expand=True, padx=12, pady=6)

        tabla = ttk.Treeview(marco_tabla, columns=("id", "nombre", "departamento"),
                             show="headings", selectmode="browse")
        tabla.heading("id", text="Id")
        tabla.heading("nombre", text="Nombre")
        tabla.heading("departamento", text="Departamento")
        tabla.column("id", width=50, anchor="center")
        tabla.column("nombre", width=250)
        tabla.column("departamento", width=250)
        barra = ttk.Scrollbar(marco_tabla, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=barra.set)
        tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

        # --- Acciones ---
        def cargar_tabla():
            tabla.delete(*tabla.get_children())
            try:
                for c in self.controlador.listar():
                    tabla.insert("", "end", iid=str(c.id_ciudad),
                                 values=(c.id_ciudad, c.nombre, c.departamento))
            except Exception as error:
                messagebox.showerror("Error", f"No se pudieron cargar las ciudades:\n{error}",
                                     parent=ventana)

        def limpiar():
            self.id_seleccionado = None
            entrada_nombre.delete(0, tk.END)
            entrada_departamento.delete(0, tk.END)
            tabla.selection_remove(tabla.selection())
            entrada_nombre.focus()

        def al_seleccionar(_evento=None):
            seleccion = tabla.selection()
            if not seleccion:
                return
            id_ciudad, nombre, departamento = tabla.item(seleccion[0], "values")
            self.id_seleccionado = int(id_ciudad)
            entrada_nombre.delete(0, tk.END)
            entrada_nombre.insert(0, nombre)
            entrada_departamento.delete(0, tk.END)
            entrada_departamento.insert(0, departamento)

        def guardar():
            try:
                if self.id_seleccionado is None:
                    self.controlador.crear(entrada_nombre.get(), entrada_departamento.get())
                else:
                    self.controlador.modificar(self.id_seleccionado, entrada_nombre.get(),
                                               entrada_departamento.get())
            except ReglaDominioError as error:
                messagebox.showwarning("Ciudades", str(error), parent=ventana)
                return
            except Exception as error:
                messagebox.showerror("Error", f"No se pudo guardar:\n{error}", parent=ventana)
                return
            cargar_tabla()
            limpiar()

        def eliminar():
            if self.id_seleccionado is None:
                messagebox.showinfo("Ciudades", "Selecciona una ciudad de la tabla.",
                                    parent=ventana)
                return
            if not messagebox.askyesno("Eliminar", "¿Eliminar la ciudad seleccionada?",
                                       parent=ventana):
                return
            try:
                self.controlador.eliminar(self.id_seleccionado)
            except ReglaDominioError as error:
                messagebox.showwarning("Ciudades", str(error), parent=ventana)
                return
            except Exception as error:
                messagebox.showerror("Error", f"No se pudo eliminar:\n{error}", parent=ventana)
                return
            cargar_tabla()
            limpiar()

        botones = ttk.Frame(ventana)
        botones.pack(pady=(0, 12))
        ttk.Button(botones, text="Nuevo", command=limpiar).pack(side="left", padx=4)
        ttk.Button(botones, text="Guardar", command=guardar).pack(side="left", padx=4)
        ttk.Button(botones, text="Eliminar", command=eliminar).pack(side="left", padx=4)
        ttk.Button(botones, text="Cerrar", command=ventana.destroy).pack(side="left", padx=4)

        tabla.bind("<<TreeviewSelect>>", al_seleccionar)
        cargar_tabla()
        entrada_nombre.focus()