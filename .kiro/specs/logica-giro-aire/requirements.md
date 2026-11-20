# Requisitos · Lógica del backend del giro y el aire (Persona B)

## Introducción

Este spec cubre solo el backend de la persona B: los giros de los receptores, la ventaja del objetivo al lanzar (el tracking termina ~0.5 s después de `pass_forward`; no existe `pass_arrived`), los mapas de calor y la cinta de jugadas clave. Produce los endpoints `api/giros/resumen`, `api/vuelo/resumen`, `api/mapa` y `api/ticker`, y las funciones `giros.giro_por_cuadro(cuadros)` y `vuelo.sigue_libre_por_jugada()` para A. Parte del esqueleto etiquetado. El dashboard de B está en el spec `dashboard-giro-aire`.

Referencias: steering `pregunta.md`, `contrato-api.md`, `stack-y-arquitectura.md`, `equipo.md`; skills `logica-giro-aire`, `calculo-carrera`, `backend-api-datos`, `estadistica-intervalos`, `mapas-de-calor`.

## Requisitos

### Requisito 1: Giro por cuadro

**Historia de usuario:** Como analista, quiero detectar cuándo y cuánto gira cada jugador, para explicar cómo se libera el receptor y dibujarlo en la cancha.

#### Criterios de aceptación

1. `giros.giro_por_cuadro(cuadros)` DEBE ser una función pura que reciba cualquier tabla de cuadros y agregue `giro_grados` (positivo = a la derecha) y `girando`, según la skill `logica-giro-aire`.
2. Las diferencias de ángulo DEBEN envolverse a [−180, 180] y solo contar con velocidad ≥ `VEL_MIN_GIRO` antes y después.
3. El sistema DEBE pasar los 3 casos sintéticos de la skill.
4. CUANDO la función deje de ser de mentira, ENTONCES B DEBE avisar a A en `ESTADO.md`.

### Requisito 2: Giro principal por ruta

#### Criterios de aceptación

1. El sistema DEBE elegir por ruta el giro con mayor |delta| entre 0.5 s y `t_fin`, con tipo, franja, separación ganada, velocidad conservada, `gana_ruta` y posición.
2. SI más del 70% de las rutas sale con giro brusco, ENTONCES el sistema DEBE avisarlo como posible ruido en `scratch/resultados-giro-aire.md`.
3. El sistema DEBE reportar cuántas rutas se excluyen por falta de cuadros válidos.

### Requisito 3: Resumen de giros e H2

#### Criterios de aceptación

1. CUANDO se pide `api/giros/resumen`, ENTONCES el sistema DEBE devolver la separación ganada por franja y tipo con intervalo de 90%, la matriz de 6 × 5 con el % que gana la carrera y un insight con números reales.
2. Las celdas o grupos con menos de 20 rutas DEBEN ser `null`.
3. El sistema DEBE reportar H2 con bootstrap de la diferencia y su robustez.

### Requisito 4: Ventaja al lanzar e H3

#### Criterios de aceptación

1. El sistema DEBE determinar el receptor objetivo solo en pases con `passResult` C o I: apellido tras " to " en `playDescription` contra `displayName` de los receptores del equipo atacante; respaldo = receptor más cercano al balón en el último cuadro con `aproximado = true`. DEBE reportar cuántos objetivos son aproximados y cuántas jugadas quedan sin objetivo.
2. El sistema DEBE calcular por jugada con objetivo válido: separación en `pass_forward`, franja de separación (cerrado, disputado, abierto), tendencia en los 0.5 s previos (abriéndose, estable, cerrándose) y completo según `passResult`.
3. CUANDO se pide `api/vuelo/resumen`, ENTONCES el sistema DEBE devolver `por_separacion`, `por_tendencia`, `n_aproximado` y un insight con números reales, con intervalo de 90% en `pct_completo` (`null` si n < 20).
4. `vuelo.sigue_libre_por_jugada()` DEBE devolver gameId, playId, valido y sigue_libre, donde `sigue_libre` significa abierto en el lanzamiento; B DEBE avisar a A cuando sea real.
5. El sistema DEBE reportar H3 (diferencia de % completo entre abierto y cerrado, con bootstrap) y su robustez con `ABIERTO_YD` de 2.0 y 4.0, también sin los objetivos aproximados.

### Requisito 5: Mapas de calor

#### Criterios de aceptación

1. CUANDO se pide `api/mapa`, ENTONCES el sistema DEBE devolver las celdas de la capa, el modo y el equipo pedidos, con `valor_norm` de 0 a 1 y solo celdas con n ≥ 5.
2. Los mapas de la liga DEBEN precalcularse; los de equipo, bajo demanda con caché.

### Requisito 6: Cinta de jugadas clave

#### Criterios de aceptación

1. CUANDO se pide `api/ticker`, ENTONCES el sistema DEBE devolver de 8 a 10 jugadas reales, dos por tipo, sin repetir jugada y alternando tipos, con el texto de la skill.
2. MIENTRAS `relojes.resultado_por_jugada()` sea de mentira, la cinta DEBE usar solo los tipos giro y aire.

### Requisito 7: Endpoints

#### Criterios de aceptación

1. Los endpoints DEBEN responder exactamente con los campos de `contrato-api.md` (modelos de `esquemas/giro_aire.py`).
2. `NaN` DEBE llegar como `null`; tipos de numpy como tipos de Python.
3. Parámetros inválidos → 422; cargando → 503; equipo inexistente → 404.
4. Cada endpoint DEBE responder en menos de 300 ms con las 8 semanas.

### Requisito 8: Verificación

#### Criterios de aceptación

1. `scratch/verifica_giro_aire.py` DEBE probar los casos sintéticos, la forma de cada endpoint y sus números contra `scratch/resultados-giro-aire.md`.
2. Las verificaciones de la skill `calculo-carrera` que tocan a B (objetivo contra `playDescription` y balón en el último cuadro, ruido de giros; `pass_arrived` no existe) DEBEN quedar registradas.
