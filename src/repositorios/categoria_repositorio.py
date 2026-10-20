"""Repositorio: acceso a la tabla categoria."""
from dominio.entidades.categoria import Categoria
from repositorios.conexion_sqlserver import obtener_conexion


class CategoriaRepositorio:

    def listar(self):
        """Devuelve todas las categorías ordenadas por nombre."""
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT id_categoria, nombre, descripcion, estado FROM categoria "
                "ORDER BY nombre")
            return [Categoria(f.id_categoria, f.nombre, f.descripcion, bool(f.estado))
                    for f in cur.fetchall()]
        finally:
            con.close()

    def existe_duplicada(self, nombre, excluir_id=0):
        """True si ya hay otra categoría con ese nombre."""
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT COUNT(*) FROM categoria WHERE nombre = ? AND id_categoria <> ?",
                nombre, excluir_id)
            return cur.fetchone()[0] > 0
        finally:
            con.close()

    def tiene_productos(self, id_categoria):
        """True si algún producto pertenece a esa categoría."""
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute("SELECT COUNT(*) FROM producto WHERE id_categoria = ?", id_categoria)
            return cur.fetchone()[0] > 0
        finally:
            con.close()

    def insertar(self, categoria):
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO categoria (nombre, descripcion, estado) VALUES (?, ?, ?)",
                categoria.nombre, categoria.descripcion, 1 if categoria.estado else 0)
            con.commit()
        finally:
            con.close()

    def actualizar(self, categoria):
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute(
                "UPDATE categoria SET nombre = ?, descripcion = ?, estado = ? "
                "WHERE id_categoria = ?",
                categoria.nombre, categoria.descripcion,
                1 if categoria.estado else 0, categoria.id_categoria)
            con.commit()
        finally:
            con.close()

    def eliminar(self, id_categoria):
        con = obtener_conexion()
        try:
            cur = con.cursor()
            cur.execute("DELETE FROM categoria WHERE id_categoria = ?", id_categoria)
            con.commit()
        finally:
            con.close()