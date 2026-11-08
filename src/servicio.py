"""
servicio.py - Coordina un ciclo completo: leer -> evaluar -> guardar.
Aplica: Laboratorio avanzado (DriverMonitorService: coordina el caso de uso con
        inyección de dependencias) y Teoría (entrada -> procesamiento -> salida)
"""


class ServicioMonitor:
    """Un ciclo completo del agente. Recibe sus colaboradores por el constructor."""

    def __init__(self, proveedor, motor, repositorio, origen="polling"):
        self.proveedor = proveedor
        self.motor = motor
        self.repositorio = repositorio
        self.origen = origen

    def ciclo(self):
        lectura = self.proveedor.leer()                         # entrada
        estado, razones = self.motor.evaluar(lectura)           # procesamiento
        self.repositorio.guardar(lectura, estado, self.origen)  # salida: persistencia
        return lectura, estado, razones
