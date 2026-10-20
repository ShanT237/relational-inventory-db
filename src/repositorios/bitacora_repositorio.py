"""Repositorio: acceso a la tabla bitacora."""
from repositorios.conexion_sqlserver import obtener_conexion


class BitacoraRepositorio:

    def registrar_entrada(self, id_usuario):
        """Crea el registro con fecha y hora de entrada. Devuelve su id."""
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute(
                """INSERT INTO bitacora (id_usuario, fecha_hora_entrada)
                   OUTPUT INSERTED.id_bitacora
                   VALUES (?, SYSDATETIME())""",
                id_usuario,
            )
            id_bitacora = cur.fetchone()[0]
            con.commit()
            return id_bitacora
        finally:
            con.close()

    def registrar_salida(self, id_bitacora):
        """Completa la fecha y hora de salida del registro."""
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute(
                "UPDATE bitacora SET fecha_hora_salida = SYSDATETIME() WHERE id_bitacora = ?",
                id_bitacora,
            )
            con.commit()
        finally:
            con.close()
