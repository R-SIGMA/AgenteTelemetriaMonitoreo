"""
app.py - Ventana principal (la Vista del MVC).

Aplica: Laboratorio avanzado y Reto 8 (cola + after: la ventana lee lo que deja el hilo)
        Lab 7 y Reto 7 (Tkinter con Treeview, filtro, filedialog/messagebox y exportar CSV)
        Teoría de E/S (errores sin cerrar el programa, cancelar no crea archivos)

Flujo de la ventana:
    [Iniciar] -> nace un ScanWorker (hilo) -> el hilo deja resultados en la cola
    -> after() revisa la cola cada 150 ms -> la ventana actualiza la tabla.
"""

import csv
import queue
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from config import (ARCHIVO_BD, ARCHIVO_BD_SIMULADO, INTERVALO_SEGUNDOS,
                    LIMITE_FILAS_TABLA, UMBRALES, UMBRALES_PREDETERMINADOS)
from demo import CASOS
from modelos import EstadoAlerta
from motor import MotorAlertas
from proveedor import ProveedorPsutil, ProveedorSimulado
from repositorio import RepositorioLecturas
from servicio import ServicioMonitor
from worker import ScanWorker

REVISION_COLA_MS = 150  # cada cuánto la ventana revisa la cola
FILTROS = {"Todas": None, "Normal": EstadoAlerta.NORMAL, "Alerta": EstadoAlerta.ALERTA}
ENCABEZADOS_CSV = ["id", "momento", "cpu_percent", "ram_percent", "disco_percent",
                   "bateria_percent", "estado_alerta", "creado_via"]


def texto_bateria(valor):
    return "N/A" if valor is None else f"{valor}%"


