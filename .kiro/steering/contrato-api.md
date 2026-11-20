---
inclusion: always
---

# Contrato de la API

Es la única fuente de verdad entre backend y dashboard. `backend/esquemas/*.py` y `dashboard/src/types.ts` la copian campo por campo. Ningún campo extra ni con otro nombre. Si hace falta cambiar algo: se cambia aquí primero, en un PR que la otra persona aprueba.

## Reglas comunes

- Todas las rutas bajo `api/`. Mientras los datos cargan: **503** con `{"detalle": "cargando"}`.
- Parámetros: `filtro` = `decisivo` (defecto) | `pocas_yardas` | `reloj_final` | `marcador_cerrado` | `normal`. `vista` = `ofe` (defecto) | `def`. `equipo` = abreviatura (`KC`), opcional. `modo` = `decisivo` (defecto) | `normal`.
- Porcentajes de 0 a 100 con 1 decimal. Tiempos en segundos con 2 decimales. Yardas con 1 decimal.
- Todo intervalo es `[bajo, alto]` al 90%.

## Endpoints de la persona A (carrera, síntesis, cancha)

| Endpoint | Respuesta |
|---|---|
| `GET api/estado-datos` (esqueleto) | `listo` (bool), `cargando` (bool), `error` (str o null), `semanas` (int), `n_jugadas` (int) |
| `GET api/resumen?filtro&vista&equipo` | `filtro`, `vista`, `n`; `kpis`: `pct_gana_receptor`, `pct_gana_defensa`, `conv_gana_receptor`, `conv_gana_defensa`, `reloj_defensa_mediana`, `conv_equipo`, `eslabon_equipo`; `cadena_liga`: lista de `{paso, pct}` (5 pasos); `insight` (str) |
| `GET api/carrera/curvas?filtro` | `filtro`, `n`; `puntos`: lista de `{t, pct_libre, pct_presion}` cada 0.1 s de 0 a 4; `mediana_libre`, `mediana_presion`, `ventaja` |
| `GET api/carrera/distancia?filtro` | `filtro`, `grupos`: lista de `{grupo ("3.º y 1–3", "3.º y 4–6", "3.º y 7+", "4.º down"), n, conv_gana, conv_pierde, ic_gana, ic_pierde}` |
| `GET api/carrera/resultado?filtro` | `filtro`, `n`, `pct_gana_receptor`, `pct_gana_defensa`, `pct_sin_presion`, `pct_sack_con_libre` |
| `GET api/equipos?filtro&vista` | `filtro`, `vista`; `medianas`: `{t_presion, p1, p2, p3, conv}`; `equipos`: lista de `{equipo, n, t_presion_mediana, p2_se_libera, p1_gana_carrera, p3_sigue_libre, conv, cadena (5 números), eslabon ("P1"|"P2"|"P3"), cuadrante}` |
| `GET api/jugadas-ejemplo` | lista de `{id, gameId, playId, titulo, ganador ("receptor"|"defensa"), situacion}` (al menos 2) |
| `GET api/jugada?gameId&playId` | `contexto`: `{down, yardsToGo, cuarto, reloj, marcador_texto, descripcion, resultado}`; `linea_golpeo`, `linea_primer_down` (x en yd); `relojes`: `{t_presion, t_libre, ganador, margen}`; `balon`: `{t_lanza, t_llega, x_lanza, y_lanza, x_llega, y_llega}`; `eventos`: lista de `{t, nombre}`; `cuadros`: lista de `{t, separacion, receptor_libre, presion_llego, balon: {x, y, altura}, jugadores: [{nflId, x, y, s, dir, giro_grados, girando, lado ("ataque"|"defensa"), jersey, posicion, rol ("qb"|"receptor"|"defensor"|"rusher"|"otro")}]}` |

`cuadrante` = "Todo funciona" | "Se liberan, pero no hay tiempo" | "La línea aguanta, nadie se libera" | "Nada funciona" | "Muestra pequeña" (n < 30, con `eslabon` = "—"). `p2_se_libera`, `p1_gana_carrera` y `p3_sigue_libre` (abierto al lanzar) son tasas condicionales de la cadena (ver `pregunta.md`). `altura` del balón de 0 a 1 (0 en el suelo, 1 a mitad del vuelo; el tracking termina ~0.5 s después del lanzamiento, así que `t_llega`, `x_llega` y `y_llega` de `balon` son los del último cuadro disponible). `x`, `y` en yardas normalizadas; el frontend recorta la ventana.

## Endpoints de la persona B (giro, aire, mapas, ticker)

| Endpoint | Respuesta |
|---|---|
| `GET api/ticker?filtro` | lista de 8 a 10 `{texto, tipo ("receptor"|"defensa"|"sin_presion"|"giro"|"aire")}` |
| `GET api/giros/resumen?filtro` | `filtro`, `n`; `por_tipo`: lista de `{franja ("corta"|"media"|"larga"), tipo ("sin_giro"|"suave"|"brusco"), n, sep_ganada, ic}`; `matriz`: lista de `{angulo_bin (0–5), vel_bin (0–4, 0 = conserva más), n, pct_gana_carrera}`; `insight` |
| `GET api/vuelo/resumen?filtro` | `filtro`, `n`, `n_aproximado` (objetivos por respaldo); `por_separacion`: lista de 3 `{franja ("cerrado"|"disputado"|"abierto"), n, pct_completo, ic}`; `por_tendencia`: lista de 3 `{tendencia ("cerrandose"|"estable"|"abriendose"), n, pct_completo, ic}`; `insight` |
| `GET api/mapa?capa&modo&equipo` | `capa` ("giro"|"vuelo"), `modo`, `n`, `tam_celda` (2.5), `x_min` (−15), `x_max` (45); `celdas`: lista de `{col, fila, x0, x1, y0, y1, n, valor, valor_norm}` (solo celdas con n ≥ 5); `escala`: `{min, max, unidad}` |

`vuelo` ahora significa "ventaja al lanzar" (no hay cuadros del balón en el aire; ver nota en `pregunta.md`). `ic` = `[bajo, alto]` del % completo; es `null` si n < 20. En `api/mapa`, la capa `vuelo` pinta la separación del objetivo al lanzar según su posición relativa a la línea de golpeo.

`angulo_bin`: 0–15°, 15–30°, 30–45°, 45–60°, 60–90°, 90°+. `vel_bin`: 90%+, 80–90%, 65–80%, 50–65%, menos de 50%. `x` de las celdas relativa a la línea de golpeo.

## Conexiones internas (funciones, no endpoints)

Solo hay tres. Todo lo demás, cada persona lo calcula con las tablas base.

| Función | Dueña | La usa | Mientras no esté |
|---|---|---|---|
| `giros.giro_por_cuadro(cuadros)` → la misma tabla con `giro_grados` (positivo = a la derecha) y `girando` | B | A en `api/jugada` (flecha curva) | Devuelve 0 y `False`: la cancha funciona sin arco |
| `vuelo.sigue_libre_por_jugada()` → gameId, playId, valido, sigue_libre (`sigue_libre` = abierto en el lanzamiento) | B | A en la cadena (paso P3) | Tabla vacía: A usa la mediana de la liga para P3 |
| `relojes.resultado_por_jugada()` → gameId, playId, t_libre, t_presion, resultado, margen, sack_con_libre | A | B en `api/ticker` | Todas `sin_presion`: la cinta usa solo giro y aire |
| `base.situacion`, `base.separacion`, `base.presion`, `base.objetivo` | Esqueleto | Las dos | Existen desde el día 1 |
