---
name: cancha-y-jugadores
description: Cómo construir el componente CanchaJugada en React 18 + TypeScript con SVG y div (sin librerías) para el replay táctico de una jugada: cancha oscura, jugadores con número, flecha de dirección, arco de giro, línea de separación, anillo de presión, trayectoria del balón en arco, relojes y barra de tiempo con marcas. Úsala para cualquier vista del campo con jugadores.
---

# Cancha y jugadores (`componentes/CanchaJugada.tsx`)

Recibe la respuesta de `api/jugada` (contrato) y solo dibuja: no calcula separaciones ni relojes.

## Restricciones

- SVG y `div` hechos a mano. Sin canvas, d3 ni librerías de deportes. Recharts no se usa aquí.
- Las coordenadas ya vienen normalizadas: el ataque va a la derecha. No vuelvas a rotar.

## Sistema de coordenadas

- Ventana fija de 60 yd: de línea de golpeo − 15 a línea + 45; alto completo de 53.3 yd.
- Contenedor con `aspect-ratio: 600 / 533` y `position: relative`. Encima, un SVG con `viewBox="0 0 60 53.3"` y `preserveAspectRatio="none"` para líneas; los jugadores son `div` con `left`/`top` en %.
- Conversión: `left% = (x − (linea − 15)) / 60 × 100`; `top% = (53.3 − y) / 53.3 × 100`.
- Trazos del SVG con `vector-effect="non-scaling-stroke"` para que no se deformen.

## La cancha

- Fondo #13202F, líneas de yarda cada 5 yd en blanco al 13%.
- Línea de golpeo azul #3B82F6 (3 px) y línea de primer down amarilla #FACC15, con etiqueta pequeña abajo.

## Los jugadores

- Círculo con el número de jersey: ataque #1D4ED8, defensa #C2410C, texto blanco.
- Protagonistas (`rol` qb, receptor, defensor, rusher): 30 px, borde blanco de 2 px, encima. Los demás: 22 px, opacidad 0.6.
- **Flecha de dirección**: `svg` posicionado en el centro del jugador y girado con `transform: rotate(θ)`, donde θ = atan2(−vy, vx) en grados (el eje y de la pantalla va hacia abajo). vx = seno(dir), vy = coseno(dir). Largo = 15 + mín(40, s × 6) px. Sin flecha si s < 0.5. Color claro de su equipo (#93C5FD / #FDBA74).
- **Arco de giro**: si `girando`, un arco amarillo (#FFD400) de un cuarto de círculo alrededor del jugador, girado con θ y reflejado (`scaleY(−1)`) si el giro es a la izquierda (`giro_grados` < 0).
- Por defecto, flechas y arcos solo en protagonistas; botón "Flechas de todos".
- Si falta `jersey`, muestra la posición abreviada.

## Lo que va encima

- **Línea de separación** punteada receptor ↔ defensor, con etiqueta "2.8 yd". Verde #4ADE80 si `receptor_libre`, gris si no.
- **Anillo de presión**: círculo de 2 yd alrededor del QB; rojo #FF453A cuando `presion_llego`.
- **Rastro** punteado de la ruta del receptor hasta el cuadro actual.
- **Trayectoria del balón**: desde `t_lanza`, una curva cuadrática punteada amarilla del punto de lanzamiento al de llegada. El balón es una elipse café con borde blanco cuyo tamaño y sombra crecen con `altura` (más grande a mitad del vuelo) y una etiqueta "Vuelo 0.8 s" mientras está en el aire.

## Controles y relojes

- Play/pausa (52 px, acento), volver al snap, barra deslizable de cuadros, velocidades 0.5×, 1× y 2×. Avanza un cuadro cada 100 ms / velocidad con `setInterval`, que se limpia al pausar y al desmontar.
- Marcas bajo la barra: Snap, Se libera, Presión, Lanza, Llega (alternando dos alturas para que no se encimen).
- Panel lateral: "Reloj del receptor" (verde) y "Reloj de la defensa" (rojo) en monoespaciada; cada uno corre con el tiempo y se congela cuando ocurre su evento. Abajo, un letrero "EN JUEGO…" que cambia a "GANA EL RECEPTOR · +0.4 s" o "GANA LA DEFENSA". Leyenda de símbolos.
- Selector de jugadas ejemplo (de `api/jugadas-ejemplo`).

## Si algo tarda (en este orden)

1. Sin arco de giro. 2. Sin trayectoria curva (línea recta). 3. Sin animación: barra deslizable sola.
Nunca se quita la cancha con jugadores, la flecha de dirección y los relojes.

## Verificar

- Con el mock: 22 jugadores + balón; el ataque a la izquierda de la línea, avanzando a la derecha.
- Un receptor que corre hacia la zona de anotación tiene la flecha hacia la derecha.
- La distancia escrita coincide con `separacion` del cuadro.
- El build termina sin errores de TypeScript.
