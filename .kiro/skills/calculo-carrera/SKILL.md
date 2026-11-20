---
name: calculo-carrera
description: Cómo calcular con el tracking del Big Data Bowl 2023 los relojes de la carrera (presión y receptor libre), la separación por cuadro, el receptor objetivo, los giros, la pérdida de separación en el aire, la cadena por equipo y sus intervalos, y cómo verificar cada cálculo. Úsala para cualquier archivo de backend/base o backend/calculos.
---

# Cálculo de la carrera

Definiciones y constantes: steering `pregunta.md`. Esta skill dice cómo calcular sin equivocarse. Úsala junto con `exploracion-datos-grandes`.

## Principios

- **Vectoriza.** Nada de ciclos por fila. Para "el defensor más cercano" cruza, por jugada y cuadro, receptores × defensores (merge por `gameId, playId, frameId`) y quédate con la distancia mínima.
- **Recorta al leer.** De cada semana guarda solo: QB, `Pass Route`, `Coverage`, `Pass Rush` y balón, de `ball_snap` a `pass_arrived` + 5 cuadros (o al final si no hay pase). Para las jugadas ejemplo guarda los 22 jugadores completos.
- **Calcula una vez.** Todo se construye al terminar la carga y se guarda en memoria. Los endpoints solo filtran.
- **Reutiliza.** `normalizacion.py` y la llegada de presión de la práctica (asistencia invisible) ya existen: impórtalos.

## Tablas base (`backend/base/`)

| Tabla | Una fila por | Columnas clave |
|---|---|---|
| `jugadas` | jugada válida | ids, equipo ataque y defensa, down, yardsToGo, cuarto, reloj_seg, dif_marcador (desde el ataque), banderas de cada filtro, cobertura, `passResult`, conversión, cuadros de snap / lanzamiento / llegada / sack, línea de golpeo |
| `sep_cuadros` | jugada × receptor × cuadro | t (s desde el snap), separación, nflId del defensor más cercano, libre (≥ `ABIERTO_YD` y t ≥ 1.0) |
| `presion` | jugada | t_presion (o vacío), nflId del rusher que llegó, fuente ("distancia" o "sack") |
| `objetivo` | jugada con pase | nflId del objetivo, distancia al balón, válido (≤ `RADIO_OBJETIVO`) |

## Trampas conocidas

- **Balón**: `team = "football"`, `nflId` vacío. Nunca es jugador.
- **Ángulos**: tras la normalización, `dir` y `o` ya van girados 180°. Para un vector de movimiento: componente x = seno(dir), componente y = coseno(dir) (grados a radianes). Las diferencias de ángulo se envuelven a [−180, 180] antes de comparar.
- **Colchón del cornerback**: un receptor puede estar a 6 yd en el snap. Por eso "libre" solo cuenta desde 1.0 s.
- **Reloj**: `gameClock` es texto "MM:SS"; conviértelo a segundos.
- **Marcador**: diferencia desde el punto de vista del equipo con el balón (usa `homeTeamAbbr`).
- **QB que corre**: si cruza la línea de golpeo, deja de buscar presión.
- **`pass_arrived` puede faltar**: mide el porcentaje y usa `pass_outcome_*` de respaldo.
- **Vista defensiva**: los agregados por equipo agrupan por `defensiveTeam` en lugar de `possessionTeam`.
- **Giro con ruido**: a baja velocidad `dir` salta. Exige velocidad ≥ `VEL_MIN_GIRO` antes y después.

## Cálculos por módulo

Esta skill cubre la base. Los algoritmos de cada persona están en:
- `logica-carrera` (A): `relojes.py`, `sintesis.py`, `ejemplos.py`.
- `logica-giro-aire` (B): `giros.py`, `vuelo.py`, `mapas.py`, `ticker.py`.

Y las reglas comunes en `backend-api-datos` (estructura y API) y `estadistica-intervalos` (intervalos y robustez).

## Verificaciones obligatorias (ejecutar y mostrar)

1. Conteos: jugadas válidas, decisivas, con pase, con presión, con objetivo válido.
2. % de jugadas con `pass_arrived`; si es menor a 80%, avisar.
3. Separación: mediana y percentiles 10/90 en el lanzamiento; nada negativo ni mayor a 40.
4. Presión: % de coincidencia con `pff_hurry`/`pff_hit`/`pff_sack` (la práctica dio 78%).
5. Objetivo: coincidencia con el nombre en `playDescription` en 20 jugadas al azar (meta ≥ 90%).
6. Giros: % de rutas con giro brusco (si es más de 70%, hay ruido).
7. Flecha de prueba: un receptor que corre hacia la zona de anotación rival debe dar componente x positiva.
8. H1 con intervalo; robustez con los otros radios y solo cobertura de hombre a hombre.

Resultados en `scratch/resultados-*.md`. Siempre di qué archivos escribiste.
