---
name: logica-carrera
description: Algoritmos paso a paso de la persona A en el backend (relojes por jugada, curvas acumuladas, resultado de la carrera, conversión por distancia, cadena y eslabón débil por equipo, cuadrante, KPIs del resumen, insight, elección de jugadas ejemplo y cuadros del replay). Úsala para backend/calculos/relojes.py, sintesis.py, ejemplos.py y routers/carrera.py.
---

# Lógica de la carrera (Persona A)

Antes: `pregunta.md` (definiciones), `calculo-carrera` (tablas base y trampas), `backend-api-datos` (estructura) y `estadistica-intervalos` (intervalos).

## Entradas (de la base)

| Tabla | Columnas que usas |
|---|---|
| `jugadas` | gameId, playId, equipo_ataque, equipo_defensa, down, yardsToGo, banderas de filtro, conversion, passResult, t_fin (lanzamiento, sack o fin), t_lanza, t_llega, linea_golpeo, cobertura |
| `sep_cuadros` | gameId, playId, nflId (receptor), t, separacion, defensor_id, libre |
| `presion` | gameId, playId, t_presion, rusher_id, fuente |
| `objetivo` | gameId, playId, objetivo_id, valido |

## 1. Relojes por jugada (`relojes.construir`)

1. De `sep_cuadros`, solo filas con `libre` y `t` < `t_fin` de su jugada. Por jugada: `t_libre` = mínimo `t` y `primer_libre_id` = el receptor de ese mínimo.
2. Une con `presion` (left join): `t_presion` puede faltar.
3. Resultado: si hay `t_libre` y (no hay `t_presion` o `t_libre` < `t_presion`) → `gana_receptor`. Si no, si hay `t_presion` → `gana_defensa`. Si no → `sin_presion`. Empate exacto (mismo cuadro) → `gana_defensa`.
4. `margen` = `t_presion` − `t_libre` (solo si existen las dos).
5. `sack_con_libre` = `passResult` es "S" y hay `t_libre` < `t_fin`.
6. Se guarda en `estado.resultados["relojes"]`. `resultado_por_jugada()` devuelve esa tabla (para B).

**Casos sintéticos para probar:** libre 1.5 s y presión 2.0 s → gana_receptor, margen 0.5. Libre nunca y presión 2.1 → gana_defensa. Libre 2.3 y presión 2.3 → gana_defensa. Libre 1.8 y sin presión → gana_receptor. Sin libre y sin presión → sin_presion.

## 2. Curvas (`relojes.curvas(filtro)`)

- Universo: jugadas del filtro. Para t de 0 a 4 cada 0.1: `pct_libre` = % de jugadas con `t_libre` ≤ t; `pct_presion` = % con `t_presion` ≤ t (las que nunca tienen evento cuentan como "todavía no").
- `mediana_libre` y `mediana_presion`: medianas entre las jugadas donde el evento ocurre. `ventaja` = presión − libre.

## 3. Resultado (`relojes.resultado(filtro)`)

Reparto de los tres resultados (suma 100) y `pct_sack_con_libre` = % de las jugadas `gana_receptor` que terminaron en sack.

## 4. Distancia (`relojes.distancia(filtro)`)

- Grupos para filtros de 3.º/4.º: "3.º y 1–3", "3.º y 4–6", "3.º y 7+", "4.º down". Con `filtro = normal`: "2.º y 1–3", "2.º y 4–6", "2.º y 7+", "1.º down".
- Por grupo: conversión de las `gana_receptor` y de las `gana_defensa`, cada una con bootstrap; n por grupo. Menos de 20 → `None`.
- H1 = diferencia de conversión (todas las decisivas) con bootstrap de la diferencia, y su robustez (ver `estadistica-intervalos`).

## 5. Cadena por equipo (`sintesis.construir` y `sintesis.equipos(filtro, vista)`)

Equipo = `equipo_ataque` con vista `ofe`, `equipo_defensa` con vista `def`. Pasos por jugada:

