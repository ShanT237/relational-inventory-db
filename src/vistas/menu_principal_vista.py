"""Vista: ventana principal. Barra lateral por secciones; las opciones dependen del rol.

Todo se muestra dentro de esta misma ventana (no se abren ventanas encima).
Hay historial de navegación: botones Atrás/Adelante, Alt+←/Alt+→ y los botones
laterales del mouse."""
import sys
import tkinter as tk
from tkinter import messagebox, ttk

from vistas import estilos as e
from vistas.bitacora_vista import BitacoraVista
from vistas.categorias_vista import CategoriasVista
from vistas.ciudades_vista import CiudadesVista
from vistas.consultas_vista import ConsultasVista
from vistas.productos_proveedor_vista import ProductosProveedorVista
from vistas.productos_vista import ProductosVista
from vistas.proveedores_vista import ProveedoresVista
from vistas.usuarios_vista import UsuariosVista


class MenuPrincipalVista:

    def __init__(self, autenticacion_controlador, ciudad_controlador,
                 categoria_controlador, proveedor_controlador, producto_controlador,
                 proveedor_producto_controlador, sesion, consulta_controlador,
                 usuario_controlador, bitacora_controlador):
        self.controlador = autenticacion_controlador
        self.ciudad_controlador = ciudad_controlador
        self.categoria_controlador = categoria_controlador
        self.proveedor_controlador = proveedor_controlador
        self.producto_controlador = producto_controlador
        self.proveedor_producto_controlador = proveedor_producto_controlador
        self.sesion = sesion
        self.consulta_controlador = consulta_controlador
        self.usuario_controlador = usuario_controlador
        self.bitacora_controlador = bitacora_controlador
        self.volver_al_login = False

    def mostrar(self):
        """Muestra el menú. Devuelve True si el usuario pidió 'Cerrar sesión'
        (volver al login) o False si pidió salir de la aplicación."""
        sesion = self.sesion
        raiz = tk.Tk()
        raiz.title("Gestión de Proveedores y Productos")
        e.aplicar_tema(raiz)
        raiz.minsize(1100, 640)
        e.centrar(raiz, 1280, 760)

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

        # --------------------------------------------------------------- navegación
        # Una "página" es (ruta, construir): la ruta es una lista de textos para la barra
        # superior (["Entidades", "Proveedores"]) y construir(zona) dibuja la página.
        estado = {"ruta": None, "construir": None}
        pila_atras, pila_adelante = [], []
        botones = {}

        def pintar(ruta, construir):
            estado["ruta"], estado["construir"] = ruta, construir
            for hijo in zona.winfo_children():
                hijo.destroy()
            construir(zona)
            migas.config(text="   ›   ".join(ruta))
            for n, b in botones.items():
                activo = n == (ruta[0] if ruta[0] in botones else "Inicio")
                b.configure(style="LateralActivo.TButton" if activo else "Lateral.TButton")
            btn_atras.state(["!disabled"] if pila_atras else ["disabled"])
            btn_adelante.state(["!disabled"] if pila_adelante else ["disabled"])

        def abrir(ruta, construir):
            """Va a una página nueva. Si ya estás en ella no hace nada (no se duplica)."""
            if estado["ruta"] == ruta:
                return
            if estado["ruta"] is not None:
                pila_atras.append((estado["ruta"], estado["construir"]))
                del pila_atras[:-30]
            pila_adelante.clear()
            pintar(ruta, construir)

        def atras(_evento=None):
            if not pila_atras:
                return
            pila_adelante.append((estado["ruta"], estado["construir"]))
            pintar(*pila_atras.pop())

        def adelante(_evento=None):
            if not pila_adelante:
                return
            pila_atras.append((estado["ruta"], estado["construir"]))
            pintar(*pila_adelante.pop())

        # --------------------------------------------------------- secciones y roles
        def crud(seccion, titulo, fabrica):
            return lambda: abrir([seccion, titulo], lambda z: fabrica().construir(z))

        # Cada sección: nombre -> (descripción, [(título, descripción, acción)])
        secciones = {}
        if sesion.puede_modificar():
            secciones["Entidades"] = ("Registra y administra los datos base del sistema.", [
                ("Proveedores", "Empresas a las que puedes hacer pedidos.",
                 crud("Entidades", "Proveedores", lambda: ProveedoresVista(
                     self.proveedor_controlador, self.ciudad_controlador))),
                ("Productos", "Catálogo de productos y su categoría.",
                 crud("Entidades", "Productos", lambda: ProductosVista(
                     self.producto_controlador, self.categoria_controlador))),
                ("Ciudades", "Ciudades donde se ubican los proveedores.",
                 crud("Entidades", "Ciudades", lambda: CiudadesVista(self.ciudad_controlador))),
                ("Categorías", "Familias para clasificar los productos.",
                 crud("Entidades", "Categorías", lambda: CategoriasVista(
                     self.categoria_controlador))),
            ])
            secciones["Transacciones"] = (
                "Relaciona proveedores con los productos que suministran.", [
                    ("Productos por proveedor",
                     "Asigna productos a cada proveedor con precio y días de entrega.",
                     crud("Transacciones", "Productos por proveedor",
                          lambda: ProductosProveedorVista(
                              self.proveedor_producto_controlador,
                              self.proveedor_controlador,
                              self.producto_controlador)))])
        consultas = [
            ("proveedores_ciudad_productos", "Proveedores con ciudad y productos",
             "Cada proveedor con su ciudad y lo que suministra."),
            ("productos_categoria_proveedores", "Productos con categoría y proveedores",
             "Productos, su categoría y quién los ofrece, con precio y entrega."),
            ("bitacora_usuarios_roles", "Bitácora de ingresos con usuario y rol",
             "Quién ingresó al sistema y con qué rol."),
            ("proveedores_precio_sobre_promedio", "Proveedores con precio sobre el promedio",
             "Proveedores con productos más caros que el promedio."),
            ("productos_sin_proveedor", "Productos sin proveedor",
             "Productos que aún no tienen proveedor asignado."),
        ]
        def abrir_consulta(identificador, titulo):
            return lambda: abrir(
                ["Consultas", titulo],
                lambda z: ConsultasVista(
                    self.consulta_controlador, identificador, titulo).construir(z))

        secciones["Consultas"] = ("Consulta la información registrada.",
                                  [(t, d, abrir_consulta(i, t)) for i, t, d in consultas])
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
                 crud("Auditoría", "Gestión de usuarios",
                      lambda: UsuariosVista(self.usuario_controlador))),
                ("Bitácora de entrada y salida", "Historial de ingresos y salidas.",
                 crud("Auditoría", "Bitácora de entrada y salida",
                      lambda: BitacoraVista(self.bitacora_controlador))),
            ])

        # ------------------------------------------------------------ barra lateral
        lateral = tk.Frame(raiz, bg=e.OSCURO, width=250)
        lateral.pack(side="left", fill="y")
        lateral.pack_propagate(False)
        tk.Frame(lateral, bg=e.PRIMARIO, width=40, height=4).pack(
            anchor="w", padx=22, pady=(28, 10))
        tk.Label(lateral, text="Proveedores\ny Productos", bg=e.OSCURO, fg="#FFFFFF",
                 font=(e.FAMILIA, 16, "bold"), justify="left").pack(
            anchor="w", padx=22, pady=(0, 24))

        # --------------------------------------------- zona derecha: barra + contenido
        derecha = ttk.Frame(raiz)
        derecha.pack(side="left", fill="both", expand=True)
        barra = tk.Frame(derecha, bg=e.TARJETA)
        barra.pack(fill="x")
        interior = tk.Frame(barra, bg=e.TARJETA)
        interior.pack(fill="x", padx=20, pady=10)
        btn_atras = ttk.Button(interior, text="←  Atrás", command=atras)
        btn_atras.pack(side="left")
        btn_adelante = ttk.Button(interior, text="Adelante  →", command=adelante)
        btn_adelante.pack(side="left", padx=(8, 0))
        migas = ttk.Label(interior, text="", style="Tarjeta.TLabel", font=e.FUENTE_B)
        migas.pack(side="left", padx=(22, 0))
        tk.Frame(derecha, bg=e.BORDE, height=1).pack(fill="x")
        zona = ttk.Frame(derecha, padding=(28, 22))
        zona.pack(fill="both", expand=True)

        # --------------------------------------------------------------- páginas
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

        def cuadricula(contenedor, titulo_seccion, acciones):
            if titulo_seccion:
                ttk.Label(contenedor, text=titulo_seccion, style="Suave.TLabel",
                          font=e.FUENTE_B).pack(anchor="w", pady=(26, 10))
            rejilla = ttk.Frame(contenedor)
            rejilla.pack(fill="x", anchor="n")
            for col in range(3):
                rejilla.columnconfigure(col, weight=1, uniform="m")
            for i, (titulo, descripcion, comando) in enumerate(acciones):
                mosaico(rejilla, titulo, descripcion, comando).grid(
                    row=i // 3, column=i % 3, sticky="nsew", padx=6, pady=6)

        def pagina_inicio(z):
            ttk.Label(z, text=f"Hola, {sesion.nombre_completo}", style="Pagina.TLabel").pack(
                anchor="w")
            ttk.Label(z, text=f"Ingresaste como {sesion.rol}. Elige una opción del menú "
                              "o usa un acceso rápido.", style="Suave.TLabel").pack(
                anchor="w", pady=(4, 0))
            primera = "Entidades" if "Entidades" in secciones else "Consultas"
            cuadricula(z, "Accesos rápidos", secciones[primera][1])

        def pagina_seccion(nombre):
            def construir(z):
                descripcion, acciones = secciones[nombre]
                ttk.Label(z, text=nombre, style="Pagina.TLabel").pack(anchor="w")
                ttk.Label(z, text=descripcion, style="Suave.TLabel").pack(
                    anchor="w", pady=(4, 0))
                cuadricula(z, "", acciones)
            return construir

        botones["Inicio"] = ttk.Button(lateral, text="Inicio", style="Lateral.TButton",
                                       command=lambda: abrir(["Inicio"], pagina_inicio))
        botones["Inicio"].pack(fill="x")
        for nombre in secciones:
            botones[nombre] = ttk.Button(
                lateral, text=nombre, style="Lateral.TButton",
                command=lambda n=nombre: abrir([n], pagina_seccion(n)))
            botones[nombre].pack(fill="x")

        # Parte inferior de la barra lateral: usuario y sesión
        pie = tk.Frame(lateral, bg=e.OSCURO)
        pie.pack(side="bottom", fill="x", pady=(0, 14))
        ttk.Button(pie, text="Salir", style="Lateral.TButton",
                   command=lambda: terminar(False)).pack(fill="x")
        ttk.Button(pie, text="Cerrar sesión", style="Lateral.TButton",
                   command=lambda: terminar(True)).pack(fill="x")
        tk.Frame(pie, bg=e.OSCURO_2, height=1).pack(fill="x", padx=22, pady=12)
        tk.Label(pie, text=sesion.nombre_completo, bg=e.OSCURO, fg="#FFFFFF",
                 font=e.FUENTE_B, anchor="w", wraplength=200, justify="left").pack(
            fill="x", padx=22)
        tk.Label(pie, text=sesion.rol, bg=e.OSCURO, fg="#94A3B8", font=e.FUENTE,
                 anchor="w").pack(fill="x", padx=22)

        # ----------------------------------------- atajos: teclado y botones del mouse
        raiz.bind("<Alt-Left>", atras)
        raiz.bind("<Alt-Right>", adelante)
        self._activar_botones_laterales_mouse(raiz, atras, adelante)

        abrir(["Inicio"], pagina_inicio)
        raiz.protocol("WM_DELETE_WINDOW", lambda: terminar(False))  # cerrar con la X
        raiz.mainloop()
        return self.volver_al_login

    @staticmethod
    def _activar_botones_laterales_mouse(raiz, atras, adelante):
        """Botón lateral 1 = atrás, botón lateral 2 = adelante.

        Tk 8.6 en Windows no entrega esos botones, así que se consulta su estado
        cada 40 ms (solo cuando esta aplicación tiene el foco). En Tk 8.7+ y en
        otros sistemas se usan los eventos <Button-8> y <Button-9>."""
        version = tuple(int(x) for x in str(raiz.tk.call("info", "patchlevel")).split(".")[:2])
        if sys.platform == "win32" and version < (8, 7):
            import ctypes
            leer_tecla = ctypes.windll.user32.GetAsyncKeyState
            antes = {0x05: False, 0x06: False}     # VK_XBUTTON1, VK_XBUTTON2

            def tiene_foco():
                try:
                    return raiz.focus_displayof() is not None
                except KeyError:       # foco en la lista desplegable de un Combobox
                    return True
                except tk.TclError:
                    return False

            def sondear():
                try:
                    foco = tiene_foco()
                    for tecla, accion in ((0x05, atras), (0x06, adelante)):
                        presionado = bool(leer_tecla(tecla) & 0x8000)
                        if foco and presionado and not antes[tecla]:
                            accion()
                        antes[tecla] = presionado
                    raiz.after(40, sondear)
                except tk.TclError:    # la ventana se cerró
                    pass

            raiz.after(100, sondear)
        else:
            for evento, accion in (("<Button-8>", atras), ("<Button-9>", adelante)):
                try:
                    raiz.bind(evento, accion)
                except tk.TclError:
                    pass
