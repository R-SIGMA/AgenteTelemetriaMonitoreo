"""
proveedor.py - De dónde salen las lecturas.
Aplica: Laboratorio avanzado (patrón Provider, como WmiDeviceProvider)
        Teoría de E/S (el SO expone el recurso; la aplicación lo consulta)
"""

from datetime import datetime
from dataclasses import replace
from itertools import cycle
from pathlib import Path

import psutil

from modelos import Lectura


class ProveedorPsutil:
    """Lee los recursos reales del equipo. El resto del programa no importa psutil."""

    def __init__(self):
        # Aplica: Teoría (pathlib). Raíz del disco: 'C:\\' en Windows y '/' en Linux o Mac
        self.raiz_disco = Path.home().anchor

    def leer(self):
        bateria = None
        # sensors_battery no existe en todos los sistemas, por eso se consulta con cuidado
        lector_bateria = getattr(psutil, "sensors_battery", None)
        if lector_bateria is not None:
            info = lector_bateria()
            if info is not None:
                bateria = round(info.percent, 1)

        return Lectura(
            momento=datetime.now().isoformat(timespec="seconds"),
            cpu=psutil.cpu_percent(interval=1),  # mide durante 1 segundo
            ram=psutil.virtual_memory().percent,
            disco=psutil.disk_usage(self.raiz_disco).percent,
            bateria=bateria,
        )


class ProveedorSimulado:
    """Entrega lecturas fijas, una tras otra y en bucle, con la misma interfaz que el real."""

    def __init__(self, casos):
        self._lecturas = cycle([lectura for _, lectura, _ in casos])

    def leer(self):
        momento = datetime.now().isoformat(timespec="seconds")
        return replace(next(self._lecturas), momento=momento)