| Paso | Pasa si |
|---|---|
| P2 · se libera | hay `t_libre` < `t_fin` |
| P1 · gana la carrera (de las que pasaron P2) | resultado `gana_receptor`, o `sin_presion` con P2 |
| P3 · sigue libre (de las que pasaron P1) | `vuelo.sigue_libre_por_jugada()` dice válido y libre (las que no tuvieron pase válido no pasan: "no se aprovechó") |
| Convierte (de las que pasaron P3) | `conversion` |

- Tasas condicionales: `p2_se_libera`, `p1_gana_carrera`, `p3_sigue_libre` (en %).
- `cadena` acumulada sobre el total: [100, %P2, %P1, %P3, %convierte tras P3].
- `conv` = conversión total del equipo en el filtro. `t_presion_mediana` = mediana entre jugadas con presión.
- Medianas de la liga de cada tasa. `eslabon` = el paso (P2, P1, P3) con la menor diferencia contra su mediana.
- `cuadrante`: x = `t_presion_mediana` contra la mediana de la liga (≥ = la línea aguanta); y = `p1_gana_carrera` contra la mediana (≥ = se liberan a tiempo).
- Equipos con n < 30: se devuelven con `eslabon = "—"` y `cuadrante = "Muestra pequeña"`.
- Mientras `vuelo.sigue_libre_por_jugada()` sea de mentira, P3 = mediana de la liga para todos (y se dice en `ESTADO.md`).

## 6. Resumen (`sintesis.resumen(filtro, vista, equipo)`)

- KPIs: reparto de resultados, conversión de `gana_receptor` y de `gana_defensa`, mediana de `t_presion`, `conv_equipo` y `eslabon_equipo` (si se pidió equipo).
- `cadena_liga`: la cadena de toda la liga con nombres de paso.
- `insight` con plantilla y números reales. Vista ofensiva: "Cuando el receptor gana la carrera {contexto}, la conversión sube de {conv_gana_defensa}% a {conv_gana_receptor}%." Vista defensiva: "Cuando la defensa gana la carrera {contexto}, la conversión rival cae a {conv_gana_defensa}%."

## 7. Jugadas ejemplo (`ejemplos.construir`)

1. Candidatas: decisivas, sin castigo, con objetivo válido y `primer_libre_id` = `objetivo_id`.
2. "Gana el receptor": conversión, margen ≥ 0.3 s, separación del objetivo al lanzar ≥ 4 yd; desempate por giro brusco del objetivo y mayor margen.
3. "Gana la defensa": `t_presion` ≤ 2.3 s y sack o incompleto.
4. Para esas 2 a 4 jugadas, `cargar_cuadros_completos(ids)` vuelve a leer **solo** las semanas que las contienen, filtrando por gameId y playId (leer es válido; escribir no).
5. Cuadros desde 0.5 s antes del snap hasta 0.5 s después de `t_llega` (o de `t_fin`). Por cuadro y jugador: x, y, s, dir (normalizados), `lado`, `jersey`, `posicion`, `rol`:
   - `qb`: el de `pff_role = "Pass"`; `receptor`: el objetivo; `rusher`: `presion.rusher_id`; `defensor`: el defensor más cercano al objetivo más frecuente entre 1.0 s y `t_llega`; el resto, `otro`.
6. Giro: `giros.giro_por_cuadro(cuadros)` de B (agrega `giro_grados` y `girando`).
7. `separacion` del cuadro = distancia objetivo ↔ jugador con rol `defensor` (así la línea dibujada y el número coinciden). `receptor_libre` = separación ≥ 3 y t ≥ 1.0. `presion_llego` = t ≥ `t_presion`.
8. Balón: posición real del balón del tracking; `altura` = seno(π·u) con u = (t − t_lanza) / (t_llega − t_lanza) durante el vuelo, 0 fuera.
9. `contexto.marcador_texto` desde el ataque: "pierden por 4", "ganan por 3" o "empate".

## Rendimiento

Todo lo anterior se precalcula para los 5 filtros × 2 vistas al construir. `api/jugada` sirve desde un diccionario por id. Meta: < 300 ms por endpoint.
