# Tareas · Dashboard de la carrera (Persona A)

Rama `a-carrera`. Se puede empezar en cuanto exista la etiqueta `esqueleto`, con mocks. Adjunta capturas de la maqueta de cada sección. Al terminar cada tarea: build sin errores y `ESTADO.md`.

- [ ] 1. CanchaJugada: cancha y jugadores
  - Ventana de 60 yd con `CampoBase`, jugadores con número, roles destacados, línea de golpeo y de primer down
  - Barra de tiempo, play/pausa, volver al snap, velocidades
  - _Requisitos: 1.1, 1.7_

- [ ] 2. CanchaJugada: lo que va encima
  - Flecha de dirección (probar que un receptor que avanza apunta a la derecha), arco de giro, línea de separación con yardas, anillo de presión, rastro
  - Balón en arco con altura y etiqueta de vuelo; relojes con letrero; marcas de eventos; "Flechas de todos"
  - _Requisitos: 1.2, 1.3, 1.4, 1.5, 1.6, 1.7_

- [ ] 3. Sección Resumen con mocks
  - Insight, 4 KPIs animados, selector de jugadas ejemplo con `CanchaJugada`, cadena de la liga
  - _Requisitos: 2.1, 2.2_

- [ ] 4. Sección P1 con mocks
  - Curvas con `ComposedChart`, conversión por distancia con `BarChart` e intervalos, barra apilada, insight armado con las medianas
  - _Requisitos: 3.1, 3.2_

- [ ] 5. Cuadrante, Embudo y sección Síntesis con mocks
  - Cuadrante con Recharts y selección de equipo; embudo animado; tabla ordenable con chips de color; los tres sincronizados con el contexto
  - _Requisitos: 4.1, 4.2, 4.3, 4.4_

- [ ] 6. Estados y accesibilidad
  - `EstadoCarga` en cada gráfica, n y leyenda, movimiento reducido, botones con `aria-*` y 44 px
  - _Requisitos: 5.1, 5.2, 5.3, 5.4_

- [ ] 7. Conexión a la API real
  - Por cada endpoint de `logica-carrera` que ya sea real en `main`: apagar su mock, revisar la sección y anotar diferencias en `ESTADO.md` (los campos que no coinciden se corrigen en el backend)
  - Reemplazar el mock de la jugada por la exportada en la tarea 9 de `logica-carrera`
  - Build final sin errores
  - _Requisitos: 6.1, 6.2, 6.3_
