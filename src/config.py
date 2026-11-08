"""Configuración del agente (se puede cambiar para la demostración)."""

INTERVALO_SEGUNDOS = 3
ARCHIVO_BD = "monitor_recursos.db"
ARCHIVO_BD_SIMULADO = "monitor_recursos_simulado.db"
UMBRALES_PREDETERMINADOS = {"cpu": 80, "ram": 85, "disco": 90, "bateria": 20}
UMBRALES = dict(UMBRALES_PREDETERMINADOS)
LIMITE_FILAS_TABLA = 50  # cuántas lecturas se muestran en la tabla
