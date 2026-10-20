"""Script de instalación: crea el usuario Administrador (solo se puede una vez).
Uso, desde la carpeta del proyecto:  python src/crear_admin.py
Requiere haber ejecutado antes 01_crear_tablas.sql y 02_datos_iniciales.sql."""
import getpass

from repositorios.conexion_sqlserver import obtener_conexion
from servicios.seguridad_servicio import SeguridadServicio


def main():
    print("== Crear usuario Administrador ==")
    nombre_usuario = input("Nombre de usuario: ").strip()
    nombre = input("Nombres: ").strip()
    apellido = input("Apellidos: ").strip()
    numero_documento = input("Numero de documento: ").strip()
    contrasena = getpass.getpass("Contrasena: ")

    con = obtener_conexion()
    cur = con.cursor()
    cur.execute("SELECT id_rol FROM rol WHERE nombre = 'Administrador'")
    fila = cur.fetchone()
    if fila is None:
        print("Falta ejecutar 02_datos_iniciales.sql (no existe el rol).")
        return
    id_rol = fila[0]

    cur.execute("SELECT COUNT(*) FROM usuario WHERE id_rol = ?", id_rol)
    if cur.fetchone()[0] > 0:
        print("Ya existe un Administrador. Solo puede haber uno.")
        return

    cur.execute("SELECT TOP 1 id_tipo_documento FROM tipo_documento ORDER BY id_tipo_documento")
    id_tipo_doc = cur.fetchone()[0]

    cur.execute(
        """INSERT INTO usuario (nombre_usuario, nombre, apellido, contrasena_hash,
                                numero_documento, id_rol, id_tipo_documento, creado_por)
           VALUES (?, ?, ?, ?, ?, ?, ?, NULL)""",
        nombre_usuario, nombre, apellido, SeguridadServicio().cifrar(contrasena),
        numero_documento, id_rol, id_tipo_doc,
    )
    con.commit()
    con.close()
    print("Administrador creado correctamente.")


if __name__ == "__main__":
    main()
