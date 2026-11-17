"""
repositorio.py - Guarda y consulta las lecturas (todo el SQL vive aquí).
Aplica: Laboratorio avanzado (SnapshotRepository: SQLite, 'with' y consultas con '?')

Nota para el equipo (Mack): aquí se amplía la base de datos. Mantener los nombres
guardar / filtrar / ultimas / contar, porque la interfaz los usa. Para el login se
agregan crear_usuario(nombre, hash) y obtener_usuario(nombre).
"""

import sqlite3

from config import ARCHIVO_BD

COLUMNAS = ("id, momento, cpu_percent, ram_percent, disco_percent, "
            "bateria_percent, estado_alerta, creado_via")


class RepositorioLecturas:
    """Guarda y consulta las lecturas en un archivo SQLite."""

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

    def filtrar(self, estado=None, limite=None):
        """Devuelve las lecturas más recientes primero. estado=None significa todas."""
        consulta = f"SELECT {COLUMNAS} FROM reportes"
        parametros = []
        if estado is not None:
            consulta += " WHERE estado_alerta = ?"
            parametros.append(estado.value)
        consulta += " ORDER BY id DESC"
        if limite is not None:
            consulta += " LIMIT ?"
            parametros.append(limite)
        with self._conectar() as con:
            return con.execute(consulta, parametros).fetchall()

    def ultimas(self, cantidad=10):
        return self.filtrar(None, cantidad)

    def contar(self, estado=None):
        consulta = "SELECT COUNT(*) FROM reportes"
        parametros = []
        if estado is not None:
            consulta += " WHERE estado_alerta = ?"
            parametros.append(estado.value)
        with self._conectar() as con:
            return con.execute(consulta, parametros).fetchone()[0]
