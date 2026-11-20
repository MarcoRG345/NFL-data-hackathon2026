---
name: mapas-de-calor
description: Cómo calcular en el backend y dibujar en React (sin librerías) los mapas de calor sobre la cancha y la matriz ángulo × velocidad, con escala de azul (frío) a rojo (caliente), celdas relativas a la línea de golpeo, mínimo de n por celda y animación de entrada. Úsala para mapas.py y MapaCalor.tsx.
---

# Mapas de calor

## Backend (`backend/calculos/mapas.py`)

- Coordenadas: x relativa a la línea de golpeo de −15 a 45 yd (24 columnas de 2.5 yd); y de 0 a 53.3 (21 filas).
- Capa `giro`: cada ruta aporta en la posición de su giro principal; valor = separación ganada media.
- Capa `vuelo`: cada pase con objetivo válido aporta en la posición de llegada; valor = separación perdida media.
- `modo`: `decisivo` (3.º y 4.º) o `normal` (1.º y 2.º). `equipo` opcional (según la vista).
- Solo se mandan celdas con n ≥ 5. `valor_norm` = (valor − mín) / (máx − mín) sobre las celdas mandadas.
- Agrega con `groupby` de columna y fila; nada de ciclos por ruta.

## Escala de color (`lib/colores.ts`)

Cinco paradas, de frío a caliente: #1D3FD6 → #2BA8F0 → #F4E04D → #FF8A1F → #E3170A. Interpolación lineal en RGB según `valor_norm`. La misma función colorea la matriz ángulo × velocidad de P2.

## Frontend (`componentes/MapaCalor.tsx`)

- Contenedor con `aspect-ratio: 600 / 533`, fondo #0E1726, esquinas redondeadas.
- Capa 1: cuadrícula CSS de 24 × 21 `div`; cada celda con su color y opacidad `0.55 + 0.45 × valor_norm`; las celdas sin dato, transparentes. A la cuadrícula se le aplica `filter: blur(9px)` y `scale(1.03)` para el aspecto difuminado.
- Capa 2 (encima, sin desenfoque): SVG con líneas de yarda y la línea de golpeo punteada en blanco, más las etiquetas "Línea de golpeo", "+15 yd", "+30 yd".
- `title` en cada celda: "+12.5 yd de la línea: +1.8 yd (n = 34)".
- Al lado: barra de leyenda con el degradado, extremos "Frío · valor mínimo" y "valor máximo · Caliente", lectura rápida en una frase y la muestra (n).
- Selector Normal / 3.º y 4.º down.
- Animación: la opacidad de cada celda se multiplica por el progreso de `useTween` (aparece en 0.9 s).

## Reglas

- Siempre con leyenda y n. Si n total < 100, mostrar "Muestra muy pequeña" en lugar del mapa.
- Nunca dibujes el mapa alrededor del mariscal (así fue el ganador de 2023); estos mapas son de los receptores en la cancha.
