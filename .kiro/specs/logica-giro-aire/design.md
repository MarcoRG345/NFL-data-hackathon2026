# Diseño · Lógica del backend del giro y el aire (Persona B)

## Flujo

```
base.cuadros (receptores) ──► giros.giro_por_cuadro ──► GIRO_CUADROS ──► giro principal ──► RUTAS
base.sep_cuadros, base.presion, base.jugadas ───────────────────────────────┘        │
                                                                                      ├─► resumen de giros (por filtro)
base.objetivo, base.sep_cuadros, base.jugadas ──► vuelo.construir ──► PASES ─────────┼─► resumen de vuelo (por filtro)
                                                          └─► sigue_libre_por_jugada() ──► (A: cadena)
RUTAS + PASES ──► mapas.construir ──► celdas (capa × modo)
relojes.resultado_por_jugada() (A) + RUTAS + PASES ──► ticker.construir
giros.giro_por_cuadro(cuadros de A) ──► (A: api/jugada)
```

Orden en el hilo de carga: `giros` → `vuelo` → `mapas` → (A) → `ticker`. Cada uno en su try/except.

## Modelo de datos (en memoria)

### RUTAS (una fila por jugada × receptor con cuadros válidos)

| Columna | Tipo | Nota |
|---|---|---|
| gameId, playId, nflId | int | llave |
| t_giro | float | centro de la ventana |
| giro_grados | float | con signo |
| tipo | category | sin_giro, suave, brusco |
| franja | category | corta, media, larga |
| sep_ganada | float o NaN | yd |
| vel_conservada | float | 0–1.5 |
| angulo_bin, vel_bin | int | para la matriz |
| gana_ruta | bool | libre antes de la presión |
| x_rel, y | float | posición del giro |
| banderas de filtro, equipo_ataque | | de `jugadas` |

### PASES (una fila por jugada con pase y objetivo válido)

| Columna | Tipo |
|---|---|
| gameId, playId, objetivo_id | int |
| sep_lanzar, sep_llegar, perdida, tiempo_vuelo, profundidad | float |
| franja, bin5 | category |
| sigue_libre, completo | bool |
| x_rel_llegada, y_llegada | float |
| banderas de filtro, equipo_ataque | |

### Resultados precalculados

`estado.resultados["giro_aire"]` con llaves `("giros", filtro)`, `("vuelo", filtro)`, `("mapa", capa, modo, None)` y la lista `ticker`. Mapas por equipo en caché `("mapa", capa, modo, equipo)`.

## Interfaces

| Módulo | Función | Devuelve |
|---|---|---|
| `giros` | `giro_por_cuadro(cuadros)` | La tabla con `giro_grados` y `girando` (de mentira: 0 y `False`) |
| `giros` | `construir(estado)` | Nada; llena RUTAS y precalculados |
| `giros` | `resumen(filtro)` | Diccionario con la forma del contrato |
| `vuelo` | `construir(estado)` | Nada; llena PASES y precalculados |
| `vuelo` | `sigue_libre_por_jugada()` | DataFrame: gameId, playId, valido, sigue_libre (de mentira: vacío) |
| `vuelo` | `resumen(filtro)` | Diccionario con `por_franja`, `trayectorias`, `insight`, `n` |
| `mapas` | `construir(estado)`, `celdas(capa, modo, equipo)` | Diccionario con la forma del contrato |
| `ticker` | `construir(estado)`, `lista(filtro)` | Lista de `{texto, tipo}` |

Dependencia de A (contrato): `relojes.resultado_por_jugada()` (de mentira: todas `sin_presion`).

## Decisiones fijas

- `delta` positivo = giro a la derecha; la cancha de A lo usa para el lado del arco.
- Centro del giro = 3 cuadros antes del cuadro con el máximo |delta|.
- Franja de la ruta por la profundidad en `t_fin`; franja del pase por la profundidad en la llegada.
- `gana_ruta` se calcula con la base (no depende de A), para que la matriz funcione desde el inicio.
- Pases con profundidad negativa cuentan como corta / 0–5.

## Routers (`routers/giro_aire.py`)

Igual que A: `requiere_datos` → validar → leer precalculado o caché → `a_json` → modelo. Sin pandas en el router.

## Manejo de errores

| Situación | Respuesta |
|---|---|
| Cargando | 503 |
| Capa, modo o filtro inválidos | 422 |
| Equipo inexistente | 404 |
| Módulo que falló | 200 con datos de mentira, `n = 0`, error en `api/estado-datos` |

## Pruebas

| Prueba | Espera |
|---|---|
| 3 casos sintéticos de giro (envolvimiento, brusco, lento) | Los de la skill |
| % de rutas con giro brusco | Menor a 70% o aviso |
| `pass_arrived` disponible | ≥ 80% de los pases o aviso |
| Objetivo contra `playDescription` (20 al azar) | ≥ 90% |
| Celdas del mapa con n ≥ 5 y `valor_norm` en [0, 1] | Verdadero |
| Cinta: 8 a 10 elementos sin repetir jugada | Verdadero |
| Números contra `resultados-giro-aire.md` | ± 0.5 |
| Tiempo por endpoint | < 300 ms |
