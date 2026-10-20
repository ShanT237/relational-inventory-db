"""Servicio: reglas del negocio del inicio y cierre de sesión."""
from dominio.entidades.sesion import Sesion
from dominio.excepciones.regla_dominio_error import ReglaDominioError


class AutenticacionServicio:

    def __init__(self, usuario_repositorio, bitacora_repositorio, seguridad_servicio):
        self.usuario_repositorio = usuario_repositorio
        self.bitacora_repositorio = bitacora_repositorio
        self.seguridad_servicio = seguridad_servicio

    def iniciar_sesion(self, nombre_usuario, contrasena):
        """Valida las credenciales y abre el registro en la bitácora."""
        if not nombre_usuario or not contrasena:
            raise ReglaDominioError("Escribe el usuario y la contraseña.")

        usuario = self.usuario_repositorio.obtener_por_nombre_usuario(nombre_usuario)
        # Mismo mensaje para usuario inexistente y contraseña errónea
        if usuario is None or not self.seguridad_servicio.verificar(
                contrasena, usuario.contrasena_hash):
            raise ReglaDominioError("Usuario o contraseña incorrectos.")
        if not usuario.estado:
            raise ReglaDominioError("Este usuario está inactivo.")

        id_bitacora = self.bitacora_repositorio.registrar_entrada(usuario.id_usuario)
        return Sesion(
            id_usuario=usuario.id_usuario,
            nombre_usuario=usuario.nombre_usuario,
            nombre_completo=f"{usuario.nombre} {usuario.apellido}",
            rol=usuario.rol,
            id_bitacora=id_bitacora,
        )

    def cerrar_sesion(self, sesion):
        """Completa la fecha y hora de salida en la bitácora."""
        self.bitacora_repositorio.registrar_salida(sesion.id_bitacora)
