# Documentación - Agente de Telemetría y Monitor de Recursos

Material del Avance 2 (Semana 10) del Caso 3, curso Programación de Interfaces y Dispositivos Periféricos.

## Diagramas (`diagramas/`)
| Archivo | Qué muestra |
|---|---|
| `flujo_general.png` | Flujo principal: login, lectura de recursos, alertas, guardado y dashboard, con ciclo de Polling |
| `arquitectura.png` | Capas MVC con Django, agente de telemetría y WebSockets (mejora planificada) |
| `modelo_entidad_relacion.png` | Tablas Usuario, Servidor y Reporte y sus relaciones |
| `polling_vs_websockets.png` | Comparación entre Polling (V1) y WebSockets (V2) |
| `planning_sprints.png` | Sprint 0 a Sprint 3 |
| `fuentes_svg/` | Versiones editables (SVG) de algunos diagramas |

## Mockups (`mockups/`)
`login.png`, `dashboard.png` y `gestion_servidores.png`. Son propuestas visuales, aún no implementadas.

## Entregables (`entregables/`)
Documento Word y presentación del Avance 2.

## Notas
- Nunca subir credenciales ni el archivo `.env` al repositorio.
