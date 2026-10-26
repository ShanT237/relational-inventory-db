"""Servicio: reglas del negocio de las categorías."""
from dominio.entidades.categoria import Categoria
from dominio.excepciones.regla_dominio_error import ReglaDominioError
from servicios import validaciones as v
from servicios.permisos import requiere_modificar


class CategoriaServicio:

    def __init__(self, categoria_repositorio):
        self.categoria_repositorio = categoria_repositorio

    def listar(self, sesion):
        requiere_modificar(sesion)
        return self.categoria_repositorio.listar()

    def crear(self, sesion, nombre, descripcion, estado):
        requiere_modificar(sesion)
        categoria = self._validar(None, nombre, descripcion, estado)
        self.categoria_repositorio.insertar(categoria)

    def modificar(self, sesion, id_categoria, nombre, descripcion, estado):
        requiere_modificar(sesion)
        categoria = self._validar(id_categoria, nombre, descripcion, estado)
        self.categoria_repositorio.actualizar(categoria)

    def eliminar(self, sesion, id_categoria):
        requiere_modificar(sesion)
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
