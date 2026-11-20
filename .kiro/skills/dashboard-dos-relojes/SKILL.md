---
name: dashboard-dos-relojes
description: Sistema visual y de interacción del dashboard Two Clocks (tema oscuro, menú lateral, barra de jugadas clave, tarjetas, gráficas con Recharts 3, animaciones al cambiar de sección) construido solo con React 18, TypeScript, Tailwind 3 y Recharts 3. Úsala para cualquier archivo de dashboard/src.
---

# Dashboard Two Clocks

La maqueta de referencia está en el lienzo de diseño "La carrera de los dos relojes: dashboard hipotético". El prototipo de Lovable sirve solo como inspiración visual: **no copies su código** (usa React 19, Tailwind 4, Radix y lucide, que están prohibidos).

## Restricciones

- Solo React 18 + TypeScript + Tailwind 3 + Recharts 3. Nada que instalar.
- Sin router: la sección activa vive en el contexto global (`estado/`).
- Íconos: SVG en línea con `stroke="currentColor"`.
- `fetch('api/...')` sin diagonal inicial, siempre a través de `api.ts`.

## Tokens (en `tailwind.config.js`, se definen en el esqueleto)

| Token | Valor | Uso |
|---|---|---|
| `fondo` | #0D1015 | página |
| `panel` | #11151B | menú lateral, cajas internas |
| `tarjeta` | #161B22 | tarjetas |
| `borde` | #232A33 | bordes |
| `texto` | #F2F4F7 | texto principal |
| `tenue` | #9AA4B2 | texto secundario (contraste ≥ 4.5:1 sobre tarjeta) |
| `acento` | #FF6B1A | sección activa, botones, KPIs de equipo |
| `receptor` | #2ECC85 | todo lo que es "gana el receptor" / libre |
| `defensa` | #F0443A | presión / gana la defensa |
| `sinpresion` | #3B9EE8 | sin presión |
| `balon` | #F5C542 | balón y vuelo |

Fuentes: títulos y números en `"Barlow Condensed", "Arial Narrow", sans-serif` (700–800, mayúsculas en títulos); texto en `Inter, system-ui`; relojes y cinta en `"JetBrains Mono", monospace`. Se cargan con un `<link>` de Google Fonts en `index.html`; si no cargan, el respaldo debe verse bien.

## Layout

- **Cinta superior** (`layout/Ticker.tsx`): etiqueta roja "JUGADAS CLAVE" con punto que parpadea; texto monoespaciado que se desplaza con la animación CSS `cinta` (la lista se duplica para que el ciclo no tenga salto). Cada elemento con una flecha del color de su tipo.
- **Menú lateral** (`layout/Sidebar.tsx`): logo "2C · TWO CLOCKS / SCOUT ANALYTICS"; selector Ofensiva/Defensiva; 6 secciones (Resumen, P1 · Dos relojes, P2 · El giro, P3 · Balón en el aire, Síntesis · Eslabón débil, Cómo leer esto) con la activa marcada con borde izquierdo de acento; abajo, la caja "Situación de juego" con los 5 filtros y su n. En pantallas angostas el menú queda arriba (flex-wrap), nunca fijo.
- **Encabezado** (`layout/Encabezado.tsx`): kicker "BIG DATA BOWL 2023 · SEMANAS 1–8 · VISTA OFENSIVA", título grande de la sección y selector de equipo.
- **Insight**: franja con borde izquierdo de acento y la frase de la sección (viene de la API).
- **Tarjeta**: fondo `tarjeta`, borde `borde`, radio 16–18 px, padding 24 px, título en Barlow mayúsculas 26 px y subtítulo `tenue` 14 px.

## Catálogo de gráficas (qué componente usar)

| Sección | Gráfica | Cómo se hace |
|---|---|---|
| Resumen | 4 KPIs | `Kpi` común; número con `useTween` |
| Resumen | Replay táctico | `CanchaJugada` (skill `cancha-y-jugadores`) |
| Resumen | Cadena de la liga | barras `div` con ancho animado |
| P1 | La carrera, segundo a segundo | Recharts `ComposedChart`: 2 `Line` (receptor, defensa), `Area` bajo la de receptor, `ReferenceArea` entre las medianas, 2 `ReferenceLine` |
| P1 | Conversión por distancia | Recharts `BarChart` agrupado (receptor / defensa) con etiquetas |
| P1 | Resultado de la carrera | barra apilada de `div` con 3 segmentos |
| P2 | Separación por tipo de giro | Recharts `BarChart` agrupado por franja, 3 colores (gris, ámbar, acento) |
| P2 | Ángulo × velocidad | cuadrícula CSS 6 × 5 con la escala de calor |
| P2 y P3 | Mapa de calor sobre la cancha | `MapaCalor` (skill `mapas-de-calor`) |
| P3 | Separación al lanzar vs al llegar | gráfica de pendiente: Recharts `LineChart` con 2 categorías en x y una línea por franja |
| P3 | % sigue libre y % completo | barras horizontales de `div` por franja |
| P3 | Trayectoria del balón | `Trayectorias`: SVG con arcos por profundidad y un balón que recorre cada arco (`<animateMotion>`), duración = tiempo de vuelo |
| Síntesis | Cuadrante de equipos | Recharts `ScatterChart` con `ReferenceLine` en las medianas, `ReferenceArea` por cuadrante, forma propia con la abreviatura; clic = seleccionar equipo |
| Síntesis | Cadena del equipo | `Embudo`: 5 barras con el eslabón débil marcado |
| Síntesis | Tabla de equipos | `<table>` con encabezados que ordenan, chips verde/ámbar/rojo contra la mediana, fila seleccionada en acento |

Nada de pasteles, 3D, doble eje ni radar. Toda gráfica con leyenda y su n.

## Animación (la app no debe sentirse estática)

- Cada sección se monta con `key={seccion + filtro + equipo}`, así al cambiar de opción todo vuelve a animarse.
- Contenedor de sección con la clase de la animación `aparece` (opacidad y desplazamiento de 10 px, 0.45 s).
- Recharts: `isAnimationActive`, `animationDuration` de 900 a 1500 ms y `animationEasing="ease-out"`.
- `div` y SVG propios: `useTween(900)` da un progreso de 0 a 1 con salida cúbica; multiplica anchos, alturas y números por ese progreso. Los números cuentan hacia arriba.
- Mapas de calor: opacidad de las celdas multiplicada por el progreso; cuadrícula de la matriz con retraso escalonado.
- Respeta `prefers-reduced-motion`: sin animaciones.
- Rendimiento: el progreso se calcula en un solo hook por sección; no animes más de una sección a la vez.

## Estados

- Cargando: rectángulos grises con brillo suave del tamaño de cada gráfica.
- 503: aviso "Cargando datos (semana X de 8)…" y reintento cada 3 s.
- Error: tarjeta roja con el mensaje y botón de reintentar.
- Sin datos para un filtro: "Muy pocas jugadas para este filtro (n = X)".

## Accesibilidad

- Botones reales (`<button>`), `aria-pressed` en interruptores, `aria-current="page"` en la sección activa, `aria-label` en botones de ícono.
- Áreas táctiles de al menos 44 px. Contraste mínimo 4.5:1. Colores que deben distinguirse también difieren en claridad.
