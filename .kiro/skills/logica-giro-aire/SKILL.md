---
name: logica-giro-aire
description: Algoritmos paso a paso de la persona B en el backend (giro por cuadro, giro principal por ruta, separación ganada, velocidad conservada, matriz ángulo × velocidad, pérdida de separación en el aire por franja y por profundidad, mapas de calor y selección de jugadas para la cinta). Úsala para backend/calculos/giros.py, vuelo.py, mapas.py, ticker.py y routers/giro_aire.py.
---

# Lógica del giro y del aire (Persona B)

Antes: `pregunta.md`, `calculo-carrera`, `backend-api-datos`, `estadistica-intervalos` y `mapas-de-calor`.

## Entradas (de la base)

| Tabla | Columnas que usas |
|---|---|
| `cuadros` (recortado) | gameId, playId, nflId, frameId, t, x, y, s, dir (normalizados), rol PFF |
| `sep_cuadros` | gameId, playId, nflId, t, separacion, libre |
| `jugadas` | banderas de filtro, linea_golpeo, t_fin, cuadro de lanzamiento y de llegada, passResult, conversion, down, yardsToGo, equipo_ataque |
| `presion` | t_presion |
| `objetivo` | objetivo_id, valido |

## 1. Giro por cuadro (`giros.giro_por_cuadro(cuadros)`)

Función pura: recibe cualquier tabla de cuadros (gameId, playId, nflId, frameId, s, dir) y devuelve la misma con dos columnas nuevas. A la usa con los 22 jugadores de sus jugadas ejemplo; tú con los receptores.

1. Ordena por jugador y cuadro. `dir_antes` y `s_antes` = valores 5 cuadros atrás (0.5 s), dentro del mismo jugador y jugada.
2. `delta` = ((dir − dir_antes + 180) módulo 360) − 180. Positivo = giro a la derecha (en el sentido del reloj).
3. Válido si `s` ≥ `VEL_MIN_GIRO` y `s_antes` ≥ `VEL_MIN_GIRO`.
4. `giro_grados` = `delta` si es válido, si no 0. `girando` = válido y |delta| ≥ `GIRO_SUAVE`.

**Casos sintéticos:** dir 350 → 10 a 5 yd/s: delta +20, no girando. dir 90 → 160 a 6 yd/s: +70, girando, brusco. dir 90 → 20 a 1 yd/s: no válido (lento).

## 2. Giro principal por ruta (`giros.construir`)

1. Receptores (`Pass Route`) con cuadros válidos entre t = 0.5 y `t_fin`.
2. Giro principal = el cuadro con mayor |delta|. El giro ocurre en la ventana: el cuadro de referencia es el del centro (3 cuadros antes).
3. `tipo`: sin_giro (< 30°), suave (30–60°), brusco (≥ 60°). Las rutas sin cuadros válidos se excluyen y se cuentan.
4. `franja` de la ruta = profundidad del receptor en `t_fin` (x − línea de golpeo): corta < 5, media 5–15, larga ≥ 15.
5. `sep_ganada` = separación 10 cuadros después del centro − separación en el centro (de `sep_cuadros`). Si falta alguno, la ruta no entra en esa métrica.
6. `vel_conservada` = s 3 cuadros después del centro / s al inicio de la ventana, recortada entre 0 y 1.5.
7. `gana_ruta` = el receptor estuvo libre (≥ 3 yd, t ≥ 1.0) antes de `t_presion` (o antes de `t_fin` si no hubo presión). Se calcula con la base, sin depender de A.
8. Posición del giro para el mapa: x relativa a la línea y y en el cuadro del centro.

## 3. Resumen de giros (`giros.resumen(filtro)`)

