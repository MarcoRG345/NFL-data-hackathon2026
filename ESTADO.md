# ESTADO del proyecto

Memoria compartida del equipo y de los dos Kiros. Cada persona escribe solo en su sección. Lo más nuevo, arriba.

## Decisiones tomadas

| Fecha | Decisión | Quién |
|---|---|---|
| | Pregunta central: la carrera de los dos relojes (ver `pregunta.md`) | Las dos |
| | GO / NO-GO: | Las dos |

## Persona A · carrera y cancha

**Tarea actual:** —
**Funciones reales disponibles para B:** `relojes.resultado_por_jugada()` → (pendiente)

| Fecha | Tarea | Qué quedó | Pendiente |
|---|---|---|---|
| 2026-11-20 | Esqueleto 4 y 5 | Esquemas, routers y `calculos/` de mentira; `backend/estado.py`; `scratch/verifica_esqueleto.py` (36/36 OK con app temporal) | A2 registra los routers en `main.py`; tareas 1–3 del esqueleto |

## Persona B · giro, aire y mapas

**Tarea actual:** —
**Funciones reales disponibles para A:** `giros.giro_por_cuadro(cuadros)` → (pendiente) · `vuelo.sigue_libre_por_jugada()` → (pendiente)

| Fecha | Tarea | Qué quedó | Pendiente |
|---|---|---|---|
| | | | |

## Números clave (los oficiales, con su n)

| Número | Valor | n | Fuente |
|---|---|---|---|
| H1: conversión gana receptor vs gana defensa (3.º/4.º) | | | `scratch/resultados-carrera.md` |
| H2: separación ganada, giro brusco vs sin giro (media) | | | `scratch/resultados-giro-aire.md` |
| H3: % completo, abierto vs cerrado al lanzar | | | `scratch/resultados-giro-aire.md` |
| Carga con 8 semanas: tiempo y memoria | (pendiente, tarea 9) | | `ESTADO.md` |
| Carga con 1 semana (`DATOS_SEMANAS=1`, Linux) | 3.5 s; pico RSS 194 MB; `cuadros` 686,814 filas / 33.0 MB; `eventos` 1,100 filas; `scouting` 45.7 MB; `plays` 8.5 MB. Excluidas: 72 "No Play", 3 sin `ball_snap` | 1,100 jugadas (16 partidos) | tarea 2 del esqueleto |
| Carga + tablas base con 1 semana (Linux) | Carga 3.1 s + base 0.8 s = 3.9 s; pico RSS 211 MB (237 MB con la app). `jugadas` 1,100 filas / 0.3 MB; `sep_cuadros` 180,438 / 6.7 MB; `presion` 1,100; `objetivo` 965 (texto 96.1 %, balón 0.2 %, ninguno 3.7 %). Presión: 28.6 % por distancia, 0.2 % por sack | 1,100 jugadas | tarea 3 del esqueleto (`scratch/prueba_base.py`) |

## Revisión cruzada

## Cambios al contrato

| Fecha | Cambio | Pidió | Aprobó |
|---|---|---|---|
| 2026-11-20 | `api/vuelo/resumen` = ventaja al lanzar (`n_aproximado`, `por_separacion`, `por_tendencia`, `insight`); sin trayectorias; `sigue_libre` = abierto al lanzar | Equipo | Pendiente de B |
# Estado del desarrollo

Última actualización: 2026-11-20

## Sección A (Persona A - Carrera y Síntesis)

Pendiente

## Sección B (Persona B - Giro y Aire)

### Tareas completadas:

✓ **Tarea 1:** Prueba de vida del receptor
  - Archivos: `scratch/prueba_giro_aire.py`, `scratch/resultados-giro-aire.md`
  - Confirmado: tracking se corta 0.5s después de pass_forward
  - P3 redefinido como "ventaja al lanzar"

✓ **Tarea 2:** Giro por cuadro (función real) - COMPLETO Y CONECTADO
  - **Archivo:** `backend/calculos/giros.py`
  - **Función:** `giro_por_cuadro(cuadros)` - Vectorizada
  - **Verificación:** `scratch/verifica_giro_aire.py` - 4 casos sintéticos ✓
  - **Conectado a:** estado global, usa tablas base
  - **Aviso a A:** Función vectorizada disponible

✓ **Tarea 3:** Giro principal por ruta (función real) - COMPLETO Y CONECTADO
  - **Archivo:** `backend/calculos/giros.py`
  - **Función:** `construir(filtro)` lee de estado.tablas, guarda en estado.resultados["giros"]
  - **Conectado a:** cuadros, jugadas, sep_cuadros del estado global
  - **Prueba:** `scratch/prueba_giros_modulo.py` (desactualizado, usar endpoint)

