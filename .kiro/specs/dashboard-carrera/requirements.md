# Requisitos · Dashboard de la carrera (Persona A)

## Introducción

Este spec cubre solo el frontend de la persona A: la cancha interactiva del replay y las secciones Resumen, P1 · Dos relojes y Síntesis · Eslabón débil. Se construye primero con los mocks del esqueleto y luego se conecta a los endpoints del spec `logica-carrera`.

Referencias: steering `contrato-api.md`, `stack-y-arquitectura.md`, `equipo.md`; skills `dashboard-dos-relojes`, `cancha-y-jugadores`; maqueta del lienzo de diseño.

## Requisitos

### Requisito 1: Cancha interactiva (`CanchaJugada`)

**Historia de usuario:** Como aficionado, quiero ver la carrera en una jugada real, para entender la idea en segundos.

#### Criterios de aceptación

1. El componente DEBE dibujar la ventana de 60 yd, las líneas de yarda, la línea de golpeo y la de primer down, y los 22 jugadores con su número.
2. CUANDO el usuario mueve la barra de tiempo o pulsa play, ENTONCES jugadores, flechas de dirección, arcos de giro, línea de separación, anillo de presión, rastro, balón y relojes DEBEN redibujarse en ese instante.
3. La flecha de dirección DEBE apuntar hacia donde se mueve el jugador y su largo DEBE crecer con la velocidad.
4. CUANDO `girando` es verdadero en un protagonista, ENTONCES DEBE verse el arco de giro del lado correcto.
5. CUANDO el balón está en el aire, ENTONCES DEBE verse su trayectoria en arco, el balón más grande a mitad del vuelo y la etiqueta del tiempo de vuelo.
6. Los relojes DEBEN correr con el tiempo y congelarse en su evento; el letrero DEBE decir quién ganó y por cuánto.
7. DEBE tener play/pausa, volver al snap, velocidades 0.5×, 1× y 2×, marcas de eventos y el botón "Flechas de todos".

### Requisito 2: Sección Resumen

#### Criterios de aceptación

1. La sección DEBE mostrar el insight, 4 KPIs que cuentan hacia arriba, el selector de jugadas ejemplo con `CanchaJugada` y la cadena de la liga.
2. CUANDO cambian el filtro, la vista o el equipo, ENTONCES los KPIs DEBEN volver a animarse.

### Requisito 3: Sección P1 · Dos relojes

#### Criterios de aceptación

1. La sección DEBE mostrar el insight (armado con las medianas de `api/carrera/curvas`), las curvas acumuladas con la franja de ventaja, la conversión por distancia (barras agrupadas con sus intervalos) y la barra apilada de resultados con el % de sacks con receptor libre.
2. Las curvas DEBEN dibujarse animadas al entrar a la sección o cambiar el filtro.

### Requisito 4: Sección Síntesis · Eslabón débil

**Historia de usuario:** Como entrenador o scout, quiero comparar equipos y ver dónde se rompe la jugada de uno, para saber qué corregir.

#### Criterios de aceptación

1. La sección DEBE mostrar el cuadrante de equipos, la cadena del equipo seleccionado con el eslabón débil marcado y su consejo, y la tabla de equipos.
2. CUANDO el usuario toca un equipo en el cuadrante, la tabla o el selector del encabezado, ENTONCES los tres elementos DEBEN mostrar ese equipo.
3. CUANDO el usuario toca un encabezado de la tabla, ENTONCES la tabla DEBE ordenarse por esa columna.
4. Las celdas de P2, P1 y P3 DEBEN colorearse verde, ámbar o rojo según su distancia a la mediana de la liga.

### Requisito 5: Estados, animación y accesibilidad

#### Criterios de aceptación

1. Cada gráfica DEBE mostrar un esqueleto gris mientras carga, el aviso de 503 con reintento y un error con botón de reintentar.
2. Cada gráfica DEBE mostrar su n y su leyenda.
3. Con `prefers-reduced-motion`, nada DEBE animarse.
4. Todos los controles DEBEN ser botones reales con área táctil de 44 px y `aria-pressed` o `aria-label` según corresponda.

### Requisito 6: Conexión y verificación

#### Criterios de aceptación

1. CUANDO un endpoint de `logica-carrera` es real en `main`, ENTONCES su mock DEBE apagarse en `api.ts` y la sección revisarse contra la API.
2. Ningún número DEBE estar escrito a mano en las secciones.
3. El build DEBE terminar sin errores de TypeScript.
