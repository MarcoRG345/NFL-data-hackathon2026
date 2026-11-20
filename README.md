# La carrera de los dos relojes · Kit Two Clocks

## Pregunta

¿Existen dinámicas de dos velocidades en las jugadas de la NFL, donde el receptor corre contra dos relojes diferentes: el tiempo hasta el snap y el tiempo en el aire de la pelota?

Específicamente: ¿Pueden los equipos predecir si un receptor llegará a tiempo para atrapar un balón basándose en su velocidad pre-snap y el tiempo de vuelo estimado? ¿Qué patrones emergen cuando se compara la eficiencia de carrera contra cada reloj?

## Datos

- **Fuente**: Tracking data de la NFL (2021-2023)
- **Alcance**: Jugadas de pase donde el receptor está en movimiento antes del snap
- **Variables clave**:
  - Velocidad y aceleración pre-snap del receptor
  - Tiempo hasta el snap (reloj 1)
  - Tiempo de vuelo del balón (reloj 2)
  - Posición y orientación frame por frame
  - Resultado de la jugada (completo/incompleto, yardas ganadas)

## Método

1. **Reconstrucción de trayectorias**: Identificar el inicio del movimiento, calcular velocidad y distancia recorrida pre-snap
2. **Cálculo de relojes**: 
   - Reloj 1: tiempo disponible hasta el snap
   - Reloj 2: tiempo de vuelo del balón desde release hasta punto de recepción proyectado
3. **Métricas de eficiencia**: 
   - Aprovechamiento del reloj 1 (% de ventaja tomada)
   - Sincronización con reloj 2 (margen de llegada a punto de recepción)
4. **Análisis comparativo**: Bootstrap y estadística de intervalos para patrones por jugador, equipo y situación de juego
5. **Visualización dual**: Dashboard con replay sincronizado de ambos relojes y mapas de calor de eficiencia

## Qué se encontró y cómo se sabe

*(Esta sección se completará con los resultados del análisis. Ejemplos de hallazgos esperados:)*

- Receptores élite toman ventaja de X segundos pre-snap en promedio (intervalo bootstrap 95%: [a, b])
- El 73% de pases completos muestran sincronización óptima con margen de ≤0.3 segundos
- Patrones de giro y aceleración post-snap predicen completions con precisión de X%
- Mapas de calor revelan zonas de eficiencia diferencial por tipo de ruta

**Evidencia**: 
- Gráficas de síntesis de cadenas de carrera
- Intervalos de confianza bootstrap (n≥30 por jugador)
- Replays visuales sincronizados con métricas en tiempo real
- Mapas de calor de giros y eficiencia espacial

### Visualizaciones del Dashboard

#### P1: Dos relojes - La carrera segundo a segundo
![Análisis de la carrera de los dos relojes](docs/images/screenshot-1-dos-relojes.png)

*Gráfica temporal que muestra el porcentaje de jugadas donde el receptor está libre vs. bajo presión, sincronizado con el tiempo desde el snap. Incluye resultados de la carrera (gana receptor vs. sin presión sobre el QB).*

#### P1: Replay de jugadas - Vista de cancha con animación
![Replay de jugada con posiciones de jugadores](docs/images/screenshot-2-replay-receptor.png)

*Visualización interactiva de la cancha que muestra la posición frame por frame de todos los jugadores. Permite seleccionar entre tres escenarios: "Receptor gana la carrera", "Defensa gana la carrera" y "Sin presión sobre el QB".*

![Replay alternativo con presión sobre QB](docs/images/screenshot-3-replay-sin-presion.png)

*Vista alternativa del replay mostrando escenarios donde no hay presión efectiva sobre el quarterback.*

#### P2: El giro - Separación ganada por tipo de giro
![Gráfica de separación por tipo de giro](docs/images/screenshot-4-separacion-giro.png)

*Análisis comparativo de la separación (en yardas) ganada 0.5 segundos después del giro, clasificada por tipo: sin giro, giro suave y giro brusco. Muestra el impacto de diferentes técnicas de cambio de dirección en la creación de espacio.*

#### P3: Ventaja al lanzar - Análisis de separación y tendencias
![Gráficas de porcentaje completo por separación y tendencia](docs/images/screenshot-5-ventaja-lanzar.png)

*Dos gráficas que muestran:*
- *Porcentaje de pases completos según la separación al momento del lanzamiento (cerrado, disputado, abierto)*
- *Porcentaje de pases completos según la tendencia del receptor al momento del lanzamiento (abriéndose, estable, cerrándose)*

## Cómo se ejecuta

### Instalación

```bash
# Backend (Python)
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt

# Frontend (TypeScript + React)
cd dashboard
npm install
```

### Ejecución en desarrollo

```bash
# Terminal 1: Backend API
cd backend
.venv\Scripts\Activate.ps1
python src/main.py

# Terminal 2: Dashboard
cd dashboard
npm run dev
```

El dashboard estará disponible en `http://localhost:5173` y consumirá la API en `http://localhost:8000`.

### Verificación

```bash
# Verificar que los datos se cargan correctamente
python backend/src/main.py --check

# Ejecutar tests (cuando estén implementados)
cd backend && pytest
cd dashboard && npm test
```

---

