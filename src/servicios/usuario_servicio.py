"""Servicio: reglas de negocio y autorización para gestionar usuarios."""
import re

from dominio.excepciones.regla_dominio_error import ReglaDominioError
from servicios import validaciones as v
from servicios.permisos import requiere_administrador

_NOMBRE_USUARIO = re.compile(r"^[A-Za-z0-9_.-]{3,50}$")
_DOCUMENTO = re.compile(r"^[A-Za-z0-9.-]{4,20}$")
_ROLES = {"Administrador", "Tradicional", "Esporadico", "Esporádico"}


class UsuarioServicio:

    def __init__(self, usuario_repositorio, seguridad_servicio):
        self.usuario_repositorio = usuario_repositorio
        self.seguridad_servicio = seguridad_servicio

    def listar(self, sesion):
        requiere_administrador(sesion)
        return self.usuario_repositorio.listar_usuarios()

    def listar_roles(self, sesion):
        requiere_administrador(sesion)
        return self.usuario_repositorio.listar_roles()

    def listar_tipos_documento(self, sesion):
        requiere_administrador(sesion)
        return self.usuario_repositorio.listar_tipos_documento()

    def crear(self, sesion, nombre_usuario, nombre, apellido, numero_documento,
              id_tipo_documento, id_rol, contrasena, estado):
        requiere_administrador(sesion)
        if self._nombre_rol(id_rol) == "Administrador":
            raise ReglaDominioError(
                "No se pueden crear usuarios con el rol Administrador.")
        datos = self._validar_datos(
            nombre_usuario, nombre, apellido, numero_documento,
            id_tipo_documento, id_rol, estado)
        datos["contrasena_hash"] = self._cifrar_contrasena(contrasena)
        datos["creado_por"] = sesion.id_usuario
        try:
            self.usuario_repositorio.insertar_usuario(datos)
        except ValueError as error:
            raise ReglaDominioError(str(error)) from error

    def modificar(self, sesion, id_usuario, nombre_usuario, nombre, apellido,
                  numero_documento, id_tipo_documento, id_rol, contrasena, estado):
        requiere_administrador(sesion)
        existente = self.usuario_repositorio.obtener_para_editar(id_usuario)
        if existente is None:
            raise ReglaDominioError("El usuario seleccionado ya no existe.")

        datos = self._validar_datos(
            nombre_usuario, nombre, apellido, numero_documento,
            id_tipo_documento, id_rol, estado, excluir_id=id_usuario)
        rol_actual = existente["rol"]
        rol_nuevo = self._nombre_rol(datos["id_rol"])
        if rol_actual == "Administrador" and rol_nuevo != "Administrador":
            raise ReglaDominioError("No se puede cambiar el rol del único Administrador.")
        if rol_actual == "Administrador" and not datos["estado"]:
            raise ReglaDominioError("No se puede desactivar al único Administrador.")
        if rol_nuevo == "Administrador" and rol_actual != "Administrador":
            raise ReglaDominioError("No se puede asignar el rol Administrador a otro usuario.")

        if contrasena:
            datos["contrasena_hash"] = self._cifrar_contrasena(contrasena)
        try:
            self.usuario_repositorio.actualizar_usuario(id_usuario, datos)
        except ValueError as error:
            raise ReglaDominioError(str(error)) from error

    def _validar_datos(self, nombre_usuario, nombre, apellido, numero_documento,
                       id_tipo_documento, id_rol, estado, excluir_id=None):
        nombre_usuario = (nombre_usuario or "").strip()
        if not _NOMBRE_USUARIO.fullmatch(nombre_usuario):
            raise ReglaDominioError(
                "El usuario debe tener entre 3 y 50 caracteres: letras, números, punto, "
                "guion o guion bajo.")
        nombre = v.solo_letras(nombre, "El nombre", minimo=2, maximo=50)
        apellido = v.solo_letras(apellido, "El apellido", minimo=2, maximo=50)
        numero_documento = (numero_documento or "").strip()
        if (not _DOCUMENTO.fullmatch(numero_documento)
                or not any(caracter.isalnum() for caracter in numero_documento)):
            raise ReglaDominioError(
                "El documento debe tener entre 4 y 20 caracteres alfanuméricos, punto o guion.")
        if self.usuario_repositorio.existe_nombre_usuario(nombre_usuario, excluir_id):
            raise ReglaDominioError("Ya existe un usuario con ese nombre de usuario.")
        if self.usuario_repositorio.existe_documento(numero_documento, excluir_id):
            raise ReglaDominioError("Ya existe un usuario con ese número de documento.")

        try:
            id_tipo_documento = int(id_tipo_documento)
        except (TypeError, ValueError) as error:
            raise ReglaDominioError("Selecciona un tipo de documento válido.") from error
        tipos_documento = dict(self.usuario_repositorio.listar_tipos_documento())
        if id_tipo_documento not in tipos_documento:
            raise ReglaDominioError("Selecciona un tipo de documento válido.")
        rol = self._nombre_rol(id_rol)
        if rol not in _ROLES:
            raise ReglaDominioError("Selecciona un rol válido.")
        return {
            "nombre_usuario": nombre_usuario,
            "nombre": nombre,
            "apellido": apellido,
            "numero_documento": numero_documento,
            "id_tipo_documento": int(id_tipo_documento),
            "id_rol": int(id_rol),
            "estado": bool(estado),
        }

    def _nombre_rol(self, id_rol):
        roles = dict(self.usuario_repositorio.listar_roles())
        try:
            return roles[int(id_rol)]
        except (KeyError, TypeError, ValueError) as error:
            raise ReglaDominioError("Selecciona un rol válido.") from error

    def _cifrar_contrasena(self, contrasena):
        contrasena = contrasena or ""
        if len(contrasena) < 8:
            raise ReglaDominioError("La contraseña debe tener al menos 8 caracteres.")
        if len(contrasena) > 128:
            raise ReglaDominioError("La contraseña admite máximo 128 caracteres.")
        return self.seguridad_servicio.cifrar(contrasena)
