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
        # EXPLICAR 3/3 - worker.py (sigue en app.py: _revisar_cola)
        # QUÉ:     repite el ciclo del agente en un hilo aparte.
        # CÓMO:    (1) mientras nadie pida detenerse, (2) llama a ciclo() y deja el
        #          resultado en la cola (si falla, deja el error), (3) espera y repite.
        # POR QUÉ: leer tarda más de 1 segundo y en la ventana la congelaría.
        #          El hilo no toca la ventana: solo deja datos en la cola.
        while not self._detener.is_set():                           # (1)
            try:
                self.cola.put(("lectura", self.servicio.ciclo()))   # (2)
            except Exception as error:  # cualquier fallo se reporta a la ventana
                self.cola.put(("error", str(error)))  # y el hilo sigue vivo
            self._detener.wait(self.intervalo)  # (3) espera que se puede interrumpir

    def detener(self):
        self._detener.set()
