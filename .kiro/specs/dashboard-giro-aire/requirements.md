# Requisitos · Dashboard del giro y el aire (Persona B)

## Introducción

Este spec cubre solo el frontend de la persona B: los mapas de calor, la cinta de jugadas clave y las secciones P2 · El giro, P3 · Ventaja al lanzar y Cómo leer esto. Se construye primero con los mocks del esqueleto y luego se conecta a los endpoints del spec `logica-giro-aire`.

Referencias: steering `contrato-api.md`, `stack-y-arquitectura.md`, `equipo.md`, `pregunta.md`; skills `dashboard-dos-relojes`, `mapas-de-calor`; maqueta del lienzo de diseño.

## Requisitos

### Requisito 1: Mapa de calor sobre la cancha (`MapaCalor`)

#### Criterios de aceptación

1. El componente DEBE dibujar la cuadrícula de 24 × 21 con la escala de azul a rojo, difuminada, debajo de las líneas de yarda y la línea de golpeo.
2. Las celdas sin dato DEBEN quedar transparentes; cada celda con dato DEBE tener un `title` con posición, valor y n.
3. Al lado DEBEN verse la leyenda con el degradado y sus extremos, una lectura en una frase y la muestra.
4. SI el n total es menor a 100, ENTONCES el componente DEBE mostrar "Muestra muy pequeña" en lugar del mapa.
5. CUANDO cambia el modo (Normal / 3.º y 4.º down), ENTONCES las celdas DEBEN volver a aparecer animadas.

### Requisito 2: Sección P2 · El giro

**Historia de usuario:** Como aficionado, quiero ver cómo un giro libera al receptor, para entender el "cómo" de la carrera.

#### Criterios de aceptación

1. La sección DEBE mostrar el insight, las barras de separación ganada por franja y tipo de giro con sus intervalos, la matriz ángulo × velocidad conservada y el mapa de calor de la capa giro.
2. La matriz DEBE usar la misma escala de color que el mapa, mostrar el % en cada celda (vacía si es `null`) y aparecer escalonada.

### Requisito 3: Sección P3 · Ventaja al lanzar

#### Criterios de aceptación

1. La sección DEBE mostrar el insight, las barras de % completo por franja de separación al lanzar (cerrado, disputado, abierto) y por tendencia (cerrándose, estable, abriéndose), ambas con su intervalo de 90% y su n, y el mapa de calor de la capa vuelo.
2. La sección DEBE avisar cuántos objetivos son aproximados (`n_aproximado`) y mostrar vacía (sin barra) cualquier categoría con `ic` en `null`.
3. El componente `Trayectorias` queda CANCELADO: no hay cuadros del balón en el aire y `api/vuelo/resumen` ya no trae trayectorias.

### Requisito 4: Cinta de jugadas clave

#### Criterios de aceptación

1. La cinta DEBE mostrar "JUGADAS CLAVE" con un punto que parpadea y desplazar los textos de `api/ticker` sin salto al reiniciar.
2. La flecha de cada texto DEBE tener el color de su tipo.
3. Con `prefers-reduced-motion`, la cinta DEBE quedarse quieta.

### Requisito 5: Sección Cómo leer esto

#### Criterios de aceptación

1. La sección DEBE mostrar en tarjetas las definiciones de `pregunta.md` (momento decisivo, relojes, receptor libre, quién gana, giro, ventaja al lanzar, eslabón débil, n e intervalos).
2. DEBE incluir la fuente de los datos, las aproximaciones (incluido que el tracking termina ~0.5 s después del lanzamiento y el receptor objetivo sale del texto de la jugada) y los créditos (LichtLab y Decision Time).

### Requisito 6: Estados, accesibilidad, conexión y verificación

#### Criterios de aceptación

1. Cada gráfica DEBE manejar carga, 503 y error con `EstadoCarga`, y mostrar su n y su leyenda.
2. Todos los controles DEBEN ser botones reales con área táctil de 44 px y `aria-pressed`.
3. CUANDO un endpoint de `logica-giro-aire` es real en `main`, ENTONCES su mock DEBE apagarse y la sección revisarse.
4. Ningún número DEBE estar escrito a mano; el build DEBE terminar sin errores.
