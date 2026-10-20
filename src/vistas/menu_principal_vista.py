"""Vista: ventana principal. Barra lateral por secciones; las opciones dependen del rol."""
import tkinter as tk
from tkinter import messagebox, ttk

from vistas import estilos as e
from vistas.categorias_vista import CategoriasVista
from vistas.ciudades_vista import CiudadesVista
from vistas.productos_vista import ProductosVista
from vistas.proveedores_vista import ProveedoresVista


class MenuPrincipalVista:

    def __init__(self, autenticacion_controlador, ciudad_controlador,
                 categoria_controlador, proveedor_controlador, producto_controlador,
                 sesion):
        self.controlador = autenticacion_controlador
        self.ciudad_controlador = ciudad_controlador
        self.categoria_controlador = categoria_controlador
        self.proveedor_controlador = proveedor_controlador
        self.producto_controlador = producto_controlador
        self.sesion = sesion
        self.volver_al_login = False

    def mostrar(self):
        """Muestra el menú. Devuelve True si el usuario pidió 'Cerrar sesión'
        (volver al login) o False si pidió salir de la aplicación."""
        sesion = self.sesion
        raiz = tk.Tk()
        raiz.title("Gestión de Proveedores y Productos")
        e.aplicar_tema(raiz)
        raiz.minsize(1000, 620)
        e.centrar(raiz, 1180, 720)

        def pendiente(nombre):
            return lambda: messagebox.showinfo(
                "En construcción", f"«{nombre}» aún no está implementado.", parent=raiz)

        def terminar(volver):
            self.volver_al_login = volver
            try:
                self.controlador.cerrar_sesion(sesion)  # registra la salida en la bitácora
            except Exception as error:
                messagebox.showerror("Bitácora", f"No se pudo registrar la salida:\n{error}")
            raiz.destroy()

        # Cada sección: nombre -> (descripción, [(título, descripción, acción)])
        secciones = {}
        if sesion.puede_modificar():
            secciones["Entidades"] = ("Registra y administra los datos base del sistema.", [
                ("Proveedores", "Empresas a las que puedes hacer pedidos.",
                 lambda: ProveedoresVista(raiz, self.proveedor_controlador,
                                          self.ciudad_controlador).mostrar()),
                ("Productos", "Catálogo de productos y su categoría.",
                 lambda: ProductosVista(raiz, self.producto_controlador,
                                        self.categoria_controlador).mostrar()),
                ("Ciudades", "Ciudades donde se ubican los proveedores.",
                 lambda: CiudadesVista(raiz, self.ciudad_controlador).mostrar()),
                ("Categorías", "Familias para clasificar los productos.",
                 lambda: CategoriasVista(raiz, self.categoria_controlador).mostrar()),
            ])
            secciones["Transacciones"] = ("Relaciona proveedores con los productos que suministran.", [
                ("Productos por proveedor",
                 "Asigna productos a cada proveedor con precio y días de entrega.",
                 pendiente("Productos por proveedor")),
            ])
        consultas = [
            ("Proveedores con ciudad y productos", "Cada proveedor con su ciudad y lo que suministra."),
            ("Productos con categoría y proveedores", "Productos, su categoría y quién los ofrece, con precio y entrega."),
            ("Bitácora de ingresos con usuario y rol", "Quién ingresó al sistema y con qué rol."),
            ("Proveedores con precio sobre el promedio", "Proveedores con productos más caros que el promedio."),
            ("Productos sin proveedor", "Productos que aún no tienen proveedor asignado."),
        ]
        secciones["Consultas"] = ("Consulta la información registrada.",
                                  [(t, d, pendiente(t)) for t, d in consultas])
        if sesion.puede_modificar():
            reportes = [
                ("Productos de un proveedor", "PDF filtrado por proveedor."),
                ("Proveedores por ciudad", "PDF filtrado por ciudad o departamento."),
                ("Proveedores de un producto", "PDF con proveedores y precios de un producto."),
                ("Productos de una categoría", "PDF con los productos de una categoría."),
                ("Cantidad de productos por categoría", "PDF con totales, filtrado por estado."),
            ]
            secciones["Reportes"] = ("Genera reportes en PDF con filtros.",
                                     [(t, d, pendiente(t)) for t, d in reportes])
        if sesion.es_administrador():
            secciones["Auditoría"] = ("Control de usuarios y accesos (solo Administrador).", [
                ("Gestión de usuarios", "Crea y administra los usuarios del sistema.",
                 pendiente("Gestión de usuarios")),
                ("Bitácora de entrada y salida", "Historial de ingresos y salidas.",
                 pendiente("Bitácora")),
            ])

        # --- Barra lateral ---
        lateral = tk.Frame(raiz, bg=e.OSCURO, width=260)
        lateral.pack(side="left", fill="y")
        lateral.pack_propagate(False)
        tk.Frame(lateral, bg=e.PRIMARIO, width=40, height=4).pack(anchor="w", padx=22, pady=(28, 10))
        tk.Label(lateral, text="Proveedores\ny Productos", bg=e.OSCURO, fg="#FFFFFF",
                 font=(e.FAMILIA, 16, "bold"), justify="left").pack(anchor="w", padx=22, pady=(0, 24))

        botones = {}
        contenido = ttk.Frame(raiz, padding=(36, 30))
        contenido.pack(side="left", fill="both", expand=True)

        def marcar(nombre):
            for n, b in botones.items():
                b.configure(style="LateralActivo.TButton" if n == nombre else "Lateral.TButton")

        def mosaico(padre, titulo, descripcion, comando):
            t = e.tarjeta(padre, cursor="hand2")
            franja = tk.Frame(t, bg=e.PRIMARIO, height=4)
            franja.pack(fill="x")
            cuerpo = tk.Frame(t, bg=e.TARJETA)
            cuerpo.pack(fill="both", expand=True, padx=18, pady=16)
            lt = tk.Label(cuerpo, text=titulo, bg=e.TARJETA, fg=e.TEXTO,
                          font=e.FUENTE_SECCION, anchor="w", justify="left", wraplength=230)
            lt.pack(fill="x")
            ld = tk.Label(cuerpo, text=descripcion, bg=e.TARJETA, fg=e.SUAVE, font=e.FUENTE,
                          anchor="w", justify="left", wraplength=230)
            ld.pack(fill="x", pady=(6, 0))

            def entrar(_ev):
                for w in (cuerpo, lt, ld):
                    w.configure(bg=e.FILA_IMPAR)
                t.configure(highlightbackground=e.PRIMARIO)

            def salir(_ev):
                for w in (cuerpo, lt, ld):
                    w.configure(bg=e.TARJETA)
                t.configure(highlightbackground=e.BORDE)

            for w in (t, franja, cuerpo, lt, ld):
                w.bind("<Button-1>", lambda _ev: comando())
                w.bind("<Enter>", entrar)
                w.bind("<Leave>", salir)
            return t

        def cuadricula(titulo_seccion, acciones):
            if titulo_seccion:
                ttk.Label(contenido, text=titulo_seccion, style="Suave.TLabel",
                          font=e.FUENTE_B).pack(anchor="w", pady=(26, 10))
            rejilla = ttk.Frame(contenido)
            rejilla.pack(fill="x", anchor="n")
            for col in range(3):
                rejilla.columnconfigure(col, weight=1, uniform="m")
            for i, (titulo, descripcion, comando) in enumerate(acciones):
                mosaico(rejilla, titulo, descripcion, comando).grid(
                    row=i // 3, column=i % 3, sticky="nsew", padx=6, pady=6)

        def ir(nombre):
            marcar(nombre)
            for hijo in contenido.winfo_children():
                hijo.destroy()
            if nombre == "Inicio":
                ttk.Label(contenido, text=f"Hola, {sesion.nombre_completo}",
                          style="Pagina.TLabel").pack(anchor="w")
                ttk.Label(contenido, text=f"Ingresaste como {sesion.rol}. Elige una opción "
                                          "del menú o usa un acceso rápido.",
                          style="Suave.TLabel").pack(anchor="w", pady=(4, 0))
                primera = "Entidades" if "Entidades" in secciones else "Consultas"
                cuadricula("Accesos rápidos", secciones[primera][1])
            else:
                descripcion, acciones = secciones[nombre]
                ttk.Label(contenido, text=nombre, style="Pagina.TLabel").pack(anchor="w")
                ttk.Label(contenido, text=descripcion, style="Suave.TLabel").pack(
                    anchor="w", pady=(4, 0))
                cuadricula("", acciones)

        for nombre in ["Inicio"] + list(secciones):
            b = ttk.Button(lateral, text=nombre, style="Lateral.TButton",
                           command=lambda n=nombre: ir(n))
            b.pack(fill="x")
            botones[nombre] = b

        # Parte inferior de la barra lateral: usuario y sesión
        pie = tk.Frame(lateral, bg=e.OSCURO)
        pie.pack(side="bottom", fill="x", pady=(0, 14))
        ttk.Button(pie, text="Salir", style="Lateral.TButton",
                   command=lambda: terminar(False)).pack(fill="x")
        ttk.Button(pie, text="Cerrar sesión", style="Lateral.TButton",
                   command=lambda: terminar(True)).pack(fill="x")
        tk.Frame(pie, bg=e.OSCURO_2, height=1).pack(fill="x", padx=22, pady=12)
        tk.Label(pie, text=sesion.nombre_completo, bg=e.OSCURO, fg="#FFFFFF",
                 font=e.FUENTE_B, anchor="w", wraplength=210, justify="left").pack(
            fill="x", padx=22)
        tk.Label(pie, text=sesion.rol, bg=e.OSCURO, fg="#94A3B8", font=e.FUENTE,
                 anchor="w").pack(fill="x", padx=22)

        ir("Inicio")
        raiz.protocol("WM_DELETE_WINDOW", lambda: terminar(False))  # cerrar con la X
        raiz.mainloop()
        return self.volver_al_login
