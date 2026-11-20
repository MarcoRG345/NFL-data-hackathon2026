---
inclusion: always
---

# La pregunta del proyecto: la carrera de los dos relojes

> **Nota sobre los datos:** `pass_arrived` no existe en estos datos. Donde una skill o spec diga `pass_arrived`, usa el último cuadro disponible para recortar, y el cuadro de `pass_forward` para medir. El tracking termina ~0.5 s después de `pass_forward`.

Este archivo manda sobre cualquier otra pregunta que aparezca en otros steering, specs viejos o archivos de `scratch/`. Las preguntas de la práctica (asistencia invisible, huella del mariscal, disfraz, separación sola) ya no se usan.

## Pregunta central

**En los momentos decisivos (3.º y 4.º down), ¿qué llega primero: el receptor libre o la defensa sobre el mariscal? ¿Y qué hace que el receptor gane esa carrera y llegue abierto al lanzamiento?**

La jugada se cuenta en tres tiempos. Cada pregunta base responde uno:

| # | Pregunta base | Qué aporta | Dueña |
|---|---|---|---|
| P1 | La carrera de dos relojes: cuando llega la presión, ¿ya hay un receptor libre? ¿Cuánto vale ganar la carrera? | Quién gana y cuánto vale | A |
| P2 | El giro que lo libera: ¿los receptores se liberan con un giro brusco o con velocidad? | Cómo se gana | B |
| P3 | Ventaja al lanzar: ¿el objetivo está abierto cuando sale el balón, y cómo llegó (abriéndose o cerrándose)? | Si ganar alcanza | B |
| S | Síntesis, el eslabón débil: ¿en qué paso se rompe la jugada de cada equipo? | La respuesta completa | A |

Hipótesis (se reportan aunque no se cumplan):
- **H1.** En 3.er down, cuando el receptor gana la carrera, la conversión es al menos 10 puntos mayor que cuando la gana la defensa.
- **H2.** A igual profundidad de ruta, un giro brusco genera más separación que una ruta recta.
- **H3 (ventaja al lanzar).** Cuando el objetivo está abierto (separación ≥ `ABIERTO_YD`) en `pass_forward`, el % de completos es mayor que cuando está cerrado, y es mayor aún si venía abriéndose en los 0.5 s previos.

## Lo que el dataset NO trae (no lo inventes)

- No hay receptor objetivo del pase como columna, ni qué defensor cubre a qué receptor, ni tacleos. Solo jugadas de pase.
- No hay cuadros del balón en el aire: no se puede medir separación en la llegada ni pérdida en el aire.
- Por eso se usan aproximaciones (abajo) y se declaran en "Cómo leer esto".

## Definiciones

Todo con datos normalizados (ataque hacia la derecha, `backend/normalizacion.py`).

| Concepto | Definición |
|---|---|
| Jugada válida | Tiene `ball_snap` y NO dice "No Play" en `playDescription` |
| Momento decisivo | `down` 3 o 4 |
| Filtros extra | `pocas_yardas`: 3.º/4.º con `yardsToGo` ≤ 3. `reloj_final`: ≤ 120 s en el 2.º o 4.º cuarto. `marcador_cerrado`: 4.º cuarto con diferencia ≤ 8. `normal`: 1.º y 2.º down |
| Receptor | `pff_role = "Pass Route"` |
| Su defensor | El `pff_role = "Coverage"` más cercano en ese cuadro (se recalcula en cada cuadro) |
| Separación | Distancia en yardas receptor ↔ defensor más cercano |
| Receptor libre | Separación ≥ `ABIERTO_YD`, contando solo desde 1.0 s después del snap (evita el colchón inicial del cornerback) |
| Reloj del receptor (`t_libre`) | Primer cuadro, desde 1.0 s, en que algún receptor está libre |
| Reloj de la defensa (`t_presion`) | Primer cuadro tras el snap y antes del lanzamiento en que un `Pass Rush` está a ≤ `RADIO_PRESION` del QB. Si hubo sack sin esa llegada, el cuadro del sack. Se deja de buscar si el QB cruzó la línea corriendo |
| Resultado de la carrera | `gana_receptor` si `t_libre` < `t_presion`; `gana_defensa` si llega la presión sin receptor libre; `sin_presion` si la presión nunca llega |
| Receptor objetivo | Solo pases con `passResult` C o I. El apellido que sigue a " to " en `playDescription`, comparado con `displayName` de los jugadores `Pass Route` del equipo atacante. Respaldo si no hay coincidencia única: receptor más cercano al balón en el último cuadro, con `aproximado = true`; si queda a > `RADIO_OBJETIVO` del balón: sin objetivo claro |
| Giro | Cambio de `dir` en 0.5 s, con velocidad ≥ 2 yd/s antes y después. Principal = el mayor entre snap y lanzamiento. Tipos: sin giro < 30°, suave 30–60°, brusco ≥ 60° |
| Separación ganada | Separación 1 s después del giro − separación en el giro |
| Velocidad conservada | `s` 0.3 s después del giro / `s` justo antes |
| Separación al lanzar | Separación del receptor objetivo en el cuadro de `pass_forward`. Abierto si ≥ `ABIERTO_YD`; cerrado si < `SEP_CERRADA_YD`; disputado entre ambos |
| Tendencia al lanzar | Separación en `pass_forward` − separación 0.5 s antes. Abriéndose > `TENDENCIA_UMBRAL_YD`; cerrándose < −`TENDENCIA_UMBRAL_YD`; estable en medio |
| Conversión | `playResult` ≥ `yardsToGo` |
| Cadena (por equipo, la calcula A) | Jugadas del filtro → **P2** algún receptor se liberó antes de `t_fin` → **P1** lo hizo antes de la presión (o no hubo presión) → **P3** hubo pase con objetivo válido y estaba abierto en `pass_forward` (las jugadas sin pase válido no pasan) → convirtió. Tasas condicionales: cada paso sobre los que pasaron el anterior |
| Eslabón débil | El paso P2, P1 o P3 donde el equipo queda más abajo de la mediana de la liga |
| Vista | `ofe`: el equipo con el balón. `def`: el equipo que defiende |

## Constantes (`backend/config.py`)

| Constante | Valor | Robustez |
|---|---|---|
| `RADIO_PRESION` | 2.0 yd | 1.5 y 3.0 |
| `ABIERTO_YD` | 3.0 yd | 2.0 y 4.0 |
| `INICIO_LIBRE_SEG` | 1.0 s | — |
| `GIRO_VENTANA_SEG` | 0.5 s | 0.3 y 0.7 |
| `GIRO_SUAVE`, `GIRO_BRUSCO` | 30°, 60° | brusco 45° y 90° |
| `VEL_MIN_GIRO` | 2.0 yd/s | — |
| `RADIO_OBJETIVO` | 3.0 yd (solo respaldo) | — |
| `SEP_CERRADA_YD` | 1.5 yd | — |
| `TENDENCIA_UMBRAL_YD` | 0.5 yd | — |
| `MIN_N_EQUIPO` | 30 jugadas | — |
| `BOOTSTRAP_REPS` | 1000, semilla 42, IC 90% | — |
| `FRANJAS` | corta 0–5, media 5–15, larga 15+ yd | — |

## Cómo se puede afirmar algo

- Toda cifra con su n. Comparaciones con intervalo de 90%.
- Con 32 equipos, ~3 salen "distintos" por azar: dilo.
- Si algo sale sorprendente (diferencias enormes, 90% de algo), primero sospecha de la definición.
- Robustez de P1: repetir con los otros radios y solo con `pff_passCoverageType = "Man"`.
