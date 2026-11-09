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
        # EXPLICAR 2/3 - motor.py
        # QUÉ:     decide si la lectura es NORMAL o ALERTA y dice por qué.
        # CÓMO:    (1) revisa cada recurso contra su umbral y agrega un motivo si lo pasa;
        #          (2) si la lista de motivos tiene algo, es ALERTA; si está vacía, NORMAL.
        # POR QUÉ: guardar los motivos permite explicar la alerta, no solo avisarla.
        razones = []

        # (1) Cada regla compara un recurso con su umbral.
        # El umbral es estricto: un valor igual al umbral todavía es normal.
        if lectura.cpu > self.umbrales["cpu"]:
            razones.append(f"CPU {lectura.cpu}% supera el {self.umbrales['cpu']}%")
        if lectura.ram > self.umbrales["ram"]:
            razones.append(f"RAM {lectura.ram}% supera el {self.umbrales['ram']}%")
        if lectura.disco > self.umbrales["disco"]:
            razones.append(f"Disco {lectura.disco}% supera el {self.umbrales['disco']}%")
        # Si no hay batería (None) esta regla se omite: no es un error
        if lectura.bateria is not None and lectura.bateria < self.umbrales["bateria"]:
            razones.append(f"Batería {lectura.bateria}% bajo el {self.umbrales['bateria']}%")

        # (2) Con al menos un motivo es ALERTA; sin motivos, NORMAL.
        estado = EstadoAlerta.ALERTA if razones else EstadoAlerta.NORMAL
        return estado, razones
