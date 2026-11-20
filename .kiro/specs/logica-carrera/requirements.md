# Requisitos · Lógica del backend de la carrera (Persona A)

## Introducción

Este spec cubre solo el backend de la persona A: los relojes de la carrera, cuánto vale ganarla, la cadena y el eslabón débil por equipo, los KPIs del resumen y las jugadas ejemplo del replay. Produce los endpoints `api/resumen`, `api/carrera/*`, `api/equipos`, `api/jugadas-ejemplo` y `api/jugada`, y la función `relojes.resultado_por_jugada()` para B. Parte del esqueleto etiquetado. El dashboard de A está en el spec `dashboard-carrera`.

Referencias: steering `pregunta.md`, `contrato-api.md`, `stack-y-arquitectura.md`, `equipo.md`; skills `logica-carrera`, `calculo-carrera`, `backend-api-datos`, `estadistica-intervalos`.

## Requisitos

### Requisito 1: Relojes y resultado por jugada

**Historia de usuario:** Como analista, quiero saber en cada jugada quién llegó primero, para medir la carrera.

#### Criterios de aceptación

1. El sistema DEBE calcular por jugada `t_libre` (primer cuadro con un receptor libre antes de `t_fin`), `primer_libre_id`, `t_presion`, resultado y margen, según la skill `logica-carrera`.
2. CUANDO el receptor queda libre y la presión llega en el mismo cuadro, ENTONCES el resultado DEBE ser `gana_defensa`.
3. El sistema DEBE marcar `sack_con_libre` cuando la jugada terminó en sack con un receptor libre antes.
4. El sistema DEBE pasar los 5 casos sintéticos de la skill.
5. El sistema DEBE exponer `relojes.resultado_por_jugada()` y avisar en `ESTADO.md` cuando deje de ser de mentira.

### Requisito 2: Curvas de la carrera

#### Criterios de aceptación

1. CUANDO se pide `api/carrera/curvas`, ENTONCES el sistema DEBE devolver 41 puntos (0 a 4 s cada 0.1) con `pct_libre` y `pct_presion` acumulados, las dos medianas y la ventaja.
2. Las dos curvas DEBEN ser no decrecientes.

### Requisito 3: Resultado de la carrera

#### Criterios de aceptación

1. CUANDO se pide `api/carrera/resultado`, ENTONCES el sistema DEBE devolver el reparto de los tres resultados, que DEBE sumar 100 ± 0.1, y `pct_sack_con_libre`.

### Requisito 4: Conversión por distancia e H1

#### Criterios de aceptación

1. CUANDO se pide `api/carrera/distancia`, ENTONCES el sistema DEBE devolver por grupo la conversión de `gana_receptor` y de `gana_defensa` con intervalo de 90%; los grupos dependen del filtro (3.º/4.º o 1.º/2.º).
2. SI un grupo tiene menos de 20 jugadas, ENTONCES sus valores DEBEN ser `null`.
3. El sistema DEBE reportar H1 (diferencia con bootstrap de la diferencia) y su robustez en `scratch/resultados-carrera.md`.

### Requisito 5: Cadena y eslabón débil por equipo

**Historia de usuario:** Como entrenador o scout, quiero saber en qué paso se rompe la jugada decisiva de un equipo, para corregir primero ese paso.

#### Criterios de aceptación

1. CUANDO se pide `api/equipos`, ENTONCES el sistema DEBE devolver por equipo y vista: n, mediana de `t_presion`, tasas condicionales P2, P1 y P3, conversión, cadena acumulada de 5 pasos, eslabón y cuadrante, más las medianas de la liga.
2. MIENTRAS `vuelo.sigue_libre_por_jugada()` sea de mentira, P3 DEBE ser la mediana de la liga y el resto DEBE funcionar.
3. SI un equipo tiene menos de 30 jugadas, ENTONCES DEBE devolverse con eslabón "—" y cuadrante "Muestra pequeña".

### Requisito 6: Resumen e insight

#### Criterios de aceptación

1. CUANDO se pide `api/resumen`, ENTONCES el sistema DEBE devolver los KPIs del contrato para el filtro, la vista y el equipo, la cadena de la liga y un insight con números reales según la plantilla de la vista.
2. SI el equipo no existe, ENTONCES el sistema DEBE responder 404 con un mensaje claro.

### Requisito 7: Jugadas ejemplo y cuadros del replay

#### Criterios de aceptación

1. El sistema DEBE elegir de 2 a 4 jugadas con los criterios de la skill (al menos una por ganador), y el objetivo DEBE ser el primer receptor libre.
2. El sistema DEBE releer solo las semanas de esas jugadas para obtener los 22 jugadores, sin escribir a disco.
3. CUANDO se pide `api/jugada`, ENTONCES el sistema DEBE devolver los cuadros de 0.5 s antes del snap a 0.5 s después de la llegada, con roles, giro (de `giros.giro_por_cuadro`), separación contra el jugador con rol `defensor`, balón real con altura y relojes.
4. La separación de cada cuadro DEBE coincidir con la distancia entre los jugadores `receptor` y `defensor` de ese cuadro.

### Requisito 8: Endpoints

#### Criterios de aceptación

1. Los endpoints DEBEN responder exactamente con los campos de `contrato-api.md` (modelos de `esquemas/carrera.py`).
2. Valores `NaN` DEBEN llegar como `null` y los tipos de numpy como tipos de Python.
3. Parámetros inválidos DEBEN responder 422; mientras carga, 503.
4. Cada endpoint DEBE responder en menos de 300 ms con las 8 semanas.

### Requisito 9: Verificación

#### Criterios de aceptación

1. `scratch/verifica_carrera.py` DEBE probar los casos sintéticos, la forma de cada endpoint y sus números contra `scratch/resultados-carrera.md`.
2. Las verificaciones de la skill `calculo-carrera` que tocan a A (presión contra PFF, H1 y robustez) DEBEN quedar registradas.