class AppMonitor:
    """Construye la ventana y reacciona a los botones y a la cola."""

    def __init__(self, ventana, usuario="sin sesión"):
        self.ventana = ventana
        self.usuario = usuario
        self.cola = queue.Queue()   # canal hilo -> ventana
        self.worker = None          # None = monitoreo detenido
        self.repositorio = None

        ventana.title("Agente de Telemetría - Monitor de recursos")
        ventana.geometry("920x560")
        ventana.minsize(780, 460)

        self._construir_interfaz()
        self._cambiar_fuente()  # crea el repositorio y muestra el historial guardado

        ventana.protocol("WM_DELETE_WINDOW", self._cerrar)  # cierre controlado
        ventana.after(REVISION_COLA_MS, self._revisar_cola)  # arranca la revisión de la cola

    # ------------------------------------------------------------------ interfaz
    def _construir_interfaz(self):
        marco = ttk.Frame(self.ventana, padding=12)
        marco.pack(fill="both", expand=True)

        # --- Encabezado
        ttk.Label(marco, text="Monitor de recursos del sistema",
                  font=("Segoe UI", 15, "bold")).pack(anchor="w")
        ttk.Label(marco, text=f"Sesión: {self.usuario}").pack(anchor="w", pady=(0, 8))

        # --- Barra de controles
        barra = ttk.Frame(marco)
        barra.pack(fill="x", pady=(0, 8))

        self.var_fuente = tk.StringVar(value="Real")
        ttk.Label(barra, text="Fuente:").pack(side="left")
        self.combo_fuente = ttk.Combobox(barra, textvariable=self.var_fuente, width=10,
                                         values=["Real", "Simulado"], state="readonly")
        self.combo_fuente.pack(side="left", padx=(4, 12))
        self.combo_fuente.bind("<<ComboboxSelected>>", lambda e: self._cambiar_fuente())

        self.boton_iniciar = ttk.Button(barra, text="Iniciar", command=self.iniciar)
        self.boton_iniciar.pack(side="left", padx=2)
        self.boton_detener = ttk.Button(barra, text="Detener", command=self.detener,
                                        state="disabled")
        self.boton_detener.pack(side="left", padx=2)

        ttk.Button(barra, text="Exportar CSV", command=self.exportar_csv).pack(side="right")
        self.var_filtro = tk.StringVar(value="Todas")
        self.combo_filtro = ttk.Combobox(barra, textvariable=self.var_filtro, width=8,
                                         values=list(FILTROS), state="readonly")
        self.combo_filtro.pack(side="right", padx=(4, 12))
        self.combo_filtro.bind("<<ComboboxSelected>>", lambda e: self._refrescar_tabla())
        ttk.Label(barra, text="Filtro:").pack(side="right")

        # --- Tabla de lecturas
        columnas = ("momento", "cpu", "ram", "disco", "bateria", "estado")
        titulos = ("Hora", "CPU %", "RAM %", "Disco %", "Batería", "Estado")
        contenedor = ttk.Frame(marco)
        contenedor.pack(fill="both", expand=True)
        self.tabla = ttk.Treeview(contenedor, columns=columnas, show="headings", height=14)
        for columna, titulo in zip(columnas, titulos):
            ancho = 190 if columna == "momento" else 100
            self.tabla.heading(columna, text=titulo)
            self.tabla.column(columna, width=ancho, anchor="center")
        # Colores por estado: la etiqueta de cada fila coincide con estado_alerta
        self.tabla.tag_configure("alerta", background="#FBE3E0")
        self.tabla.tag_configure("normal", background="#E6F4EA")
        barra_scroll = ttk.Scrollbar(contenedor, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=barra_scroll.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        barra_scroll.pack(side="right", fill="y")

        # --- Mensajes de estado (feedback para el usuario)
        self.var_estado = tk.StringVar(value="Detenido")
        self.var_alerta = tk.StringVar(value="Sin lecturas todavía")
        self.var_resumen = tk.StringVar(value="")
        ttk.Label(marco, textvariable=self.var_estado,
                  font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(8, 0))
        ttk.Label(marco, textvariable=self.var_alerta).pack(anchor="w")
        ttk.Label(marco, textvariable=self.var_resumen).pack(anchor="w")

    # ------------------------------------------------------------------ fuente de datos
    def _cambiar_fuente(self):
        """Elige de dónde salen los datos y qué base de datos se muestra."""
        if self.var_fuente.get() == "Simulado":
            self.repositorio = RepositorioLecturas(ARCHIVO_BD_SIMULADO)
        else:
            self.repositorio = RepositorioLecturas(ARCHIVO_BD)
        self._refrescar_tabla()

    def _crear_servicio(self):
        """Arma el servicio con los colaboradores de la fuente elegida (inyección)."""
        if self.var_fuente.get() == "Simulado":
            return ServicioMonitor(ProveedorSimulado(CASOS),
                                   MotorAlertas(UMBRALES_PREDETERMINADOS),
                                   self.repositorio, origen="simulado")
        return ServicioMonitor(ProveedorPsutil(), MotorAlertas(UMBRALES),
                               self.repositorio, origen="polling")

    # ------------------------------------------------------------------ botones
    def iniciar(self):
        if self.worker is not None:
            return
        self.worker = ScanWorker(self._crear_servicio(), self.cola, INTERVALO_SEGUNDOS)
        self.worker.start()
        self.boton_iniciar.config(state="disabled")
        self.boton_detener.config(state="normal")
        self.combo_fuente.config(state="disabled")
        self.var_estado.set(f"Monitoreando (cada {INTERVALO_SEGUNDOS} s)...")

    def detener(self):
        if self.worker is None:
            return
        self.worker.detener()  # el hilo termina su ciclo actual y sale
        self.worker = None
        self.boton_iniciar.config(state="normal")
        self.boton_detener.config(state="disabled")
        self.combo_fuente.config(state="readonly")
        self.var_estado.set("Detenido")

    def exportar_csv(self):
        filas = self.repositorio.filtrar(self._estado_filtro(), limite=None)
        if not filas:
            messagebox.showwarning("Sin datos", "No hay lecturas para exportar con este filtro.")
            return
        ruta = filedialog.asksaveasfilename(defaultextension=".csv",
                                            initialfile="lecturas.csv",
                                            filetypes=[("Archivo CSV", "*.csv")])
        if not ruta:  # el usuario canceló: no se crea ningún archivo
            return
        try:
            # utf-8-sig y newline="" para que Excel abra bien las tildes y no duplique saltos
            with open(ruta, "w", newline="", encoding="utf-8-sig") as archivo:
                escritor = csv.writer(archivo)
                escritor.writerow(ENCABEZADOS_CSV)
                escritor.writerows(filas)
        except OSError as error:
            messagebox.showerror("Error al exportar", f"No se pudo guardar el archivo:\n{error}")
            return
        messagebox.showinfo("Exportación lista", f"Se exportaron {len(filas)} lecturas.")

    # ------------------------------------------------------------------ cola y tabla
    def _revisar_cola(self):
        """Lee lo que dejó el hilo. Corre en el hilo de la ventana, por eso es seguro."""
        # EXPLICAR 3/3 (parte 2) - app.py
        # QUÉ:     la ventana lee lo que dejó el hilo en la cola.
        # CÓMO:    (1) saca mensajes de la cola sin esperar, (2) muestra la lectura o el
        #          error, (3) se vuelve a programar con after() cada 150 ms.
        # POR QUÉ: Tkinter solo es seguro desde su propio hilo; por eso la ventana
        #          pregunta a la cola en lugar de que el hilo la actualice.
        try:
            while True:
                tipo, dato = self.cola.get_nowait()                    # (1)
                if tipo == "lectura":
                    self._mostrar_lectura(*dato)                       # (2)
                else:
                    self.var_estado.set(f"Error en el ciclo: {dato}")  # (2)
        except queue.Empty:
            pass  # no hay nada nuevo; se vuelve a revisar enseguida
        self.ventana.after(REVISION_COLA_MS, self._revisar_cola)       # (3)

    def _mostrar_lectura(self, lectura, estado, razones):
        if razones:
            self.var_alerta.set("Última alerta: " + "; ".join(razones))
        else:
            self.var_alerta.set("Última lectura sin alertas")
        self._refrescar_tabla()

    def _estado_filtro(self):
        return FILTROS[self.var_filtro.get()]

    def _refrescar_tabla(self):
        """Vuelve a dibujar la tabla desde la base de datos, respetando el filtro."""
        self.tabla.delete(*self.tabla.get_children())
        for _, momento, cpu, ram, disco, bateria, estado, _origen in self.repositorio.filtrar(
                self._estado_filtro(), LIMITE_FILAS_TABLA):
            self.tabla.insert("", "end", tags=(estado,),
                              values=(momento.replace("T", " "), cpu, ram, disco,
                                      texto_bateria(bateria), estado.upper()))
        total = self.repositorio.contar()
        alertas = self.repositorio.contar(EstadoAlerta.ALERTA)
        self.var_resumen.set(f"Lecturas guardadas: {total}  |  Alertas: {alertas}")

    # ------------------------------------------------------------------ cierre
    def _cerrar(self):
        if self.worker is not None:
            self.worker.detener()
        self.ventana.destroy()
