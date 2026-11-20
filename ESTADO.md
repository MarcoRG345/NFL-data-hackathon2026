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

✓ **Tarea 3 (prototipo):** Giro principal por ruta
  - Archivo: `scratch/prueba_giros.py`
  - Ventana corregida: dir(t+0.25s) - dir(t-0.25s)
  - % brusco: 6.9% (coherente con prueba de vida: 4.3%)

✓ **Tarea 2:** Giro por cuadro (función real) - COMPLETO
  - **Archivo:** `backend/calculos/giros.py`
  - **Función:** `giro_por_cuadro(cuadros)` - Vectorizada
  - **Verificación:** `scratch/verifica_giro_aire.py` - 4 casos sintéticos ✓
  - **Aviso a A:** Función vectorizada disponible para uso en síntesis

✓ **Tarea 3:** Giro principal por ruta (función real) - COMPLETO
  - **Archivo:** `backend/calculos/giros.py`
  - **Función:** `construir_giros(cuadros, plays, players, pff)`
  - **Implementación:**
    - Giro principal = mayor |Δdir| válido entre 0.5s post-snap y pass_forward
    - Rutas sin giro: sep_ganada medida desde tiempo mediano de giros (igualdad de condiciones)
    - Tipos: sin_giro (<30°), suave (30-60°), brusco (≥60°)
  - **Prueba:** `scratch/prueba_giros_modulo.py` - 4433 rutas analizadas

✓ **Tarea 4:** Resumen de giros e H2 - COMPLETO
  - **Función:** `giros.resumen(filtro)` - Por tipo con IC 90%
  - **H2 parcial:** El giro brusco conserva separación (+0.35 yd vs sin giro, IC NO se solapan) pero no aumenta el % libre en pass_forward (IC se solapan)
  - **Insight:** "H2 parcial: el giro brusco conserva separación (+0.35 yd vs sin giro) pero no aumenta el % libre en pass_forward (IC se solapan)."
  - **Resultados:** `scratch/resultados-giro-aire.md` actualizado con H2

✓ **Tareas 5 y 6:** Ventaja al lanzar (vuelo) - COMPLETO Y CORREGIDO
  - **Archivos creados:**
    - `backend/calculos/vuelo.py` - Módulo de ventaja al lanzar (constantes inline)
    - `backend/calculos/__init__.py` - Inicializador
    - `scratch/prueba_vuelo_modulo.py` - Pruebas del módulo con tablas principal y robustez
  
  - **Funciones implementadas:**
    - `vuelo.construir(usar_respaldo=False)` - Tabla de ventaja por jugada
    - `vuelo.sigue_libre_por_jugada()` - **REAL** - Para síntesis de A
    - `vuelo.resumen(ventaja_df, ventaja_robustez_df)` - Resumen con IC 90% por bootstrap
  
  - **Corrección aplicada (identificación de objetivo):**
    - Búsqueda mejorada: " to " (pases) o "intended for " (intercepciones)
    - Normalización: quitar Jr., Sr., II, III, IV, guiones
    - Usar inicial si hay dos receptores con mismo apellido
    - Sin objetivo (spike, throwaway): valido=false, fuera de H3
    - Respaldo SOLO en tabla de robustez (no en principal)
  
  - **H3 confirmado (tabla principal, n=778 por nombre):**
    - Abierto (≥3 yd) vs Cerrado (<1.5 yd): 88.7% - 58.0% = **+30.7 puntos** (IC 90% no se solapan)
    - Abriéndose vs Cerrándose: 90.2% - 77.8% = **+12.4 puntos** (IC 90% no se solapan)
  
  - **Cobertura (semana 1, 1051 pases totales):**
    - Por nombre: 778 (74.0%) - **tabla principal**
    - Sin objetivo: 50 (4.8%) - spike, throwaway (valido=false)
    - Aproximados: 223 (21.2%) - **solo tabla de robustez**
  
  - **Constantes:**
    - ABIERTO_YD = 3.0
    - SEP_CERRADA_YD = 1.5 (actualizado)
    - TENDENCIA_UMBRAL_YD = 0.5
    - IC_NIVEL = 0.90 (90%, no 95%)
    - BOOTSTRAP_REPS = 1000, SEMILLA = 42

### Avisos para A:

🔔 **`giro_por_cuadro()` está REAL y VERIFICADO**
  - Ubicación: `backend/calculos/giros.py`
  - Firma: `giro_por_cuadro(cuadros)`
  - Retorna: DataFrame con giro_grados, girando, valido (columnas añadidas)
  - Vectorizado: procesa todo el tracking de una vez
  - Verificación: 4 casos sintéticos en `scratch/verifica_giro_aire.py`

🔔 **`vuelo.sigue_libre_por_jugada()` está REAL**
  - Ubicación: `backend/calculos/vuelo.py`
  - Firma: `sigue_libre_por_jugada(cuadros, plays, players, pff)`
  - Retorna: DataFrame con gameId, playId, valido, sigue_libre
  - Significado: sigue_libre = objetivo a ≥3 yd en pass_forward
  - Cobertura semana 1: 778 jugadas (74.0% del total de pases)

### Pendiente:

- [ ] Tarea 7: Mapas de calor
- [ ] Tarea 8: Cinta
- [ ] Tarea 9: Integración con A
- [ ] Tarea 10: Verificación final

### Notas:

- **H2 parcial:** El giro brusco conserva separación (+0.35 yd vs sin giro, IC NO se solapan) pero no aumenta el % libre en pass_forward (IC se solapan)
- **H3 confirmada:** La ventaja al lanzar SÍ predice conversión (+30.7 pp abierto vs cerrado, IC no se solapan)
- **Prioridad narrativa:** P3 (ventaja al lanzar) > P2 (giros)
