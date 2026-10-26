# Aplicación de lo enseñado en el curso (Caso 3)

Agente de Telemetría y Monitor de Recursos del Sistema. Este documento muestra qué enseñó el profe y en qué parte del código lo aplicamos.

## 1. Qué enseñó el profe y dónde lo aplicamos

| Tema (fuente) | Dónde en el código | Estado |
|---|---|---|
| Teoría de E/S: entrada → validación → procesamiento → salida → errores | `ServicioMonitor.ciclo()` y `monitorear()` | Hecho |
| Teoría: `pathlib` y errores de E/S | `Path.home().anchor` y `except (OSError, sqlite3.Error, psutil.Error)` | Hecho |
| Lab avanzado: patrón Provider | `ProveedorPsutil` y `ProveedorSimulado` | Hecho |
| Lab avanzado: Repository con SQLite (`with` y consultas con `?`) | `RepositorioLecturas` | Hecho |
| Lab avanzado: motor de reglas con explicación (RiskEngine) | `MotorAlertas` | Hecho |
| Lab avanzado: Service con inyección de dependencias | `ServicioMonitor` | Hecho |
| Lab avanzado: dominio con `dataclass` y `Enum` | `Lectura` y `EstadoAlerta` | Hecho |
| Lab avanzado: demo controlada y plan de pruebas | `python monitor_recursos.py demo` y la sección 3 | Hecho |
| Lab avanzado y Reto 8: hilo, cola y `after` | `Worker` para el Polling | Previsto Sem 13 |
| Lab 7 y Reto 7: Tkinter con `Treeview`, filtro y exportar CSV | Tabla de lecturas con filtro y exportación | Previsto Sem 13 y 14 |
| Lab de captura y Reto individual: TXT y CSV con `flush` | Registro de lecturas en archivo | Previsto Sem 14 |
| Teoría: `subprocess` | `ping` para marcar un servidor «Sin conexión» (opcional) | Previsto Sem 14 |

## 2. Cómo ejecutar

```
pip install psutil
python monitor_recursos.py                      # monitoreo real (Ctrl+C para salir)
python monitor_recursos.py historial            # últimas lecturas guardadas
python monitor_recursos.py demo                 # casos controlados con resultado esperado
python monitor_recursos.py simulado             # monitoreo con datos simulados
python monitor_recursos.py historial simulado   # lecturas de la base simulada
```

## 3. Plan de pruebas (completar al ejecutar)

| ID | Caso | Procedimiento | Resultado esperado | Resultado |
|---|---|---|---|---|
| P01 | Ejecución real | `python monitor_recursos.py` | Una lectura cada unos 4 segundos | Pendiente |
| P02 | Persistencia | Ctrl+C y luego `historial` | Las lecturas siguen guardadas | Pendiente |
| P03 | Casos controlados | `python monitor_recursos.py demo` | 8 de 8 casos conformes | Pendiente |
| P04 | Alerta visible | `python monitor_recursos.py simulado` | Aparece `ALERTA` con su razón | Pendiente |
| P05 | Sin batería | PC de escritorio, o el caso «Sin batería» de la demo | Estado normal y batería N/A | Pendiente |
| P06 | Umbral exacto | Caso «Justo en el umbral» de la demo | Normal (el umbral es estricto) | Pendiente |
| P07 | Cierre limpio | Ctrl+C durante el monitoreo | Mensaje «Monitoreo detenido» sin error | Pendiente |
| P08 | Base eliminada | Borrar el archivo `.db` y ejecutar | Se crea de nuevo y funciona | Pendiente |

## 4. Preguntas de sustentación probables

- **¿Por qué esto no es un driver?** Porque no controla el hardware: consulta con psutil lo que el sistema operativo ya expone.
- **¿Por qué separar Proveedor y Repositorio?** Cada capa cambia por separado, no hay SQL fuera del repositorio y el proveedor se puede reemplazar por uno simulado.
- **¿Para qué el ProveedorSimulado?** Para probar sin depender del equipo y obtener siempre el mismo resultado.
- **¿Por qué usar `?` en las consultas?** Separa el SQL de los valores y evita errores al concatenar texto.
- **¿Por qué `with` con la base de datos?** Confirma la transacción al terminar el bloque.
- **¿Por qué un `Enum` para el estado?** Limita los valores posibles y evita escribirlos de formas distintas.
- **¿Por qué la batería puede ser `None`?** Una PC de escritorio no tiene batería; eso no es un error y la regla se omite.
