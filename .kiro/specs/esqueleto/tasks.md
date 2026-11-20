# Tareas · Esqueleto compartido (juntas, día 1)

Una persona maneja Kiro y la otra revisa. Ejecutar una tarea a la vez, con 1 semana de datos. Al final de cada tarea: archivos cambiados, comando corrido y salida.

- [ ] 1. Limpiar lo de la práctica
  - Borrar servicios, endpoints y specs de asistencias, huella y disfraz (ya están en la etiqueta `practica-asistencias`)
  - Conservar `normalizacion.py`, `columnas.py`, `config.py`, la carga en segundo plano, `/health` y `api/estado-datos`
  - Agregar a `config.py` las constantes de `pregunta.md`
  - _Requisitos: 1.1, 3.4_

- [x] 2. Extender la carga de datos
  - `data_loader.py`: columnas `s`, `a`, `dir`, `o`, `jerseyNumber`; recorte por rol y por cuadros; exclusión de "No Play"; `DATOS_SEMANAS`
  - Tipos de columna pequeños y lectura por semana
  - Medir tiempo y memoria con 1 semana y anotarlos en `ESTADO.md`
  - _Requisitos: 1.3, 1.4, 1.5, 1.6_

- [x] 3. Tablas base
  - `base/situacion.py` → `jugadas`; `base/separacion.py` → `sep_cuadros`; `base/presion.py` → `presion` (reutiliza la práctica); `base/objetivo.py` → `objetivo`
  - Ejecutar las verificaciones 1 a 5 de la skill `calculo-carrera` y mostrar sus resultados
  - _Requisitos: 2.1, 2.2, 2.3, 2.4_

- [x] 4. Esquemas y routers con datos de mentira
  - `esquemas/comun.py`, `esquemas/carrera.py`, `esquemas/giro_aire.py` campo por campo con `contrato-api.md`
  - `routers/carrera.py` y `routers/giro_aire.py` con todos los endpoints del contrato y la dependencia de 503
  - Funciones vacías en `calculos/` con su valor de mentira (incluidas las conexiones internas)
  - _Requisitos: 1.2, 2.5, 3.1, 3.2, 3.3, 3.4_

- [x] 5. Verificación del backend
  - `scratch/verifica_esqueleto.py` con `urllib`: estado y forma de cada endpoint
  - Ejecutarlo y mostrar la salida
  - _Requisitos: 6.1_

- [ ] 6. Tema, fuentes y estilos base
  - `tailwind.config.js` (colores y fuentes), `index.css` (directivas de Tailwind 3, keyframes, movimiento reducido), `<link>` de fuentes en `index.html`
  - _Requisitos: 5.1_

- [ ] 7. Contrato del frontend
  - `types.ts` desde `contrato-api.md`; un mock por endpoint (la jugada con 22 jugadores y 35+ cuadros, tomada de una jugada real exportada desde `scratch/`)
  - `api.ts` con interruptor de mocks por endpoint; `hooks/useApi.ts` con reintento por 503
  - _Requisitos: 4.1, 4.2, 4.3, 4.4_

- [ ] 8. Armazón visual
  - `estado/Contexto.tsx`, `hooks/useTween.ts`, `lib/colores.ts`, `lib/formato.ts`
  - Componentes comunes y `CampoBase`
  - `layout/Sidebar.tsx`, `layout/Encabezado.tsx`, `layout/Ticker.tsx` (lee el mock de `api/ticker`)
  - `App.tsx` y las 6 secciones con "En construcción · dueña: A/B"
  - _Requisitos: 5.2, 5.3, 5.4, 5.5, 5.6_

- [ ] 9. Verificación completa y etiqueta
  - Build del dashboard sin errores; `--check` en verde; prueba sin `.env`
  - Tiempo y memoria con 8 semanas en `ESTADO.md`
  - Commit en `main`, etiqueta `esqueleto`, crear ramas `a-carrera` y `b-giro-aire` (lo hace la persona, no Kiro)
  - _Requisitos: 6.2, 6.3, 6.4_
