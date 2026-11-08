"""
worker.py - Hilo que repite el ciclo del agente (el Polling) sin congelar la ventana.
Aplica: Laboratorio avanzado y Reto 8 (productor en un hilo + cola)

Regla del profe: el hilo NO toca la ventana. Deja sus resultados en una cola y la
ventana los lee con after() (ver app.py).
"""

import threading


class ScanWorker(threading.Thread):
    """Productor: lee, evalúa y guarda cada X segundos y avisa por la cola."""

    def __init__(self, servicio, cola, intervalo):
        super().__init__(daemon=True)  # daemon: no impide cerrar el programa
        self.servicio = servicio
        self.cola = cola
        self.intervalo = intervalo
        self._detener = threading.Event()

    def run(self):
        while not self._detener.is_set():
            try:
                self.cola.put(("lectura", self.servicio.ciclo()))
            except Exception as error:  # cualquier fallo se reporta a la ventana
                self.cola.put(("error", str(error)))  # y el hilo sigue vivo
            self._detener.wait(self.intervalo)  # espera que se puede interrumpir

    def detener(self):
        self._detener.set()
