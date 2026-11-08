"""
modelos.py - Los datos que maneja el agente (el Modelo del MVC).
Aplica: Laboratorio avanzado (dominio con dataclass y Enum)
"""

from dataclasses import dataclass
from enum import Enum


class EstadoAlerta(Enum):
    """Limita los valores posibles: evita escribir el estado de formas distintas."""

    NORMAL = "normal"
    ALERTA = "alerta"


@dataclass(frozen=True)
class Lectura:
    """Una 'fotografía' de los recursos en un instante (equivale a un Reporte)."""

    momento: str
    cpu: float
    ram: float
    disco: float
    bateria: float | None  # None si el equipo no tiene batería (PC de escritorio)
