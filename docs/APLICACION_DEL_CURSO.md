# Aplicación de lo enseñado en el curso (Caso 3)

Agente de Telemetría y Monitor de Recursos del Sistema. Este documento muestra qué enseñó el profe y en qué parte del código lo aplicamos.

## 1. Qué enseñó el profe y dónde lo aplicamos

| Tema (fuente) | Dónde en el código | Estado |
|---|---|---|
| Teoría de E/S: entrada → validación → procesamiento → salida → errores | `ServicioMonitor.ciclo()` (servicio.py) y `ScanWorker.run()` (worker.py) | Hecho |
| Teoría: `pathlib` y errores de E/S | `Path.home().anchor` (proveedor.py) y el manejo de errores del hilo | Hecho |
| Lab avanzado: patrón Provider | `ProveedorPsutil` y `ProveedorSimulado` (proveedor.py) | Hecho |
| Lab avanzado: Repository con SQLite (`with` y consultas con `?`) | `RepositorioLecturas` (repositorio.py) | Hecho |
| Lab avanzado: motor de reglas con explicación (RiskEngine) | `MotorAlertas` (motor.py) | Hecho |
| Lab avanzado: Service con inyección de dependencias | `ServicioMonitor` (servicio.py) | Hecho |
| Lab avanzado: dominio con `dataclass` y `Enum` | `Lectura` y `EstadoAlerta` (modelos.py) | Hecho |
| Lab avanzado: demo controlada y plan de pruebas | `python src/main.py demo` (demo.py) y la sección 4 | Hecho |
| Lab avanzado y Reto 8: hilo, cola y `after` | `ScanWorker` (worker.py) y `AppMonitor._revisar_cola` (app.py) | Hecho |
| Lab 7 y Reto 7: Tkinter con `Treeview`, filtro, `filedialog`, `messagebox` y exportar CSV | `AppMonitor` (app.py) | Hecho |
| MVC pedido por el profe | Modelo: modelos, motor y repositorio. Vista: app.py. Controlador: servicio, worker y main | Hecho |
| Lab de captura y Reto individual: TXT y CSV con `flush` | Registro de lecturas en archivo de texto | Previsto |
| Login con contraseña protegida y base de datos ampliada | login.py y repositorio.py (usuarios) | En desarrollo (compañeros) |

## 2. Estructura de archivos

```
src/
  main.py          arranca la ventana (o la demo con el argumento demo)
  config.py        intervalo, umbrales y nombres de las bases de datos
  modelos.py       Lectura y EstadoAlerta
  proveedor.py     ProveedorPsutil (real) y ProveedorSimulado
  motor.py         MotorAlertas: aplica los umbrales y explica el motivo
  repositorio.py   RepositorioLecturas: todo el SQL (guardar, filtrar, contar)
  servicio.py      ServicioMonitor: leer, evaluar y guardar
  worker.py        ScanWorker: hilo que repite el ciclo y avisa por una cola
  app.py           AppMonitor: ventana con tabla, filtro, exportar CSV
  demo.py          casos de prueba controlados
```

## 3. Cómo ejecutar

```
pip install psutil
python src/main.py          # abre la ventana
python src/main.py demo     # demo controlada en consola
```

La versión de consola del Incremento 1 (`monitor_recursos.py`) sigue funcionando. El Incremento 2 separa sus clases en módulos y agrega la ventana.

## 4. Plan de pruebas (completar al ejecutar)

| ID | Caso | Procedimiento | Resultado esperado | Resultado |
|---|---|---|---|---|
| P01 | Casos controlados | `python src/main.py demo` | 8 de 8 casos conformes | Pendiente |
| P02 | Abrir la ventana | `python src/main.py` | Aparece la ventana con la tabla | Pendiente |
| P03 | Monitoreo real | Fuente Real, Iniciar | Una fila nueva cada unos 4 segundos | Pendiente |
| P04 | Alertas visibles | Fuente Simulado, Iniciar | Filas en rojo con ALERTA y el motivo en «Última alerta» | Pendiente |
| P05 | Ventana sin congelarse | Mover la ventana mientras monitorea | La ventana responde siempre | Pendiente |
| P06 | Filtro | Elegir Alerta y luego Normal | La tabla muestra solo ese estado | Pendiente |
| P07 | Exportar CSV | Exportar CSV y abrirlo en Excel | Encabezado, filas y tildes correctas | Pendiente |
| P08 | Cancelar exportación | Exportar CSV y cancelar | No se crea ningún archivo | Pendiente |
| P09 | Exportar sin datos | Fuente sin lecturas y Exportar CSV | Aviso «Sin datos» | Pendiente |
| P10 | Detener | Pulsar Detener | No se agregan más filas y los botones se restablecen | Pendiente |
| P11 | Cierre limpio | Cerrar con la X durante el monitoreo | Se cierra sin error | Pendiente |
| P12 | Fallo en la lectura | Error simulado en el proveedor | Se muestra el error y el hilo sigue vivo | Pendiente |
| P13 | Sin batería | PC de escritorio | Batería N/A y estado normal | Pendiente |

## 5. Preguntas de sustentación probables

- **¿Por qué esto no es un driver?** Porque no controla el hardware: consulta con psutil lo que el sistema operativo ya expone.
- **¿Por qué un hilo?** La lectura tarda más de un segundo; si corriera en la ventana, esta se congelaría.
- **¿Por qué una cola?** Es la forma segura de pasar datos de un hilo a otro.
- **¿Por qué `after` y no actualizar la ventana desde el hilo?** Tkinter no es seguro entre hilos: solo el hilo de la ventana toca los widgets.
- **¿Por qué el hilo es `daemon`?** Para que no impida cerrar el programa.
- **¿Por qué `Event.wait` y no `time.sleep`?** Porque se puede interrumpir al detener y el hilo no queda esperando.
- **¿Por qué la tabla se redibuja desde la base de datos?** Para tener una sola fuente de verdad: la tabla, el filtro y el CSV leen lo mismo.
- **¿Por qué separar en módulos?** Cada capa cambia por separado y se puede probar sola; es el MVC que pidió el profe.
- **¿Para qué el ProveedorSimulado?** Para probar sin depender del equipo y obtener siempre el mismo resultado.
- **¿Por qué `?` en las consultas y `with` en SQLite?** Los `?` separan el SQL de los valores; `with` confirma la transacción.
- **¿Por qué la batería puede ser `None`?** Una PC de escritorio no tiene batería; no es un error y la regla se omite.
