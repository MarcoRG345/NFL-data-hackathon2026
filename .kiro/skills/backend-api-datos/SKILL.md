---
name: backend-api-datos
description: Cómo estructurar el backend FastAPI del proyecto (carga en segundo plano, estado global, tablas en memoria, routers delgados, modelos Pydantic, 503 mientras carga, caché por filtro, aislamiento de errores, conversión de tipos de numpy a JSON, memoria y verificación con urllib) dentro del stack fijo. Úsala para cualquier archivo de backend/.
---

# Backend: API sobre datos en memoria

## Capas (de abajo hacia arriba)

| Capa | Hace | No hace |
|---|---|---|
| `data_loader.py` | Leer CSV, normalizar, recortar, tipos chicos | Calcular métricas |
| `base/` | Tablas comunes (`jugadas`, `sep_cuadros`, `presion`, `objetivo`) | Agregar por equipo o filtro |
| `calculos/` | Métricas, agregados, intervalos; guarda resultados en el estado | Conocer FastAPI o Pydantic |
| `esquemas/` | Modelos Pydantic de respuesta (espejo del contrato) | Lógica |
| `routers/` | Validar parámetros, pedir el resultado, armar el modelo | Calcular con pandas |

Un router nunca hace `groupby`: si lo necesita, la función va en `calculos/`.

## Estado global y carga

- Un solo objeto de estado (por ejemplo una clase con atributos) en un módulo importable: `cargando`, `listo`, `error`, `errores_modulo` (diccionario), `semanas`, `t_inicio`, las tablas base y `resultados` (diccionario por módulo).
- `main.py` arranca un hilo daemon al iniciar la app. El hilo: carga → base → cálculos de B → cálculos de A → ticker → `listo = True`.
- Cada módulo de `calculos/` tiene `construir(estado)`. El hilo lo llama dentro de un try/except: si falla, guarda el mensaje en `errores_modulo[nombre]` y el módulo sigue devolviendo sus datos de mentira. La app nunca se cae por un cálculo.
- Dependencia de FastAPI `requiere_datos` en los routers: si no está `listo`, lanza 503 con `{"detalle": "cargando"}`. `api/estado-datos` y `/health` no la usan.
- Mensajes de progreso por consola (`print("[carga] semana 3/8")`). Nunca archivos de log: la app no escribe a disco.

## Caché

- Lo que depende solo de `filtro` y `vista` (5 × 2 combinaciones) se precalcula al final de `construir`.
- Lo que depende de `equipo` se calcula bajo demanda y se guarda en un diccionario `{(filtro, vista, equipo): resultado}`.
- No uses `lru_cache` con DataFrames como argumento.

## Parámetros

- Declara `filtro`, `vista` y `modo` con `Literal[...]` en la firma del endpoint: FastAPI devuelve 422 solo, sin código extra.
- `equipo`: válido si está en la lista de equipos; si no, 404 con mensaje claro.

## De pandas a JSON (fuente de errores silenciosos)

- Convierte `numpy.float64`, `int64` y `bool_` a tipos de Python (`float()`, `int()`, `bool()`) antes de armar el modelo.
- `NaN` e infinitos no son JSON válido: conviértelos a `None` (y declara el campo como opcional en el modelo).
- Redondea al final: porcentajes y yardas a 1 decimal, tiempos a 2.
- Una función común `a_json(valor, decimales)` en `esquemas/comun.py` hace las tres cosas.

## Memoria y velocidad

- `usecols` y `dtype` al leer: `float32` para coordenadas, `int32` para ids y cuadros, `category` para textos repetidos.
- Lee semana por semana, recorta y concatena. Borra los intermedios (`del`).
- Vectoriza: `merge`, `groupby`, `numpy`. Prohibido `iterrows` y `apply` por fila sobre tracking.
- Metas: carga de 1 semana < 30 s; 8 semanas < 3 min y < 1.5 GB; cada endpoint < 300 ms.

## Verificación

- Scripts en `scratch/verifica_*.py` con `urllib.request` (nunca `requests`). Para cada endpoint: código 200, campos del contrato, tipos y números contra `scratch/resultados-*.md` con tolerancia (±0.5 puntos).
- Pruebas de lógica con DataFrames sintéticos pequeños escritos dentro del script (casos del `design.md` de cada spec). pytest es opcional.
- Ejecutar con `.venv\Scripts\python.exe` y mostrar la salida completa.
