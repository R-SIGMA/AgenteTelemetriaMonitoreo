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
        # EXPLICAR 1/3 - servicio.py
        # QUÉ:     hace un ciclo completo del agente.
        # CÓMO:    (1) pide una lectura, (2) la evalúa, (3) la guarda.
        # POR QUÉ: cada paso lo hace una clase distinta; si cambia la base de datos,
        #          solo se toca el repositorio.
        lectura = self.proveedor.leer()                         # (1) entrada
        estado, razones = self.motor.evaluar(lectura)           # (2) procesamiento
        self.repositorio.guardar(lectura, estado, self.origen)  # (3) salida: persistencia
        return lectura, estado, razones
