---
name: estadistica-intervalos
description: Reglas de estadística del proyecto (bootstrap por jugada, intervalos de 90% para proporciones, medias, medianas y diferencias, mínimos de n, pruebas de robustez y cómo redactar los resultados) para que todos los números del backend sean comparables y honestos. Úsala en cualquier cálculo que se muestre en el dashboard.
---

# Estadística e intervalos

## Unidad de remuestreo

Siempre la **jugada** (o la ruta cuando la métrica es por ruta), nunca el cuadro: los cuadros de una misma jugada no son independientes.

## Bootstrap estándar

- 1000 repeticiones, semilla 42 (`numpy.random.default_rng(42)`), percentiles 5 y 95 (intervalo de 90%).
- Vectorizado: una matriz de índices de tamaño repeticiones × n con `rng.integers`, y la métrica calculada sobre esa matriz de una vez. Nada de ciclos de 1000 vueltas con pandas dentro.
- Para una **diferencia** (por ejemplo, conversión si gana el receptor menos si gana la defensa), remuestrea cada grupo por separado en cada repetición y resta. El intervalo es el de la diferencia, no la resta de dos intervalos.
- Para **medianas** de tiempo, bootstrap de la mediana.

## Atajo para proporciones grandes

Con n ≥ 200, se puede usar el intervalo de Wilson al 90% en lugar del bootstrap (más rápido). Declara cuál usaste en `scratch/resultados-*.md`.

## Mínimos de n

| Unidad | Mínimo | Si no llega |
|---|---|---|
| Equipo | 30 jugadas | Se muestra, marcado `n_bajo`, sin eslabón ni cuadrante (o con "—") |
| Grupo de distancia o franja | 20 | Valor `None` y aviso |
| Celda de la matriz de giros | 20 rutas | Celda vacía |
| Celda del mapa de calor | 5 rutas | No se manda |
| Filtro completo | 100 jugadas | Aviso "Muy pocas jugadas para este filtro" |

## Comparaciones múltiples

Con 32 equipos y un intervalo de 90%, unos 3 equipos salen "distintos" por puro azar. No destaques a un solo equipo como prueba de nada. Usa los equipos como ilustración y la liga como hallazgo.

## Robustez (obligatoria para H1, H2 y H3)

Repite el número principal cambiando una cosa a la vez y repórtalo en una tabla:
- H1: `RADIO_PRESION` 1.5 / 2.0 / 3.0; `ABIERTO_YD` 2.0 / 3.0 / 4.0; solo cobertura `Man`.
- H2: `GIRO_BRUSCO` 45 / 60 / 90; ventana 0.3 / 0.5 / 0.7 s.
- H3: franjas con cortes en 5/15 y en 10/20.

Si el signo del resultado cambia con alguna variante, el hallazgo no es robusto: dilo así en el insight.

## Cómo redactar

- "En 3.º y 4.º down, cuando el receptor gana la carrera se convierte el 58% (IC 90%: 54–62, n = 562) contra 31% cuando gana la defensa (27–35, n = 401)." Los números de este ejemplo son inventados: usa los reales.
- Nunca "significativo" sin el intervalo al lado. Nunca causalidad ("girar causa…"): asociación ("los giros bruscos se asocian con…").
