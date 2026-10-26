"""Controlador: recibe las acciones de la vista de reportes y las pasa al servicio."""


class ReporteControlador:

    def __init__(self, reporte_servicio, sesion):
        self.reporte_servicio = reporte_servicio
        self.sesion = sesion

    def generar(self, clave, filtros):
        """Devuelve la ruta del PDF creado."""
        return self.reporte_servicio.generar(self.sesion, clave, filtros)

    def previsualizar(self, clave, filtros):
        """Devuelve la ruta de un PDF temporal para mostrarlo en pantalla."""
        return self.reporte_servicio.previsualizar(self.sesion, clave, filtros)

    def descargar(self, reporte):
        """Crea el PDF del reporte ya mostrado y devuelve su ruta."""
        return self.reporte_servicio.descargar(self.sesion, reporte)