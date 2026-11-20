# Diseño · Esqueleto compartido

## Visión general

Una sola app: FastAPI sirve la API bajo `api/` y el build de Vite (`dashboard/dist`) en la misma URL. El backend carga y precalcula todo en memoria al arrancar; los endpoints solo filtran. El dashboard es una página con menú lateral; cada sección pide sus endpoints al montarse.

```
Navegador ── fetch('api/…') ──► routers/carrera.py (A) ─┐
                               routers/giro_aire.py (B) ┤──► calculos/* ──► base/* ──► data_loader.py ──► data/*.csv
                                                         └──► estado de carga (hilo)
```

## Backend

### Lo que se reutiliza de la práctica

`normalizacion.py` (giro de 180°, línea de golpeo), `columnas.py`, `config.py`, la carga en segundo plano de `main.py` con `/health` y `api/estado-datos`, y la llegada de presión a 2 yd de la asistencia invisible. Lo de asistencias, huella y disfraz se borra (queda en la etiqueta de Git de la práctica).

### Módulos nuevos del esqueleto

| Archivo | Responsabilidad | Salida |
|---|---|---|
| `data_loader.py` | Leer semanas, normalizar, recortar jugadores y cuadros, guardar en el estado global | `cuadros` (recortado), `cuadros_completos` (solo jugadas ejemplo, se llena después), `plays`, `players`, `pff`, `games` |
| `base/situacion.py` | Banderas de filtros, vista, conversión, eventos por jugada | tabla `jugadas` |
| `base/separacion.py` | Distancia receptor ↔ defensor más cercano por cuadro | tabla `sep_cuadros` |
| `base/presion.py` | Primer cuadro con un rusher a ≤ 2 yd del QB, con las reglas de `pregunta.md` | tabla `presion` |
| `base/objetivo.py` | Receptor más cercano al balón en la llegada | tabla `objetivo` |
| `esquemas/comun.py` | Modelos compartidos: `Intervalo`, `EstadoDatos`, errores | — |
| `esquemas/carrera.py`, `esquemas/giro_aire.py` | Un modelo Pydantic por respuesta del contrato | — |
| `routers/carrera.py`, `routers/giro_aire.py` | Endpoints del contrato con datos de mentira | — |
| `calculos/*.py` | Funciones vacías con su firma y valor de mentira | — |

### Estado global y carga

- Un objeto de estado (módulo `estado` dentro de `main.py` o `data_loader.py`) con: `cargando`, `listo`, `error`, `semanas`, las tablas base y un diccionario `resultados` donde cada módulo de `calculos/` guarda lo suyo.
- Orden al cargar: tracking → tablas base → `calculos` de B (giros, vuelo, mapas) → `calculos` de A (relojes, síntesis, ejemplos) → ticker. Si un cálculo falla, se registra el error y ese endpoint sigue con datos de mentira (la app no se cae).
- Dependencia `requiere_datos()` en los routers: si `listo` es falso, 503.

### Memoria

Las 8 semanas pesan ~1 GB en CSV. Leer por semana con `usecols` y tipos `float32`/`int32`/`category`, recortar y concatenar. Meta: menos de 1.5 GB en memoria. Medirlo y escribirlo en `ESTADO.md`.

## Frontend

### Estructura

| Carpeta / archivo | Contenido |
|---|---|
| `index.html` | `<link>` de Google Fonts (Barlow Condensed, Inter, JetBrains Mono) |
| `tailwind.config.js` | Colores del tema (`fondo`, `panel`, `tarjeta`, `borde`, `texto`, `tenue`, `acento`, `receptor`, `defensa`, `sinpresion`, `balon`) y familias de fuente |
| `index.css` | Directivas de Tailwind 3, keyframes `cinta`, `pulso`, `aparece`, regla de `prefers-reduced-motion` |
| `estado/Contexto.tsx` | `seccion`, `vista`, `filtro`, `equipo` y sus setters |
| `hooks/useApi.ts` | Carga con estados `cargando`/`listo`/`error`, reintento con 503 |
| `hooks/useTween.ts` | Progreso 0→1 con salida cúbica |
| `lib/colores.ts` | Paleta y `colorCalor(valorNorm)` |
| `lib/formato.ts` | Porcentajes, segundos, yardas |
| `api.ts` | Una función por endpoint; `USAR_MOCKS` por endpoint |
| `types.ts` | Tipos del contrato |
| `mocks/*.json` | Un archivo por endpoint |
| `componentes/` | `Tarjeta`, `Kpi`, `Insight`, `Segmentado`, `EstadoCarga`, `Leyenda`, `CampoBase` |
| `layout/` | `Sidebar`, `Encabezado`, `Ticker` |
| `secciones/` | 6 archivos con "En construcción · dueña: A/B" |
| `App.tsx` | Cinta arriba; fila con menú y contenido (flex-wrap); `key` de la sección = sección + filtro + vista + equipo |

### Interfaces de los componentes comunes

| Componente | Props | Qué hace |
|---|---|---|
| `Tarjeta` | `titulo`, `subtitulo?`, `children`, `acciones?` | Caja con título Barlow y subtítulo tenue |
| `Kpi` | `etiqueta`, `valor` (número), `formato`, `sub`, `color` | Número grande que cuenta hacia arriba con `useTween` |
| `Insight` | `texto` | Franja con borde izquierdo de acento |
| `Segmentado` | `opciones` (valor, etiqueta), `valor`, `alCambiar`, `etiquetaAria` | Botones con `aria-pressed` |
| `EstadoCarga` | `estado`, `alto` | Esqueleto gris, aviso de 503 o error con reintento |
| `Leyenda` | `elementos` (color, texto, forma) | Leyenda horizontal |
| `CampoBase` | `ventana` (x mín y máx), `lineaGolpeo?`, `primerDown?`, `children` | Contenedor `aspect-ratio 600/533`, SVG de líneas; los hijos se dibujan encima |

## Manejo de errores

- Backend: un cálculo que falla no tumba la app; queda en `api/estado-datos.error` y ese endpoint responde con datos de mentira y `n = 0`.
- Frontend: cada sección maneja sus estados con `EstadoCarga`; nunca una pantalla en blanco.

## Pruebas

- `scratch/verifica_esqueleto.py`: estado, forma de cada endpoint, tiempo de respuesta < 300 ms.
- Build de Vite sin errores; `--check` en verde; prueba sin `.env`.
