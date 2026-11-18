# AgenteTelemetriaMonitoreo
Proyecto del curso Programación de Interfases y Dispositivos Periféricos. Agente web para monitorear los recursos del sistema, enviar alertas y generar reportes.

## Configuración

1. Copia `.env.example` a `.env`.
2. Activa el entorno virtual:
   `.\.venv\Scripts\activate`
3. Genera una clave y pégala en `SECRET_KEY`:
   `python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"`
4. Modifica `DEBUG` y `ALLOWED_HOSTS` según sea necesario.

**IMPORTANTE:** Aunque `.env` ya está siendo ignorado por Git, evita subirlo o compartirlo por cualquier medio.
