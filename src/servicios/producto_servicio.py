"""Servicio: reglas del negocio de los productos."""
from dominio.entidades.producto import Producto
from dominio.excepciones.regla_dominio_error import ReglaDominioError


class ProductoServicio:

    def __init__(self, producto_repositorio):
        self.producto_repositorio = producto_repositorio

    def listar(self):
        return self.producto_repositorio.listar()

    def crear(self, codigo, nombre, id_categoria, descripcion, unidad_medida, estado):
        producto = self._validar(None, codigo, nombre, id_categoria, descripcion,
                                 unidad_medida, estado)
        self.producto_repositorio.insertar(producto)

    def modificar(self, id_producto, codigo, nombre, id_categoria, descripcion,
                  unidad_medida, estado):
        producto = self._validar(id_producto, codigo, nombre, id_categoria,
                                 descripcion, unidad_medida, estado)
        self.producto_repositorio.actualizar(producto)

    def eliminar(self, id_producto):
        if self.producto_repositorio.tiene_proveedores(id_producto):
            raise ReglaDominioError(
                "No se puede eliminar: hay proveedores que ofrecen este producto. "
                "Puedes desmarcar «Activo» para desactivarlo.")
        self.producto_repositorio.eliminar(id_producto)

    def _validar(self, id_producto, codigo, nombre, id_categoria, descripcion,
                 unidad_medida, estado):
        codigo = (codigo or "").strip()
        nombre = (nombre or "").strip()
        descripcion = (descripcion or "").strip() or None
        unidad_medida = (unidad_medida or "").strip() or None

        if not codigo:
            raise ReglaDominioError("El código es obligatorio.")
        if len(codigo) > 30:
            raise ReglaDominioError("El código admite máximo 30 caracteres.")
        if " " in codigo:
            raise ReglaDominioError("El código no debe tener espacios.")
        if not nombre:
            raise ReglaDominioError("El nombre es obligatorio.")
        if len(nombre) > 200:
            raise ReglaDominioError("El nombre admite máximo 200 caracteres.")
        if id_categoria is None:
            raise ReglaDominioError("Selecciona la categoría del producto.")
        if descripcion is not None and len(descripcion) > 250:
            raise ReglaDominioError("La descripción admite máximo 250 caracteres.")
        if unidad_medida is not None and len(unidad_medida) > 20:
            raise ReglaDominioError("La unidad de medida admite máximo 20 caracteres.")
        if self.producto_repositorio.existe_codigo(codigo, id_producto or 0):
            raise ReglaDominioError("Ya existe un producto con ese código.")
        return Producto(id_producto, codigo, nombre, int(id_categoria), descripcion,
                        unidad_medida, bool(estado))