✓ **Tarea 4:** Resumen de giros e H2 - COMPLETO Y CONECTADO
  - **Función:** `giros.resumen(filtro)` - Por tipo con IC 90%
  - **Endpoint:** `GET /api/giros/resumen?filtro=decisivo` ✓
  - **H2 parcial (n=4213 rutas):**
    - Brusco vs Sin giro: +0.34 yd conserva separación (IC NO se solapan)
    - PERO % libre similar (IC se solapan - dato no implementado aún)
  - **Resultados:** Ver sección "RESULTADOS FINALES" en `scratch/resultados-giro-aire.md`

✓ **Tareas 5 y 6:** Ventaja al lanzar (vuelo) - COMPLETO Y CONECTADO
  - **Archivo:** `backend/calculos/vuelo.py`
  - **Funciones conectadas:**
    - `construir(filtro)` lee tabla base `objetivo`, guarda en estado.resultados["ventaja_al_lanzar"]
    - `sigue_libre_por_jugada(filtro)` - **REAL** - Para síntesis de A
    - `resumen(filtro)` - Resumen con IC 90% por bootstrap
  - **Endpoint:** `GET /api/vuelo/resumen?filtro=decisivo` ✓
  
  - **Tabla base objetivo (A2):** 96.4% identificación por texto, SIN respaldo
  
  - **H3 confirmado (n=927 pases):**
    - Abierto (≥3 yd) vs Cerrado (<1.5 yd): 77.4% - 39.0% = **+38.4 puntos** (IC 90% no se solapan)
    - Abriéndose vs Cerrándose: 77.9% - 63.8% = **+14.1 puntos** (IC 90% no se solapan)
  
  - **Insight:** "La ventaja al lanzar predice conversión: +38.4 puntos con objetivo abierto (≥3.0 yd); +14.1 puntos abriéndose vs cerrándose."
  
  - **Constantes en config.py:**
    - ABIERTO_YD = 3.0
    - SEP_CERRADA_YD = 1.5
    - TENDENCIA_UMBRAL_YD = 0.5
    - NIVEL_IC = 0.90 (90%, no 95%)
    - BOOTSTRAP_REPS = 1000, BOOTSTRAP_SEMILLA = 42

### Avisos para A:

🔔 **`giro_por_cuadro()` está REAL y CONECTADO**
  - Ubicación: `backend/calculos/giros.py`
  - Firma: `giro_por_cuadro(cuadros)`
  - Retorna: DataFrame con giro_grados, girando, valido (columnas añadidas)
  - Vectorizado: procesa todo el tracking de una vez

🔔 **`vuelo.sigue_libre_por_jugada()` está REAL y CONECTADO**
  - Ubicación: `backend/calculos/vuelo.py`
  - Firma: `sigue_libre_por_jugada(filtro="decisivo")`
  - Retorna: DataFrame con gameId, playId, valido, sigue_libre
  - Significado: sigue_libre = objetivo a ≥3 yd en frame_lanza
  - Lee de tabla base `objetivo` (96.4% cobertura)

### Backend funcionando:

✅ **Servidor levantado:** `uvicorn backend.main:app --reload --port 8000`

✅ **Endpoints operativos:**
  - `GET /api/vuelo/resumen?filtro=decisivo` → VueloResp
  - `GET /api/giros/resumen?filtro=decisivo` → GirosResp

✅ **Integración completa:**
  - `backend/calculos/vuelo.py` conectado a tabla base `objetivo` ✓
  - `backend/calculos/giros.py` conectado a `cuadros`, `jugadas`, `sep_cuadros` ✓
  - Constantes movidas a `backend/config.py` ✓
  - Estado global en `backend/estado.py` ✓

### Pendiente:

- [ ] Tarea 7: Mapas de calor
- [ ] Tarea 8: Cinta
- [ ] Tarea 9: Integración con A
- [ ] Tarea 10: Verificación final

### Notas:

- **H2 parcial (FINAL):** Giro brusco conserva separación (+0.34 yd vs sin giro, IC NO se solapan), datos de % libre pendientes
- **H3 confirmada (FINAL):** La ventaja al lanzar SÍ predice conversión (+38.4 pp abierto vs cerrado con tabla base objetivo, IC no se solapan)
- **Prioridad narrativa:** P3 (ventaja al lanzar, +38.4 pp) >> P2 (giros, +0.34 yd)
