# Diseño · Dashboard del giro y el aire (Persona B)

## Archivos

| Archivo | Contenido | Datos |
|---|---|---|
| `componentes/MapaCalor.tsx` | Mapa difuminado sobre la cancha | prop `respuesta` (de `api/mapa`), `lectura` |
| `componentes/Trayectorias.tsx` | Arcos del balón animados | prop `trayectorias` (de `api/vuelo/resumen`) |
| `layout/Ticker.tsx` | Cinta superior | `api/ticker` |
| `secciones/P2Giro.tsx` | Barras, matriz, mapa capa giro | `api/giros/resumen`, `api/mapa?capa=giro` |
| `secciones/P3Aire.tsx` | Pendiente, barras, trayectorias, mapa capa vuelo | `api/vuelo/resumen`, `api/mapa?capa=vuelo` |
| `secciones/ComoLeer.tsx` | Definiciones y créditos | texto |

Usa los comunes del esqueleto: `Tarjeta`, `Insight`, `Segmentado`, `EstadoCarga`, `Leyenda`, `CampoBase`, `useApi`, `useTween`, `colorCalor` de `lib/colores.ts` y el contexto.

## `MapaCalor`

Detalle en la skill `mapas-de-calor`. Estructura: `CampoBase` como contenedor; dentro, primero la cuadrícula CSS (24 × 21, `filter: blur(9px)`, `scale(1.03)`), luego el SVG de líneas sin desenfoque y las etiquetas de profundidad. El selector de modo vive en la tarjeta (`Segmentado`) y cambia el parámetro `modo` de `useApi`. Opacidad por celda × progreso de `useTween`.

## `Trayectorias`

SVG de 1000 × 300. QB en (70, 236). Destinos en x = 210, 360, 520, 700, 900 para las 5 profundidades; arco cuadrático con altura proporcional a la profundidad. Por destino: arco punteado amarillo, círculo del receptor coloreado por la pérdida (verde → rojo), y una elipse café con `<animateMotion>` (`dur` = tiempo de vuelo × 1.5 s, `repeatCount="indefinite"`, `rotate="auto"`, `path` = el del arco). Debajo: "11–15 yd" y "−1.2 yd". Con movimiento reducido: balón quieto en el punto más alto.

## Gráficas con Recharts 3

| Gráfica | Componentes | Notas |
|---|---|---|
| Separación por tipo de giro | `BarChart` con x = franja y 3 `Bar` (sin giro gris, suave ámbar, brusco acento), `LabelList` "+1.6", `ErrorBar` | `animationDuration` 1200 |
| Pendiente al lanzar → al llegar | `LineChart` con x categórica ("Al lanzar", "Al llegar"), una `Line` por franja con puntos, `ReferenceLine` en y = 3 ("libre: 3 yd"), etiquetas al final de cada línea con la pérdida | Colores: corta gris, media ámbar, larga defensa |

## Hechas con `div` y `useTween`

- Matriz ángulo × velocidad: cuadrícula 6 × 5; cada celda con `colorCalor(valor_norm)`, texto blanco u oscuro según el fondo, opacidad con retraso por posición (efecto escalonado); ejes con etiquetas.
- Barras de % sigue libre (acento) y % completo (amarillo) por franja: ancho × progreso.

## `Ticker`

Contenedor de altura 44 px y `overflow: hidden`; etiqueta roja fija a la izquierda; fila con la lista duplicada y la animación `cinta` lineal (~55 s). Colores de la flecha: receptor verde, defensa roja, sin presión azul, giro acento, aire amarillo.

## Insights

Vienen de la API (`insight` de `api/giros/resumen` y `api/vuelo/resumen`).

## Verificación

- Con mocks: cada sección completa, mapas que reaparecen al cambiar el modo, balones que tardan más cuanto más profundos.
- Con la API: campos completos; números como en `scratch/resultados-giro-aire.md`.
- Build sin errores de TypeScript.
