# Kit Two Clocks · la carrera de los dos relojes

Todo lo que Kiro y el equipo necesitan para construir el backend y el dashboard con el stack del hackathon, en paralelo entre dos personas.

## Qué hay y dónde va

Copia cada archivo a la misma ruta dentro de `hackathon-unam/`.

### Steering (Kiro la lee siempre)

| Archivo | Qué es | Acción |
|---|---|---|
| `pregunta.md` | Pregunta, definiciones, cadena, constantes | Reemplaza al anterior |
| `equipo.md` | Dueños de archivos, Git, reglas con Kiro | Reemplaza al anterior |
| `stack-y-arquitectura.md` | Tecnología permitida, carpetas, flujo de datos | Nuevo |
| `contrato-api.md` | 12 endpoints y las 3 funciones que conectan a A con B | Nuevo |

### Skills

| Skill | Para | Quién |
|---|---|---|
| `calculo-carrera` | Tablas base y trampas del tracking | Las dos (esqueleto) |
| `backend-api-datos` | Estructura del backend: carga, estado, caché, 503, JSON, memoria | Las dos |
| `estadistica-intervalos` | Bootstrap, intervalos, mínimos de n, robustez | Las dos |
| `logica-carrera` | Algoritmos de relojes, cadena, resumen y replay | A |
| `logica-giro-aire` | Algoritmos de giros, vuelo, mapas y cinta | B |
| `dashboard-dos-relojes` | Sistema visual, gráficas y animaciones | Las dos |
| `cancha-y-jugadores` | La cancha del replay | A |
| `mapas-de-calor` | Mapas de azul a rojo | B |
| `exploracion-datos-grandes` | (de la práctica, se queda) | Las dos |

Borra la skill vieja `separacion-receptores`.

### Specs (ya escritos: requirements, design y tasks)

| Spec | Quién | Tareas |
|---|---|---|
| `esqueleto` | Juntas, día 1 | 9 |
| `logica-carrera` | A · backend | 11 |
| `dashboard-carrera` | A · frontend | 7 |
| `logica-giro-aire` | B · backend | 10 |
| `dashboard-giro-aire` | B · frontend | 7 |

### Para el equipo

| Archivo | Qué es |
|---|---|
| `docs/equipo/guia-persona-A.md`, `guia-persona-B.md` | Archivos, conexiones, orden recomendado de tareas, checklist |
| `docs/equipo/prompts.md` | Prompts para cada momento y emergencias |
| `docs/equipo/dia-del-evento.md` | Cronograma y prompts de las 3 horas |
| `ESTADO.md` | Memoria compartida (reemplaza al anterior) |

## Paso 0 (juntas, a mano, ~20 minutos)

1. `git tag practica-asistencias` y push del tag.
2. Borrar los specs viejos de `.kiro/specs/` y la skill `separacion-receptores`.
3. Copiar el kit. Revisar que `.gitignore` incluya `data/*.csv`, `scratch/`, `.env`, `.venv/`, `node_modules/`, `dashboard/dist/`.
4. Commit en `main`: "kit two clocks".
5. Prompt "Poner al día la steering vieja" (en `prompts.md`).

## El flujo completo

```
Fase 1  Negocio ......... juntas: aprobar pregunta.md y la división
Fase 2  Datos ........... A: logica-carrera 1        |  B: logica-giro-aire 1
                           ── GO / NO-GO ──  si no pasa: plan B, la asistencia invisible
Esqueleto ............... juntas: esqueleto 1–9 → etiqueta "esqueleto"
Fase 3  Preparación ..... A: relojes + cancha         |  B: giros + MapaCalor
                           ── Merge 1 ──
Fase 4  Modelado ........ A: curvas, H1, cadena, ejemplos + Resumen, P1, Síntesis
                          B: giros, vuelo, H2, H3, mapas, cinta + P2, P3, Cómo leer
                           ── Merge 2: app completa ──
Fase 5  Evaluación ...... integración A↔B, revisión cruzada de números, Renée revisa los replays
Fase 6  Despliegue ...... conexión a la API, verificación con 8 semanas, --check, simulacro
                           ── etiqueta "app-completa" ──
```

El orden exacto, alternando backend y frontend, está en cada guía.

## Por qué no se estorban

- El esqueleto crea desde el día 1 todos los endpoints, tipos, mocks y secciones, con datos de mentira de la forma correcta.
- Cada persona solo toca sus archivos (`equipo.md`). Lo compartido se cambia con un PR pequeño.
- Solo hay 3 conexiones entre A y B, y cada una funciona con datos de mentira hasta que la otra la termine.
- Cada sección conecta su API cuando su endpoint funciona, sin esperar a la otra.

## Cómo se usan los specs en Kiro

Abre el spec en el panel de Kiro: `requirements.md`, `design.md` y `tasks.md` ya están escritos y alineados con el contrato. Ejecuta las tareas una por una (botón de la tarea o prompt "Ejecutar una tarea"). No le pidas que regenere el spec.

## Referencia visual

La maqueta es el lienzo de diseño "La carrera de los dos relojes: dashboard hipotético". Adjunta capturas en el chat de Kiro con el prompt "Construir una sección". El prototipo de Lovable solo sirve de inspiración: su código usa tecnologías prohibidas.
