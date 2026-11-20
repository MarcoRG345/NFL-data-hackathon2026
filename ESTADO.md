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

✓ **Tareas 5 y 6:** Ventaja al lanzar (vuelo) - COMPLETO
  - **Archivos creados:**
    - `backend/calculos/vuelo.py` - Módulo de ventaja al lanzar (constantes inline)
    - `backend/calculos/__init__.py` - Inicializador
    - `scratch/prueba_vuelo_modulo.py` - Pruebas del módulo
  
  - **Funciones implementadas:**
    - `vuelo.construir()` - Tabla de ventaja por jugada con respaldo
    - `vuelo.sigue_libre_por_jugada()` - **REAL** - Para síntesis de A
    - `vuelo.resumen()` - Resumen con IC por bootstrap
  
  - **H3 confirmado:**
    - Abierto vs Cerrado: +32.7 puntos (IC no se solapan)
    - Abriéndose vs Cerrándose: +21.0 puntos (IC no se solapan)
  
  - **Cobertura:** 1028/1175 pases (87.5%)
    - Exactos: 778 (75.7%) - objetivo por apellido en playDescription
    - Aproximados: 250 (24.3%) - objetivo por distancia al balón (respaldo)
  
  - **Constantes:**
    - ABIERTO_YD = 3.0
    - SEP_CERRADA_YD = 1.5 (actualizado)
    - TENDENCIA_UMBRAL_YD = 0.5
    - BOOTSTRAP_REPS = 1000, SEMILLA = 42

### Avisos para A:

🔔 **`vuelo.sigue_libre_por_jugada()` está REAL**
  - Ubicación: `backend/calculos/vuelo.py`
  - Firma: `sigue_libre_por_jugada(cuadros, plays, players, pff)`
  - Retorna: DataFrame con gameId, playId, valido, sigue_libre
  - Significado: sigue_libre = objetivo a ≥3 yd en pass_forward
  - Cobertura semana 1: 1028 jugadas (87.5% del total de pases)

### Pendiente:

- [ ] Tarea 2: Giro por cuadro (función real)
- [ ] Tarea 3: Giro principal por ruta (pasar prototipo a módulo)
- [ ] Tarea 4: Resumen de giros e H2
- [ ] Tarea 7: Mapas de calor
- [ ] Tarea 8: Cinta
- [ ] Tarea 9: Integración con A
- [ ] Tarea 10: Verificación final
