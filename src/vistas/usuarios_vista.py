"""Vista CRUD administrativa para usuarios del sistema."""
from vistas.crud_base import Campo, Columna, CrudVista


class UsuariosVista:

    def __init__(self, controlador):
        self.controlador = controlador

    def construir(self, contenedor):
        c = self.controlador

        def cargar():
            return c.listar()

        def roles():
            return c.listar_roles()

        def tipos_documento():
            return c.listar_tipos_documento()

        columnas = [
            Columna("nombre_usuario", "Usuario", 130),
            Columna("nombre", "Nombre", 140),
            Columna("apellido", "Apellido", 140),
            Columna("tipo_documento", "Tipo documento", 150),
            Columna("numero_documento", "Documento", 130),
            Columna("rol", "Rol", 120),
            Columna("estado_texto", "Estado", 90, True),
        ]
        campos = [
            Campo("nombre_usuario", "Nombre de usuario", obligatorio=True, max_largo=50,
                  ayuda="Entre 3 y 50 caracteres: letras, números, punto, guion o guion bajo."),
            Campo("nombre", "Nombres", obligatorio=True, max_largo=50),
            Campo("apellido", "Apellidos", obligatorio=True, max_largo=50),
            Campo("id_tipo_documento", "Tipo de documento", tipo="combo",
                  opciones=tipos_documento, obligatorio=True),
            Campo("numero_documento", "Número de documento", obligatorio=True, max_largo=20),
            Campo("id_rol", "Rol", tipo="combo", opciones=roles, obligatorio=True),
            Campo("contrasena", "Contraseña", tipo="password", max_largo=128,
                  ayuda="Obligatoria al crear (mínimo 8 caracteres); en edición, déjala "
                        "vacía para conservar la actual."),
            Campo("estado", "Activo", tipo="check"),
        ]

        CrudVista(
            contenedor,
            subtitulo="Crea cuentas, modifica sus datos y cambia su estado de acceso.",
            columnas=columnas,
            campos=campos,
            cargar=cargar,
            crear=lambda v: c.crear(
                v["nombre_usuario"], v["nombre"], v["apellido"],
                v["numero_documento"], v["id_tipo_documento"], v["id_rol"],
                v["contrasena"], v["estado"]),
            modificar=lambda i, v: c.modificar(
                i, v["nombre_usuario"], v["nombre"], v["apellido"],
                v["numero_documento"], v["id_tipo_documento"], v["id_rol"],
                v["contrasena"], v["estado"]),
            eliminar=lambda _id: None,
            texto_nuevo="Nuevo usuario",
            texto_editar="Editar usuario",
            clave_nombre="nombre_usuario",
            permitir_eliminar=False,
        ).construir()
