# Requisitos · Esqueleto compartido

## Introducción

El esqueleto es la base que las dos personas construyen juntas el día 1, en una sola computadora. Deja listas la carga de datos, las tablas base, los contratos (backend y frontend), los datos de prueba y el armazón visual del dashboard. Al terminar, A y B trabajan en paralelo sin depender una de la otra: cada endpoint y cada sección ya existen con datos de mentira que tienen la forma correcta.

Referencias: steering `pregunta.md`, `stack-y-arquitectura.md`, `contrato-api.md`, `equipo.md`; skills `exploracion-datos-grandes`, `calculo-carrera`, `backend-api-datos`, `dashboard-dos-relojes`.

## Requisitos

### Requisito 1: Carga y recorte de datos

**Historia de usuario:** Como analista, quiero que la app cargue las 8 semanas sin quedarse sin memoria, para poder calcular sobre todo el dataset.

#### Criterios de aceptación

1. CUANDO arranca el backend, ENTONCES el sistema DEBE cargar los datos en un hilo aparte y responder `/health` de inmediato.
2. MIENTRAS los datos cargan, el sistema DEBE responder 503 con `{"detalle": "cargando"}` en todo endpoint bajo `api/` excepto `api/estado-datos`.
3. CUANDO se lee cada semana de tracking, ENTONCES el sistema DEBE normalizar con `normalizacion.py` y conservar solo QB, `Pass Route`, `Coverage`, `Pass Rush` y balón, del snap a `pass_arrived` + 5 cuadros.
4. El sistema DEBE excluir las jugadas que dicen "No Play" en `playDescription` y las que no tienen `ball_snap`.
5. El sistema DEBE cargar también `s`, `a`, `dir`, `o` y `jerseyNumber`.
6. CUANDO `DATOS_SEMANAS` está definida, ENTONCES el sistema DEBE cargar solo esas semanas.

### Requisito 2: Tablas base

**Historia de usuario:** Como persona A o B, quiero tablas base comunes, para no recalcular la separación ni la presión cada una por su lado.

#### Criterios de aceptación

1. El sistema DEBE construir `jugadas` (una fila por jugada válida) con situación, banderas de cada filtro, vista ofensiva y defensiva, conversión y cuadros de eventos (`pregunta.md`).
2. El sistema DEBE construir `sep_cuadros` con la separación de cada receptor contra su defensor más cercano en cada cuadro, y la bandera `libre` (≥ `ABIERTO_YD` y t ≥ 1.0 s).
3. El sistema DEBE construir `presion` con `t_presion` por jugada según `pregunta.md`, reutilizando la llegada de presión de la práctica.
4. El sistema DEBE construir `objetivo` con el receptor objetivo por jugada y su validez.
5. CUANDO termina la carga, ENTONCES `api/estado-datos` DEBE responder `listo = true` con `semanas` y `n_jugadas`.

### Requisito 3: Esqueleto del backend

**Historia de usuario:** Como persona A o B, quiero que todos mis endpoints existan desde el día 1, para conectar el dashboard sin esperar a la otra persona.

#### Criterios de aceptación

1. `main.py` DEBE registrar los routers `routers/carrera.py` y `routers/giro_aire.py`.
2. Cada endpoint de `contrato-api.md` DEBE existir y responder datos de mentira con la forma exacta del contrato (modelos Pydantic en `esquemas/`).
3. Cada función de "Conexiones internas" DEBE existir y devolver su valor de mentira documentado.
4. Los archivos de `calculos/` DEBEN existir con sus funciones vacías y una nota de su dueña.

### Requisito 4: Contrato del frontend y datos de prueba

**Historia de usuario:** Como persona A o B, quiero tipos y mocks iguales al contrato, para construir mis secciones antes de que exista el backend.

#### Criterios de aceptación

1. `types.ts` DEBE declarar un tipo por respuesta del contrato, campo por campo.
2. `mocks/` DEBE tener un JSON verosímil por endpoint, marcado como ejemplo, incluida una jugada completa con 22 jugadores y al menos 35 cuadros.
3. `api.ts` DEBE tener una función por endpoint con `fetch('api/...')` sin diagonal inicial y un interruptor de mocks por endpoint.
4. CUANDO un endpoint responde 503, ENTONCES `useApi` DEBE reintentar cada 3 s y exponer el estado "cargando".

### Requisito 5: Armazón visual

**Historia de usuario:** Como usuario del dashboard, quiero navegar por secciones con un menú, para leer la historia en orden.

#### Criterios de aceptación

1. El dashboard DEBE usar el tema oscuro y las fuentes de la skill `dashboard-dos-relojes`, definidos en `tailwind.config.js`, `index.css` e `index.html`.
2. El dashboard DEBE mostrar la cinta superior (con un componente de B que en el esqueleto lee el mock), el menú lateral con 6 secciones, el selector de vista, los 5 filtros y el encabezado con el selector de equipo.
3. CUANDO el usuario elige una sección, filtro, vista o equipo, ENTONCES el contexto global DEBE actualizarse y la sección DEBE volver a montarse para animarse.
4. Cada sección DEBE existir como archivo con un aviso "En construcción" y el nombre de su dueña.
5. El esqueleto DEBE incluir los componentes comunes: `Tarjeta`, `Kpi`, `Insight`, `Segmentado`, `EstadoCarga`, `Leyenda` y `CampoBase` (cancha vacía con líneas de yarda y línea de golpeo).
6. `useTween(ms)` DEBE devolver un progreso de 0 a 1 con salida cúbica y respetar `prefers-reduced-motion`.

### Requisito 6: Verificación del esqueleto

#### Criterios de aceptación

1. `scratch/verifica_esqueleto.py` DEBE llamar con `urllib` a cada endpoint y confirmar que la forma coincide con el contrato.
2. El build del dashboard DEBE terminar sin errores de TypeScript.
3. `.hackathon\setup.cmd --check` DEBE terminar en verde.
4. La carga con 1 semana DEBE tardar menos de 30 s, y se DEBE reportar el tiempo y la memoria con 8 semanas.