## Contenido del Kit

Todo lo que Kiro y el equipo necesitan para construir el backend y el dashboard con el stack del hackathon, en paralelo entre dos personas.

### Qué hay y dónde va

Copia cada archivo a la misma ruta dentro de `hackathon-unam/`.

### Steering (Kiro la lee siempre)

| Archivo | Qué es | Acción |
|---|---|---|
| `pregunta.md` | Pregunta, definiciones, cadena, constantes | Reemplaza al anterior |
| `equipo.md` | Dueños de archivos, Git, reglas con Kiro | Reemplaza al anterior |
| `stack-y-arquitectura.md` | Tecnología permitida, carpetas, flujo de datos | Nuevo |
| `contrato-api.md` | 12 endpoints y las 3 funciones que conectan a A con B | Nuevo |

### Skills

| Skill | Para | Quién |
|---|---|---|
| `calculo-carrera` | Tablas base y trampas del tracking | Las dos (esqueleto) |
| `backend-api-datos` | Estructura del backend: carga, estado, caché, 503, JSON, memoria | Las dos |
| `estadistica-intervalos` | Bootstrap, intervalos, mínimos de n, robustez | Las dos |
| `logica-carrera` | Algoritmos de relojes, cadena, resumen y replay | A |
| `logica-giro-aire` | Algoritmos de giros, vuelo, mapas y cinta | B |
| `dashboard-dos-relojes` | Sistema visual, gráficas y animaciones | Las dos |
| `cancha-y-jugadores` | La cancha del replay | A |
| `mapas-de-calor` | Mapas de azul a rojo | B |
| `exploracion-datos-grandes` | (de la práctica, se queda) | Las dos |

Borra la skill vieja `separacion-receptores`.

### Specs (ya escritos: requirements, design y tasks)

| Spec | Quién | Tareas |
|---|---|---|
| `esqueleto` | Juntas, día 1 | 9 |
| `logica-carrera` | A · backend | 11 |
| `dashboard-carrera` | A · frontend | 7 |
| `logica-giro-aire` | B · backend | 10 |
| `dashboard-giro-aire` | B · frontend | 7 |

### Para el equipo

| Archivo | Qué es |
|---|---|
| `docs/equipo/guia-persona-A.md`, `guia-persona-B.md` | Archivos, conexiones, orden recomendado de tareas, checklist |
| `docs/equipo/prompts.md` | Prompts para cada momento y emergencias |
| `docs/equipo/dia-del-evento.md` | Cronograma y prompts de las 3 horas |
| `ESTADO.md` | Memoria compartida (reemplaza al anterior) |

## Paso 0 (juntas, a mano, ~20 minutos)

1. `git tag practica-asistencias` y push del tag.
2. Borrar los specs viejos de `.kiro/specs/` y la skill `separacion-receptores`.
3. Copiar el kit. Revisar que `.gitignore` incluya `data/*.csv`, `scratch/`, `.env`, `.venv/`, `node_modules/`, `dashboard/dist/`.
4. Commit en `main`: "kit two clocks".
5. Prompt "Poner al día la steering vieja" (en `prompts.md`).

## El flujo completo

```
Fase 1  Negocio ......... juntas: aprobar pregunta.md y la división
Fase 2  Datos ........... A: logica-carrera 1        |  B: logica-giro-aire 1
                           ── GO / NO-GO ──  si no pasa: plan B, la asistencia invisible
Esqueleto ............... juntas: esqueleto 1–9 → etiqueta "esqueleto"
Fase 3  Preparación ..... A: relojes + cancha         |  B: giros + MapaCalor
                           ── Merge 1 ──
Fase 4  Modelado ........ A: curvas, H1, cadena, ejemplos + Resumen, P1, Síntesis
                          B: giros, vuelo, H2, H3, mapas, cinta + P2, P3, Cómo leer
                           ── Merge 2: app completa ──
Fase 5  Evaluación ...... integración A↔B, revisión cruzada de números, Renée revisa los replays
Fase 6  Despliegue ...... conexión a la API, verificación con 8 semanas, --check, simulacro
                           ── etiqueta "app-completa" ──
```

El orden exacto, alternando backend y frontend, está en cada guía.

## Por qué no se estorban

- El esqueleto crea desde el día 1 todos los endpoints, tipos, mocks y secciones, con datos de mentira de la forma correcta.
- Cada persona solo toca sus archivos (`equipo.md`). Lo compartido se cambia con un PR pequeño.
- Solo hay 3 conexiones entre A y B, y cada una funciona con datos de mentira hasta que la otra la termine.
- Cada sección conecta su API cuando su endpoint funciona, sin esperar a la otra.

## Cómo se usan los specs en Kiro

Abre el spec en el panel de Kiro: `requirements.md`, `design.md` y `tasks.md` ya están escritos y alineados con el contrato. Ejecuta las tareas una por una (botón de la tarea o prompt "Ejecutar una tarea"). No le pidas que regenere el spec.

## Referencia visual

La maqueta es el lienzo de diseño "La carrera de los dos relojes: dashboard hipotético". Adjunta capturas en el chat de Kiro con el prompt "Construir una sección". El prototipo de Lovable solo sirve de inspiración: su código usa tecnologías prohibidas.
