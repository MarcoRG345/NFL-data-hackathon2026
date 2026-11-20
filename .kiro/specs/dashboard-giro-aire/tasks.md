# Tareas · Dashboard del giro y el aire (Persona B)

Rama `b-giro-aire`. Se puede empezar en cuanto exista la etiqueta `esqueleto`, con mocks. Adjunta capturas de la maqueta de cada sección. Al terminar cada tarea: build sin errores y `ESTADO.md`.

- [ ] 1. Componente MapaCalor con el mock
  - Cuadrícula difuminada con `colorCalor`, líneas encima, etiquetas, `title` por celda, leyenda, lectura, muestra, aviso de muestra pequeña, animación de entrada
  - _Requisitos: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ] 2. Sección P2 con mocks
  - Insight, barras por tipo de giro con intervalos (Recharts), matriz escalonada, `MapaCalor` capa giro con selector de modo
  - _Requisitos: 2.1, 2.2_

- [-] 3. ~~Componente Trayectorias con el mock~~ CANCELADA (sin cuadros del balón en el aire; ver `pregunta.md`)
  - _Requisitos: 3.3_

- [ ] 4. Sección P3 con mocks
  - Insight, pendiente con Recharts, barras de % libre y % completo, `Trayectorias`, `MapaCalor` capa vuelo
  - _Requisitos: 3.1_

- [ ] 5. Cinta y Cómo leer esto
  - `Ticker` con animación sin salto y colores por tipo; `ComoLeer` con tarjetas, fuente y créditos
  - _Requisitos: 4.1, 4.2, 4.3, 5.1, 5.2_

- [ ] 6. Estados y accesibilidad
  - `EstadoCarga` en cada gráfica, n y leyenda, botones con `aria-pressed` y 44 px
  - _Requisitos: 6.1, 6.2_

- [ ] 7. Conexión a la API real
  - Por cada endpoint de `logica-giro-aire` que ya sea real en `main`: apagar su mock, revisar la sección, anotar diferencias en `ESTADO.md` (se corrigen en el backend)
  - Build final sin errores
  - _Requisitos: 6.3, 6.4_
