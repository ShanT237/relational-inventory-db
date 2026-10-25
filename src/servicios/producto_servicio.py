"""Servicio: reglas del negocio de los productos."""
from dominio.entidades.producto import Producto
from dominio.excepciones.regla_dominio_error import ReglaDominioError
from servicios import validaciones as v
from servicios.permisos import requiere_modificar


class ProductoServicio:

    def __init__(self, producto_repositorio):
        self.producto_repositorio = producto_repositorio

    def listar(self, sesion):
        requiere_modificar(sesion)
        return self.producto_repositorio.listar()

    def crear(self, sesion, codigo, nombre, id_categoria, descripcion, unidad_medida, estado):
        requiere_modificar(sesion)
        producto = self._validar(None, codigo, nombre, id_categoria, descripcion,
                                 unidad_medida, estado)
        self.producto_repositorio.insertar(producto)

    def modificar(self, sesion, id_producto, codigo, nombre, id_categoria, descripcion,
                  unidad_medida, estado):
        requiere_modificar(sesion)
        producto = self._validar(id_producto, codigo, nombre, id_categoria,
                                 descripcion, unidad_medida, estado)
        self.producto_repositorio.actualizar(producto)

    def eliminar(self, sesion, id_producto):
        requiere_modificar(sesion)
        if self.producto_repositorio.tiene_proveedores(id_producto):
            raise ReglaDominioError(
                "No se puede eliminar: hay proveedores que ofrecen este producto. "
                "Puedes desmarcar «Activo» para desactivarlo.")
        self.producto_repositorio.eliminar(id_producto)

    def _validar(self, id_producto, codigo, nombre, id_categoria, descripcion,
                 unidad_medida, estado):
        codigo = v.codigo(codigo)
        nombre = v.texto(nombre, "El nombre", minimo=2, maximo=200)
        v.seleccion(id_categoria, "La categoría del producto")
        descripcion = v.texto(descripcion, "La descripción", minimo=5, maximo=250,
                              multilinea=True)
        unidad_medida = v.solo_letras(unidad_medida, "La unidad de medida",
                                      minimo=1, maximo=20).lower()
        if self.producto_repositorio.existe_codigo(codigo, id_producto or 0):
            raise ReglaDominioError("Ya existe un producto con ese código.")
        return Producto(id_producto, codigo, nombre, int(id_categoria), descripcion,
                        unidad_medida, bool(estado))
