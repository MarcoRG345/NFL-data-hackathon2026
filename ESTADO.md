# ESTADO del proyecto

Memoria compartida del equipo y de los dos Kiros. Cada persona escribe solo en su sección. Lo más nuevo, arriba.

## Decisiones tomadas

| Fecha | Decisión | Quién |
|---|---|---|
| | Pregunta central: la carrera de los dos relojes (ver `pregunta.md`) | Las dos |
| | GO / NO-GO: | Las dos |

## Persona A · carrera y cancha

**Tarea actual:** —
**Funciones reales disponibles para B:** `relojes.resultado_por_jugada()` → (pendiente)

| Fecha | Tarea | Qué quedó | Pendiente |
|---|---|---|---|
| 2026-11-20 | Esqueleto 4 y 5 | Esquemas, routers y `calculos/` de mentira; `backend/estado.py`; `scratch/verifica_esqueleto.py` (36/36 OK con app temporal) | A2 registra los routers en `main.py`; tareas 1–3 del esqueleto |

## Persona B · giro, aire y mapas

**Tarea actual:** —
**Funciones reales disponibles para A:** `giros.giro_por_cuadro(cuadros)` → (pendiente) · `vuelo.sigue_libre_por_jugada()` → (pendiente)

| Fecha | Tarea | Qué quedó | Pendiente |
|---|---|---|---|
| | | | |

## Números clave (los oficiales, con su n)

| Número | Valor | n | Fuente |
|---|---|---|---|
| H1: conversión gana receptor vs gana defensa (3.º/4.º) | | | `scratch/resultados-carrera.md` |
| H2: separación ganada, giro brusco vs sin giro (media) | | | `scratch/resultados-giro-aire.md` |
| H3: % completo, abierto vs cerrado al lanzar | | | `scratch/resultados-giro-aire.md` |
| Carga con 8 semanas: tiempo y memoria | (pendiente, tarea 9) | | `ESTADO.md` |
| Carga con 1 semana (`DATOS_SEMANAS=1`, Linux) | 3.5 s; pico RSS 194 MB; `cuadros` 686,814 filas / 33.0 MB; `eventos` 1,100 filas; `scouting` 45.7 MB; `plays` 8.5 MB. Excluidas: 72 "No Play", 3 sin `ball_snap` | 1,100 jugadas (16 partidos) | tarea 2 del esqueleto |
| Carga + tablas base con 1 semana (Linux) | Carga 3.1 s + base 0.8 s = 3.9 s; pico RSS 211 MB (237 MB con la app). `jugadas` 1,100 filas / 0.3 MB; `sep_cuadros` 180,438 / 6.7 MB; `presion` 1,100; `objetivo` 965 (texto 96.1 %, balón 0.2 %, ninguno 3.7 %). Presión: 28.6 % por distancia, 0.2 % por sack | 1,100 jugadas | tarea 3 del esqueleto (`scratch/prueba_base.py`) |

## Revisión cruzada

## Cambios al contrato

| Fecha | Cambio | Pidió | Aprobó |
|---|---|---|---|
| 2026-11-20 | `api/vuelo/resumen` = ventaja al lanzar (`n_aproximado`, `por_separacion`, `por_tendencia`, `insight`); sin trayectorias; `sigue_libre` = abierto al lanzar | Equipo | Pendiente de B |
