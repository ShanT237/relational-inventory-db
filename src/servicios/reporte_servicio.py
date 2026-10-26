"""Servicio: arma los 5 reportes en PDF a partir de los filtros que elige el usuario."""
from dominio.entidades.reporte import Reporte
from dominio.excepciones.regla_dominio_error import ReglaDominioError
from servicios import validaciones as v
from servicios.permisos import requiere_modificar
import tempfile
from pathlib import Path

# Estados que ofrece el filtro del reporte "Cantidad de productos por categoría".
_ESTADOS = {"todos": (None, "Todos"), "activos": (True, "Solo activos"),
            "inactivos": (False, "Solo inactivos")}


def _moneda(valor):
    """1500.5 -> '$ 1.500,50' (formato colombiano). None se queda como None."""
    if valor is None:
        return None
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"$ {texto}"


def _estado(activo):
    return "Activo" if activo else "Inactivo"


class ReporteServicio:

    def __init__(self, reporte_repositorio, generador_pdf):
        """generador_pdf(reporte, usuario) -> ruta del archivo creado."""
        self.repositorio = reporte_repositorio
        self.generador_pdf = generador_pdf
        self._constructores = {
            "productos_proveedor": self._productos_proveedor,
            "proveedores_ciudad": self._proveedores_ciudad,
            "proveedores_producto": self._proveedores_producto,
            "productos_categoria": self._productos_categoria,
            "conteo_categorias": self._conteo_categorias,
        }

    def generar(self, sesion, clave, filtros):
        """Valida los filtros, consulta los datos y crea el PDF. Devuelve la ruta."""
        reporte = self.construir(sesion, clave, filtros)
        usuario = f"{sesion.nombre_completo} ({sesion.nombre_usuario})"
        return self.generador_pdf(reporte, usuario)

    def previsualizar(self, sesion, clave, filtros):
        """Crea el PDF en una carpeta temporal (para la vista previa). Devuelve su ruta."""
        reporte = self.construir(sesion, clave, filtros)
        usuario = f"{sesion.nombre_completo} ({sesion.nombre_usuario})"
        carpeta = Path(tempfile.gettempdir()) / "proveedores_vista_previa"
        return self.generador_pdf(reporte, usuario, carpeta=carpeta)

    def descargar(self, sesion, reporte):
        """Crea el PDF de un reporte ya armado. Devuelve la ruta del archivo."""
        requiere_modificar(sesion)
        usuario = f"{sesion.nombre_completo} ({sesion.nombre_usuario})"
        return self.generador_pdf(reporte, usuario)

    def construir(self, sesion, clave, filtros):
        # Hoy solo Administrador y Tradicional generan reportes (igual que el menú).
        # Si el Esporádico también puede, basta cambiar esta línea por requiere_sesion.
        requiere_modificar(sesion)
        constructor = self._constructores.get(clave)
        if constructor is None:
            raise ReglaDominioError("El reporte solicitado no existe.")
        return constructor(filtros or {})

    # ------------------------------------------------------------------ reportes
    def _productos_proveedor(self, filtros):
        id_proveedor = v.seleccion(filtros.get("id_proveedor"), "El proveedor")
        datos = self.repositorio.obtener_proveedor(id_proveedor)
        if datos is None:
            raise ReglaDominioError("El proveedor seleccionado ya no existe.")
        filas = [(codigo, producto, categoria, unidad, _moneda(precio), dias, _estado(estado))
                 for codigo, producto, categoria, unidad, precio, dias, estado
                 in self.repositorio.productos_de_proveedor(id_proveedor)]
        return Reporte(
            clave="productos_proveedor",
            titulo="Productos que suministra un proveedor",
            filtros=[("Proveedor", f"{datos[0]} ({datos[1]})")],
            columnas=["Código", "Producto", "Categoría", "Unidad", "Precio unitario",
                      "Entrega (días)", "Estado"],
            filas=filas, anchos=[1.2, 3, 2, 1.2, 1.6, 1.2, 1],
            a_la_derecha=(4, 5))

    def _proveedores_ciudad(self, filtros):
        ubicacion = v.seleccion(filtros.get("ubicacion"), "La ciudad o el departamento")
        try:
            tipo, valor = ubicacion
        except (TypeError, ValueError):
            raise ReglaDominioError("Selecciona la ciudad o el departamento.") from None
        if tipo == "ciudad":
            ciudad = self.repositorio.obtener_ciudad(valor)
            if ciudad is None:
                raise ReglaDominioError("La ciudad seleccionada ya no existe.")
            filtro = ("Ciudad", f"{ciudad[0]} ({ciudad[1]})")
            datos = self.repositorio.proveedores_por_ubicacion(id_ciudad=valor)
        elif tipo == "departamento":
            filtro = ("Departamento", valor)
            datos = self.repositorio.proveedores_por_ubicacion(departamento=valor)
        else:
            raise ReglaDominioError("Selecciona la ciudad o el departamento.")
        filas = [(departamento, ciudad, proveedor, nit,
                  producto or "Sin productos asignados", _moneda(precio))
                 for departamento, ciudad, proveedor, nit, producto, precio in datos]
        return Reporte(
            clave="proveedores_ciudad",
            titulo="Proveedores por ciudad con sus productos",
            filtros=[filtro],
            columnas=["Departamento", "Ciudad", "Proveedor", "NIT", "Producto",
                      "Precio unitario"],
            filas=filas, anchos=[1.5, 1.5, 3, 1.5, 3, 1.5], a_la_derecha=(5,))

    def _proveedores_producto(self, filtros):
        id_producto = v.seleccion(filtros.get("id_producto"), "El producto")
        datos = self.repositorio.obtener_producto(id_producto)
        if datos is None:
            raise ReglaDominioError("El producto seleccionado ya no existe.")
        filas = [(proveedor, nit, f"{ciudad} ({departamento})", _moneda(precio), dias,
                  _estado(estado))
                 for proveedor, nit, ciudad, departamento, precio, dias, estado
                 in self.repositorio.proveedores_de_producto(id_producto)]
        return Reporte(
            clave="proveedores_producto",
            titulo="Proveedores de un producto con precios",
            filtros=[("Producto", f"{datos[0]} · {datos[1]}")],
            columnas=["Proveedor", "NIT", "Ciudad", "Precio unitario", "Entrega (días)",
                      "Estado"],
            filas=filas, anchos=[3, 1.5, 2.5, 1.6, 1.2, 1], a_la_derecha=(3, 4))

    def _productos_categoria(self, filtros):
        id_categoria = v.seleccion(filtros.get("id_categoria"), "La categoría")
        datos = self.repositorio.obtener_categoria(id_categoria)
        if datos is None:
            raise ReglaDominioError("La categoría seleccionada ya no existe.")
        filas = [(codigo, producto, unidad, descripcion, _estado(estado))
                 for codigo, producto, unidad, descripcion, estado
                 in self.repositorio.productos_de_categoria(id_categoria)]
        return Reporte(
            clave="productos_categoria",
            titulo="Productos de una categoría",
            filtros=[("Categoría", datos[0])],
            columnas=["Código", "Producto", "Unidad", "Descripción", "Estado"],
            filas=filas, anchos=[1.2, 3, 1.2, 5, 1])

    def _conteo_categorias(self, filtros):
        opcion = _ESTADOS.get(filtros.get("estado"))
        if opcion is None:
            raise ReglaDominioError("Selecciona el estado de los productos.")
        activo, etiqueta = opcion
        datos = self.repositorio.cantidad_por_categoria(activo)
        filas = [(categoria, cantidad) for categoria, cantidad in datos]
        if filas:
            filas.append(("TOTAL", sum(cantidad for _, cantidad in datos)))
        return Reporte(
            clave="conteo_categorias",
            titulo="Cantidad de productos por categoría",
            filtros=[("Estado de los productos", etiqueta)],
            columnas=["Categoría", "Cantidad de productos"],
            filas=filas, anchos=[4, 2], a_la_derecha=(1,))
