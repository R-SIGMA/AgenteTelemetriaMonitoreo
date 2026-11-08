"""
demo.py - Demo controlada: prueba el motor con casos conocidos (Conforme / No conforme).
Aplica: Laboratorio avanzado (demo controlada y plan de pruebas)
"""

from config import UMBRALES_PREDETERMINADOS
from modelos import EstadoAlerta, Lectura
from motor import MotorAlertas

CASOS = [
    # (descripción, lectura, estado esperado)
    ("Todo normal", Lectura("", 10.0, 40.0, 50.0, 80.0), EstadoAlerta.NORMAL),
    ("CPU alta", Lectura("", 95.0, 40.0, 50.0, 80.0), EstadoAlerta.ALERTA),
    ("RAM alta", Lectura("", 10.0, 92.0, 50.0, 80.0), EstadoAlerta.ALERTA),
    ("Disco casi lleno", Lectura("", 10.0, 40.0, 95.0, 80.0), EstadoAlerta.ALERTA),
    ("Batería baja", Lectura("", 10.0, 40.0, 50.0, 15.0), EstadoAlerta.ALERTA),
    ("Sin batería (PC de escritorio)", Lectura("", 10.0, 40.0, 50.0, None), EstadoAlerta.NORMAL),
    ("Justo en el umbral (CPU 80%)", Lectura("", 80.0, 40.0, 50.0, 80.0), EstadoAlerta.NORMAL),
    ("Varias alertas a la vez", Lectura("", 95.0, 92.0, 95.0, 10.0), EstadoAlerta.ALERTA),
]


def demo_controlada():
    motor = MotorAlertas(UMBRALES_PREDETERMINADOS)  # umbrales fijos, no los editados
    conformes = 0
    print(f"{'Caso':<32} {'Esperado':<9} {'Obtenido':<9} Resultado")
    for descripcion, lectura, esperado in CASOS:
        obtenido, razones = motor.evaluar(lectura)
        conforme = obtenido == esperado
        conformes += conforme
        print(f"{descripcion:<32} {esperado.value:<9} {obtenido.value:<9} "
              f"{'Conforme' if conforme else 'No conforme'}")
        for razon in razones:
            print(f"    - {razon}")
    print(f"\n{conformes} de {len(CASOS)} casos conformes")
