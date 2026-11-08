"""
motor.py - Reglas de alerta.
Aplica: Laboratorio avanzado (RiskEngine: reglas con explicación visible)
"""

from modelos import EstadoAlerta


class MotorAlertas:
    """Decide si una lectura es NORMAL o ALERTA y dice por qué."""

    def __init__(self, umbrales):
        self.umbrales = umbrales

    def evaluar(self, lectura):
        razones = []

        # El umbral es estricto: un valor igual al umbral todavía es normal
        if lectura.cpu > self.umbrales["cpu"]:
            razones.append(f"CPU {lectura.cpu}% supera el {self.umbrales['cpu']}%")
        if lectura.ram > self.umbrales["ram"]:
            razones.append(f"RAM {lectura.ram}% supera el {self.umbrales['ram']}%")
        if lectura.disco > self.umbrales["disco"]:
            razones.append(f"Disco {lectura.disco}% supera el {self.umbrales['disco']}%")
        # Si no hay batería (None) esta regla se omite: no es un error
        if lectura.bateria is not None and lectura.bateria < self.umbrales["bateria"]:
            razones.append(f"Batería {lectura.bateria}% bajo el {self.umbrales['bateria']}%")

        estado = EstadoAlerta.ALERTA if razones else EstadoAlerta.NORMAL
        return estado, razones
