"""Servicio: reglas del negocio de las categorías."""
from dominio.entidades.categoria import Categoria
from dominio.excepciones.regla_dominio_error import ReglaDominioError
from servicios import validaciones as v


class CategoriaServicio:

    def __init__(self, categoria_repositorio):
        self.categoria_repositorio = categoria_repositorio

    def listar(self):
        return self.categoria_repositorio.listar()

    def crear(self, nombre, descripcion, estado):
        categoria = self._validar(None, nombre, descripcion, estado)
        self.categoria_repositorio.insertar(categoria)

    def modificar(self, id_categoria, nombre, descripcion, estado):
        categoria = self._validar(id_categoria, nombre, descripcion, estado)
        self.categoria_repositorio.actualizar(categoria)

    def eliminar(self, id_categoria):
        if self.categoria_repositorio.tiene_productos(id_categoria):
            raise ReglaDominioError(
                "No se puede eliminar: hay productos en esta categoría. "
                "Puedes desmarcar «Activa» para desactivarla.")
        self.categoria_repositorio.eliminar(id_categoria)

    def _validar(self, id_categoria, nombre, descripcion, estado):
        nombre = v.texto(nombre, "El nombre", minimo=3, maximo=50)
        descripcion = v.texto(descripcion, "La descripción", minimo=5, maximo=200,
                              multilinea=True)
        if self.categoria_repositorio.existe_duplicada(nombre, id_categoria or 0):
            raise ReglaDominioError("Ya existe una categoría con ese nombre.")
        return Categoria(id_categoria, nombre, descripcion, bool(estado))
