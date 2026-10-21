"""Punto de entrada. Aquí se arman las piezas (repositorios -> servicios ->
controladores -> vistas), igual que una clase de configuración."""
from controladores.autenticacion_controlador import AutenticacionControlador
from controladores.categoria_controlador import CategoriaControlador
from controladores.ciudad_controlador import CiudadControlador
from controladores.producto_controlador import ProductoControlador
from controladores.proveedor_producto_controlador import ProveedorProductoControlador
from controladores.proveedor_controlador import ProveedorControlador
from repositorios.bitacora_repositorio import BitacoraRepositorio
from repositorios.categoria_repositorio import CategoriaRepositorio
from repositorios.ciudad_repositorio import CiudadRepositorio
from repositorios.producto_repositorio import ProductoRepositorio
from repositorios.proveedor_producto_repositorio import ProveedorProductoRepositorio
from repositorios.proveedor_repositorio import ProveedorRepositorio
from repositorios.usuario_repositorio import UsuarioRepositorio
from servicios.autenticacion_servicio import AutenticacionServicio
from servicios.categoria_servicio import CategoriaServicio
from servicios.ciudad_servicio import CiudadServicio
from servicios.producto_servicio import ProductoServicio
from servicios.proveedor_producto_servicio import ProveedorProductoServicio
from servicios.proveedor_servicio import ProveedorServicio
from servicios.seguridad_servicio import SeguridadServicio
from vistas.login_vista import LoginVista
from vistas.menu_principal_vista import MenuPrincipalVista


def main():
    # Repositorios
    usuario_repositorio = UsuarioRepositorio()
    bitacora_repositorio = BitacoraRepositorio()
    ciudad_repositorio = CiudadRepositorio()
    categoria_repositorio = CategoriaRepositorio()
    proveedor_repositorio = ProveedorRepositorio()
    producto_repositorio = ProductoRepositorio()
    proveedor_producto_repositorio = ProveedorProductoRepositorio()

    # Servicios
    seguridad_servicio = SeguridadServicio()
    autenticacion_servicio = AutenticacionServicio(
        usuario_repositorio, bitacora_repositorio, seguridad_servicio)
    ciudad_servicio = CiudadServicio(ciudad_repositorio)
    categoria_servicio = CategoriaServicio(categoria_repositorio)
    proveedor_servicio = ProveedorServicio(proveedor_repositorio)
    producto_servicio = ProductoServicio(producto_repositorio)
    proveedor_producto_servicio = ProveedorProductoServicio(proveedor_producto_repositorio)

    # Controladores
    autenticacion_controlador = AutenticacionControlador(autenticacion_servicio)
    ciudad_controlador = CiudadControlador(ciudad_servicio)
    categoria_controlador = CategoriaControlador(categoria_servicio)
    proveedor_controlador = ProveedorControlador(proveedor_servicio)
    producto_controlador = ProductoControlador(producto_servicio)
    proveedor_producto_controlador = ProveedorProductoControlador(proveedor_producto_servicio)

    # Vistas
    while True:
        sesion = LoginVista(autenticacion_controlador).mostrar()
        if sesion is None:                      # cerró la ventana de login
            break
        menu = MenuPrincipalVista(autenticacion_controlador, ciudad_controlador,
                                  categoria_controlador, proveedor_controlador,
                                  producto_controlador,
                                  proveedor_producto_controlador, sesion)
        if not menu.mostrar():
            break                               # False = salir de la aplicación


if __name__ == "__main__":
    main()
