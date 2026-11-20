# Diseño · Dashboard de la carrera (Persona A)

## Archivos

| Archivo | Contenido | Datos |
|---|---|---|
| `componentes/CanchaJugada.tsx` | Replay táctico | prop `jugada` (respuesta de `api/jugada`) |
| `componentes/Cuadrante.tsx` | Dispersión de equipos | prop `equipos`, `medianas`, `seleccionado`, `alElegir` |
| `componentes/Embudo.tsx` | Cadena con eslabón débil | prop `pasos`, `eslabon` |
| `secciones/Resumen.tsx` | KPIs, replay, cadena de la liga | `api/resumen`, `api/jugadas-ejemplo`, `api/jugada` |
| `secciones/P1DosRelojes.tsx` | Curvas, distancia, resultado | `api/carrera/curvas`, `/distancia`, `/resultado` |
| `secciones/Sintesis.tsx` | Cuadrante, embudo, tabla | `api/equipos`, `api/resumen` (con equipo) |

Usa los comunes del esqueleto: `Tarjeta`, `Kpi`, `Insight`, `Segmentado`, `EstadoCarga`, `Leyenda`, `CampoBase`, `useApi`, `useTween` y el contexto.

## `CanchaJugada`

Detalle completo en la skill `cancha-y-jugadores`. Estado interno: `cuadro`, `reproduciendo`, `velocidad`, `flechasTodos`. Un `setInterval` de 100 ms / velocidad que se limpia al pausar, al cambiar de jugada y al desmontar. Distribución: cancha (3 partes) y panel lateral de relojes y leyenda (1 parte) en una fila con `flex-wrap`; controles debajo de la cancha.

## Gráficas con Recharts 3

| Gráfica | Componentes de Recharts | Notas |
|---|---|---|
| Curvas de la carrera | `ComposedChart`, `XAxis` (t, 0–4 s), `YAxis` (0–100%), `CartesianGrid` punteada, `Area` bajo la curva de libre, 2 `Line` sin puntos, `ReferenceArea` entre las medianas, 2 `ReferenceLine` con etiqueta | `animationDuration` 1500; colores `receptor` y `defensa` |
| Conversión por distancia | `BarChart` con 2 `Bar` (gana receptor, gana defensa), `LabelList` arriba, `ErrorBar` con los intervalos | Eje y 0–80% |
| Cuadrante | `ScatterChart`, `XAxis` (t_presion), `YAxis` (P1), 2 `ReferenceLine` en las medianas, 4 `ReferenceArea` tenues, `Scatter` con forma propia (círculo de 40 px con la abreviatura) y `onClick` | Seleccionado en `acento`; etiquetas de cuadrante en las esquinas |

## Hechas con `div` y `useTween`

- KPIs: número × progreso.
- Cadena de la liga y `Embudo`: ancho × progreso; eslabón en `defensa` con la etiqueta "Eslabón débil −X%".
- Barra apilada de resultados: 3 segmentos con ancho × progreso y texto en Barlow.
- Tabla de Síntesis: `<table>` con encabezados que son botones (ordenan) y filas clicables; fila seleccionada en tono acento; chips con verde (≥ mediana + 5), ámbar o rojo (≤ mediana − 5); contenedor con `overflow-x: auto` y altura máxima con desplazamiento.

## Animación al cambiar de opción

`App.tsx` monta la sección con `key = seccion-filtro-vista-equipo` (esqueleto). Dentro de cada sección, un solo `useTween(900)` alimenta los `div`; Recharts usa su animación propia.

## Insights que arma el frontend

- P1: "El receptor se libera en mediana {ventaja} s antes de que llegue la presión: la ventana existe, hay que verla." (con `mediana_libre`, `mediana_presion` y `ventaja` de la API).
- Síntesis: "{equipo} se rompe sobre todo en {eslabon}. Ese es el paso que conviene corregir primero."
- Resumen: el `insight` viene de `api/resumen`.

## Verificación

- Con mocks: cada sección se ve completa y anima al cambiar filtro y equipo.
- Con la API: ningún campo faltante; los números coinciden con `scratch/resultados-carrera.md`.
- Build sin errores de TypeScript.
