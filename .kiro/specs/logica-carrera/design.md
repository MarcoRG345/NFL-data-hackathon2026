# Diseño · Lógica del backend de la carrera (Persona A)

## Flujo

```
base.jugadas ─┐
base.sep_cuadros ─┼─► relojes.construir ──► tabla RELOJES ──► curvas / resultado / distancia (por filtro)
base.presion ─┘                                │                 └─► routers/carrera.py
                                               ├─► resultado_por_jugada() ──► (B: ticker)
                                               ▼
vuelo.sigue_libre_por_jugada() (B) ──► sintesis.construir ──► tabla CADENA ──► equipos / resumen (por filtro × vista)
base.objetivo ─────────────────────► ejemplos.construir ──► cargar_cuadros_completos ──► giros.giro_por_cuadro (B) ──► JUGADAS
```

Orden dentro del hilo de carga: B (giros, vuelo) → `relojes` → `sintesis` → `ejemplos`. Cada uno en su try/except (skill `backend-api-datos`).

## Modelo de datos (en memoria)

### Tabla RELOJES (una fila por jugada válida)

| Columna | Tipo | Nota |
|---|---|---|
| gameId, playId | int | llave |
| t_libre | float o NaN | s desde el snap |
| primer_libre_id | int o NaN | receptor |
| t_presion | float o NaN | de la base |
| resultado | category | gana_receptor, gana_defensa, sin_presion |
| margen | float o NaN | t_presion − t_libre |
| sack_con_libre | bool | |
| conversion | bool | de `jugadas` |
| banderas de filtro | bool | de `jugadas` |
| equipo_ataque, equipo_defensa | category | de `jugadas` |

### Tabla CADENA (una fila por jugada válida)

Columnas de RELOJES más: `pasa_p2`, `pasa_p1`, `pasa_p3`, `convierte_final` (bool).

### Resultados precalculados

`estado.resultados["carrera"]` = diccionario con llaves `("curvas", filtro)`, `("resultado", filtro)`, `("distancia", filtro)`, `("equipos", filtro, vista)`, `("resumen", filtro, vista)`; más `jugadas_ejemplo` (lista) y `jugadas` (diccionario id → respuesta completa de `api/jugada`). El resumen con equipo se calcula bajo demanda con caché.

## Interfaces

| Módulo | Función | Devuelve |
|---|---|---|
| `relojes` | `construir(estado)` | Nada; llena RELOJES y los precalculados de curvas, resultado y distancia |
| `relojes` | `resultado_por_jugada()` | DataFrame: gameId, playId, t_libre, t_presion, resultado, margen, sack_con_libre (de mentira: todas `sin_presion`) |
| `relojes` | `curvas(filtro)`, `resultado(filtro)`, `distancia(filtro)` | Diccionarios con la forma del contrato |
| `sintesis` | `construir(estado)` | Nada; llena CADENA y los precalculados de equipos y resumen |
| `sintesis` | `equipos(filtro, vista)`, `resumen(filtro, vista, equipo)` | Diccionarios con la forma del contrato |
| `ejemplos` | `construir(estado)` | Nada; elige jugadas y arma sus respuestas |
| `ejemplos` | `cargar_cuadros_completos(ids)` | DataFrame con los 22 jugadores y el balón de esas jugadas |
| `ejemplos` | `lista()`, `jugada(gameId, playId)` | Lista y respuesta completa |

Dependencias de B (contrato): `giros.giro_por_cuadro(cuadros)` (de mentira: 0 y `False`) y `vuelo.sigue_libre_por_jugada()` (de mentira: tabla vacía → P3 = mediana).

## Detalles de cálculo

Ver skill `logica-carrera` secciones 1 a 7. Decisiones fijas de este spec:
- Empate de relojes → `gana_defensa`.
- Las jugadas que pasan P1 sin pase válido (sack, scramble, pase tirado) no pasan P3.
- La cadena acumulada usa como denominador todas las jugadas del filtro del equipo.
- Medianas de `t_presion` solo entre jugadas con presión.

## Routers (`routers/carrera.py`)

Cada endpoint: dependencia `requiere_datos` → validar `equipo` → leer del precalculado o de la caché → convertir con `a_json` → modelo Pydantic. Sin pandas en el router.

## Manejo de errores

| Situación | Respuesta |
|---|---|
| Cargando | 503 `{"detalle": "cargando"}` |
| Filtro, vista o modo inválidos | 422 (automático) |
| Equipo inexistente | 404 `{"detalle": "equipo desconocido: XYZ"}` |
| Jugada inexistente | 404 |
| Módulo que falló al construir | 200 con datos de mentira, `n = 0`, error visible en `api/estado-datos` |

## Pruebas

| Prueba | Dónde | Espera |
|---|---|---|
| 5 casos sintéticos de relojes | `verifica_carrera.py` (tablas pequeñas escritas en el script) | Resultados de la skill |
| Curvas no decrecientes, 41 puntos | idem | Verdadero |
| Reparto suma 100 | idem | ± 0.1 |
| Separación del cuadro = distancia receptor ↔ defensor | idem, sobre `api/jugada` | Diferencia < 0.05 yd |
| Números contra `resultados-carrera.md` | idem | ± 0.5 puntos |
| Tiempo por endpoint | idem | < 300 ms |
