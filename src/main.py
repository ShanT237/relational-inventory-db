"""Punto de entrada. Aquí se arman las piezas (repositorios -> servicios ->
controladores -> vistas), igual que una clase de configuración."""
from controladores.autenticacion_controlador import AutenticacionControlador
from repositorios.bitacora_repositorio import BitacoraRepositorio
from repositorios.usuario_repositorio import UsuarioRepositorio
from servicios.autenticacion_servicio import AutenticacionServicio
from servicios.seguridad_servicio import SeguridadServicio
from vistas.login_vista import LoginVista
from vistas.menu_principal_vista import MenuPrincipalVista
from controladores.ciudad_controlador import CiudadControlador
from repositorios.ciudad_repositorio import CiudadRepositorio
from servicios.ciudad_servicio import CiudadServicio
from controladores.categoria_controlador import CategoriaControlador
from repositorios.categoria_repositorio import CategoriaRepositorio
from servicios.categoria_servicio import CategoriaServicio


def main():
    # Repositorios
    usuario_repositorio = UsuarioRepositorio()
    bitacora_repositorio = BitacoraRepositorio()
    ciudad_repositorio = CiudadRepositorio()
    categoria_repositorio = CategoriaRepositorio()

    # Servicios
    seguridad_servicio = SeguridadServicio()
    autenticacion_servicio = AutenticacionServicio(
        usuario_repositorio, bitacora_repositorio, seguridad_servicio)
    ciudad_servicio = CiudadServicio(ciudad_repositorio)
    categoria_servicio = CategoriaServicio(categoria_repositorio)

    # Controladores
    autenticacion_controlador = AutenticacionControlador(autenticacion_servicio)
    ciudad_controlador = CiudadControlador(ciudad_servicio)
    categoria_controlador = CategoriaControlador(categoria_servicio)

    # Vistas
    while True:
        sesion = LoginVista(autenticacion_controlador).mostrar()
        if sesion is None:                      # cerró la ventana de login
            break
        menu = MenuPrincipalVista(autenticacion_controlador, ciudad_controlador,
                                  categoria_controlador, sesion)
        if not menu.mostrar():
            break                               # False = salir de la aplicación                     # False = salir de la aplicación


if __name__ == "__main__":
    main()