- `por_tipo`: por franja × tipo, media de `sep_ganada` con bootstrap por ruta; n < 20 → `None`.
- `matriz`: `angulo_bin` con cortes en 15, 30, 45, 60, 90; `vel_bin` 0 = ≥ 0.9, 1 = 0.8–0.9, 2 = 0.65–0.8, 3 = 0.5–0.65, 4 = < 0.5; valor = % de `gana_ruta`; n < 20 → `None`.
- H2 = `sep_ganada` de brusco − sin giro en la franja media, con bootstrap de la diferencia y robustez.
- `insight`: "Un giro brusco gana {x} yd de separación en rutas medias, contra {y} yd de una ruta sin giro."

## 4. El balón en el aire (`vuelo.construir`)

1. Jugadas con cuadro de lanzamiento, cuadro de llegada (o `pass_outcome_*` de respaldo) y objetivo válido.
2. `sep_lanzar` y `sep_llegar` = separación del objetivo en esos cuadros (de `sep_cuadros`).
3. `tiempo_vuelo` = (llegada − lanzamiento) / 10. `perdida` = `sep_lanzar` − `sep_llegar`.
4. `profundidad` = x del objetivo en la llegada − línea de golpeo. `franja`: corta < 5, media 5–15, larga ≥ 15. `bin5`: 0–5, 6–10, 11–15, 16–20, 21+ (las negativas cuentan en 0–5).
5. `sigue_libre` = `sep_llegar` ≥ `ABIERTO_YD`. `completo` = `passResult` es "C".
6. `sigue_libre_por_jugada()`: gameId, playId, valido, sigue_libre (para la cadena de A).

## 5. Resumen de vuelo (`vuelo.resumen(filtro)`)

- `por_franja`: n, media de `sep_lanzar` y `sep_llegar`, % sigue libre, % completo, mediana de `tiempo_vuelo`.
- `trayectorias` (para la animación): por `bin5`, n, mediana de `tiempo_vuelo` y media de `perdida`.
- H3 = `perdida` en larga − corta, con bootstrap; y % completo con ventaja conservada contra perdida.
- `insight`: "A partir de 15 yardas la ventaja se evapora: se pierden {x} yd en el vuelo y el % de completos cae a {y}%."

## 6. Mapas (`mapas.construir` y `mapas.celdas(capa, modo, equipo)`)

Según `mapas-de-calor`. Capa `giro`: rutas con `girando` en su giro principal, en la posición del giro, valor = `sep_ganada`. Capa `vuelo`: pases válidos en la posición de llegada, valor = `perdida`. Modo `decisivo` (3.º y 4.º) o `normal` (1.º y 2.º). Liga precalculada; por equipo (ataque) bajo demanda con caché.

## 7. Cinta (`ticker.construir`)

Usa `relojes.resultado_por_jugada()` de A (con datos de mentira hasta que sea real) más tus tablas. Candidatas solo decisivas y sin castigo:

| Tipo | Criterio | Texto |
|---|---|---|
| receptor | gana_receptor, convierte, mayor margen | "KC 3.º y 4 · Receptor libre a 2.0 s · Presión 2.7 s · CONVIERTE" |
| defensa | gana_defensa, sack, menor t_presion | "BUF 3.º y 8 · Presión 1.9 s · Sack · gana la defensa" |
| sin_presion | sin_presion, convierte | "DET 3.º y 2 · Sin presión · CONVIERTE" |
| giro | giro brusco del objetivo, mayor sep_ganada, convierte | "PHI 4.º y 1 · Giro brusco de 72° · +2.1 yd · CONVIERTE" |
| aire | mayor pérdida, incompleto | "SF 3.º y 6 · Libre al lanzar, cubierto al llegar (−2.3 yd) · INCOMPLETO" |

Dos por tipo, sin repetir jugada, alternando tipos. Equipo = el que ataca.

## Rendimiento

Giro por cuadro vectorizado sobre todos los receptores a la vez (`groupby(...).shift(5)`). Resúmenes precalculados para los 5 filtros; mapas de liga para 2 capas × 2 modos.
