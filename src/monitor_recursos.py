"""
monitor_recursos.py - Incremento 1 (v2) del Agente de Telemetría (Caso 3)

Flujo: leer (psutil) -> evaluar (umbrales) -> guardar (SQLite) -> mostrar,
y se repite cada X segundos (Polling).

Uso:
    python monitor_recursos.py                       # monitoreo real (Ctrl+C para salir)
    python monitor_recursos.py historial             # últimas lecturas guardadas
    python monitor_recursos.py demo                  # demo controlada: casos con resultado esperado
    python monitor_recursos.py simulado              # monitoreo con datos simulados
    python monitor_recursos.py historial simulado    # últimas lecturas de la base simulada

Instalación previa:
    pip install psutil

Qué enseñó el profe y dónde se aplica (detalle en APLICACION_DEL_CURSO.md):
    Teoría de E/S ........ flujo entrada -> validación -> procesamiento -> salida -> errores
    Lab avanzado ......... Provider, Repository, Engine, Service, dataclass, Enum, SQLite con '?',
                           demo controlada y plan de pruebas
    Próximo incremento ... hilo + cola + Tkinter con after (lab avanzado y Reto 8)
"""

import sqlite3
import sys
import time
from dataclasses import dataclass, replace
from datetime import datetime
from enum import Enum
from itertools import cycle
from pathlib import Path

import psutil

# ---------------------------------------------------------------------------
# Configuración (se puede cambiar para la demostración)
# ---------------------------------------------------------------------------
INTERVALO_SEGUNDOS = 3
ARCHIVO_BD = "monitor_recursos.db"
ARCHIVO_BD_SIMULADO = "monitor_recursos_simulado.db"
UMBRALES_PREDETERMINADOS = {"cpu": 80, "ram": 85, "disco": 90, "bateria": 20}
UMBRALES = dict(UMBRALES_PREDETERMINADOS)
# Para provocar una alerta con datos reales, por ejemplo: UMBRALES["ram"] = 10


# ---------------------------------------------------------------------------
# Dominio
# Aplica: Laboratorio avanzado (dominio con dataclass y Enum)
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Proveedor real
# Aplica: Laboratorio avanzado (patrón Provider, como WmiDeviceProvider)
#         Teoría de E/S (el SO expone el recurso; la aplicación lo consulta)
# ---------------------------------------------------------------------------
class ProveedorPsutil:
    """Lee los recursos del equipo. El resto del programa no importa psutil."""

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


