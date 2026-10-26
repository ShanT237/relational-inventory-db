"""Controlador: acciones de gestión de usuarios."""


class UsuarioControlador:

    def __init__(self, usuario_servicio, sesion):
        self.usuario_servicio = usuario_servicio
        self.sesion = sesion

    def listar(self):
        return self.usuario_servicio.listar(self.sesion)

    def listar_roles(self):
        return self.usuario_servicio.listar_roles(self.sesion)

    def listar_tipos_documento(self):
        return self.usuario_servicio.listar_tipos_documento(self.sesion)

    def crear(self, nombre_usuario, nombre, apellido, numero_documento,
              id_tipo_documento, id_rol, contrasena, estado):
        self.usuario_servicio.crear(
            self.sesion, nombre_usuario, nombre, apellido, numero_documento,
            id_tipo_documento, id_rol, contrasena, estado)

    def modificar(self, id_usuario, nombre_usuario, nombre, apellido,
                  numero_documento, id_tipo_documento, id_rol, contrasena, estado):
        self.usuario_servicio.modificar(
            self.sesion, id_usuario, nombre_usuario, nombre, apellido,
            numero_documento, id_tipo_documento, id_rol, contrasena, estado)