# ---------------------------------------------------------------------------
# Motor de alertas
# Aplica: Laboratorio avanzado (RiskEngine: reglas con explicación visible)
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Repositorio
# Aplica: Laboratorio avanzado (SnapshotRepository: SQLite, 'with' y consultas con '?')
# ---------------------------------------------------------------------------
class RepositorioLecturas:
    """Guarda y consulta las lecturas en un archivo SQLite (sin SQL fuera de esta clase)."""

    def __init__(self, ruta=ARCHIVO_BD):
        self.ruta = ruta
        self._crear_esquema()

    def _conectar(self):
        return sqlite3.connect(self.ruta)

    def _crear_esquema(self):
        with self._conectar() as con:  # 'with' confirma la transacción
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS reportes(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    momento TEXT NOT NULL,
                    cpu_percent REAL NOT NULL,
                    ram_percent REAL NOT NULL,
                    disco_percent REAL NOT NULL,
                    bateria_percent REAL,
                    estado_alerta TEXT NOT NULL,
                    creado_via TEXT NOT NULL
                )
                """
            )

    def guardar(self, lectura, estado, creado_via):
        # Los '?' separan el SQL de los valores (evita concatenar texto)
        with self._conectar() as con:
            con.execute(
                "INSERT INTO reportes(momento, cpu_percent, ram_percent, disco_percent,"
                " bateria_percent, estado_alerta, creado_via) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (lectura.momento, lectura.cpu, lectura.ram, lectura.disco,
                 lectura.bateria, estado.value, creado_via),
            )

    def ultimas(self, cantidad=10):
        with self._conectar() as con:
            return con.execute(
                "SELECT id, momento, cpu_percent, ram_percent, disco_percent,"
                " bateria_percent, estado_alerta, creado_via"
                " FROM reportes ORDER BY id DESC LIMIT ?",
                (cantidad,),
            ).fetchall()

    def contar(self):
        with self._conectar() as con:
            return con.execute("SELECT COUNT(*) FROM reportes").fetchone()[0]


# ---------------------------------------------------------------------------
# Servicio
# Aplica: Laboratorio avanzado (DriverMonitorService: coordina el caso de uso
#         con inyección de dependencias) y Teoría (entrada -> procesamiento -> salida)
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Datos de prueba y proveedor simulado
# Aplica: Laboratorio avanzado (demo controlada: se prueba el algoritmo con datos
#         simulados, sin depender del equipo real)
# ---------------------------------------------------------------------------
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


class ProveedorSimulado:
    """Entrega lecturas fijas, una tras otra y en bucle, con la misma interfaz que el real."""

    def __init__(self, casos):
        self._lecturas = cycle([lectura for _, lectura, _ in casos])

    def leer(self):
        momento = datetime.now().isoformat(timespec="seconds")
        return replace(next(self._lecturas), momento=momento)


def demo_controlada():
    """Prueba el motor con casos conocidos y muestra Conforme / No conforme."""
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


# ---------------------------------------------------------------------------
# Salida por consola
# Aplica: Teoría de E/S (salida estándar)
# ---------------------------------------------------------------------------
def texto_bateria(valor):
    return "N/A" if valor is None else f"{valor}%"


def mostrar_resultado(lectura, estado, razones):
    print(f"[{lectura.momento}] CPU {lectura.cpu}% | RAM {lectura.ram}% | "
          f"Disco {lectura.disco}% | Batería {texto_bateria(lectura.bateria)} | {estado.value}")
    for razon in razones:
        print(f"    ALERTA: {razon}")


def mostrar_historial(repositorio):
    filas = repositorio.ultimas(10)
    print(f"Lecturas guardadas: {repositorio.contar()} (se muestran las últimas {len(filas)})")
    for id_, momento, cpu, ram, disco, bateria, estado, origen in filas:
        print(f"#{id_} {momento} | CPU {cpu}% | RAM {ram}% | Disco {disco}% | "
              f"Batería {texto_bateria(bateria)} | {estado} | {origen}")


# ---------------------------------------------------------------------------
# Ciclo principal (Polling) con manejo de errores y cierre controlado
# Aplica: Teoría (errores de E/S: diseñar para fallar sin cerrar el programa)
# ---------------------------------------------------------------------------
def monitorear(servicio):
    print(f"Monitoreo iniciado (cada {INTERVALO_SEGUNDOS} s). Presiona Ctrl+C para salir.")
    try:
        while True:
            try:
                lectura, estado, razones = servicio.ciclo()
                mostrar_resultado(lectura, estado, razones)
            except (OSError, sqlite3.Error, psutil.Error) as error:
                # Un fallo puntual no debe cerrar el programa
                print("Error en el ciclo:", error)
            time.sleep(INTERVALO_SEGUNDOS)
    except KeyboardInterrupt:
        print("\nMonitoreo detenido.")


def main():
    argumentos = sys.argv[1:]
    modo = argumentos[0] if argumentos else "real"

    if modo == "demo":
        demo_controlada()
    elif modo == "historial":
        ruta = ARCHIVO_BD_SIMULADO if "simulado" in argumentos[1:] else ARCHIVO_BD
        mostrar_historial(RepositorioLecturas(ruta))
    elif modo == "simulado":
        servicio = ServicioMonitor(ProveedorSimulado(CASOS),
                                   MotorAlertas(UMBRALES_PREDETERMINADOS),
                                   RepositorioLecturas(ARCHIVO_BD_SIMULADO),
                                   origen="simulado")
        monitorear(servicio)
    elif modo == "real":
        servicio = ServicioMonitor(ProveedorPsutil(), MotorAlertas(UMBRALES),
                                   RepositorioLecturas(), origen="polling")
        monitorear(servicio)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
