# Tareas · Lógica del backend del giro y el aire (Persona B)

Rama `b-giro-aire`. Una tarea a la vez, con `DATOS_SEMANAS=1` salvo que diga otra cosa. Al terminar cada una: archivos cambiados, comando y salida; actualizar la sección B de `ESTADO.md`.

- [ ] 1. Prueba de vida del receptor (fase 2, antes del esqueleto)
  - Script `scratch/prueba_giro_aire.py`: % de pases con `pass_arrived`, separación en el snap (colchón), % de rutas con giro suave y brusco, ruido de `dir` a baja velocidad, coincidencia del objetivo con `playDescription` (20 al azar)
  - Guardar en `scratch/resultados-giro-aire.md`; decidir GO / NO-GO con A
  - _Requisitos: 2.2, 8.2_

- [ ] 2. Giro por cuadro
  - `giros.giro_por_cuadro(cuadros)` vectorizado; los 3 casos sintéticos en `scratch/verifica_giro_aire.py`
  - Avisar a A en `ESTADO.md` (función real, columnas, commit)
  - _Requisitos: 1.1, 1.2, 1.3, 1.4_

- [ ] 3. Giro principal por ruta
  - `giros.construir`: RUTAS con tipo, franja, separación ganada, velocidad conservada, `gana_ruta`, posición; conteo de excluidas; aviso de ruido
  - Imprimir 3 rutas reales cuadro por cuadro y revisarlas
  - _Requisitos: 2.1, 2.2, 2.3_

- [ ] 4. Resumen de giros e H2
  - `giros.resumen(filtro)` con bootstrap por ruta y matriz 6 × 5; `null` con n < 20; insight
  - H2 y robustez (umbral brusco 45/60/90, ventana 0.3/0.5/0.7) en `resultados-giro-aire.md`
  - Endpoint `api/giros/resumen` real
  - _Requisitos: 3.1, 3.2, 3.3_

- [ ] 5. El balón en el aire
  - `vuelo.construir`: PASES; `sigue_libre_por_jugada()` real y aviso a A
  - _Requisitos: 4.1, 4.3_

- [ ] 6. Resumen de vuelo e H3
  - `vuelo.resumen(filtro)` con `por_franja`, `trayectorias` (5 profundidades) e insight; H3 y robustez
  - Endpoint `api/vuelo/resumen` real
  - _Requisitos: 4.2, 4.4_

- [ ] 7. Mapas de calor
  - `mapas.construir` (liga: 2 capas × 2 modos) y `celdas` por equipo con caché
  - Endpoint `api/mapa` real; prueba de n ≥ 5 y `valor_norm` en [0, 1]
  - _Requisitos: 5.1, 5.2_

- [ ] 8. Cinta
  - `ticker.construir` con los 5 tipos (solo giro y aire mientras A no tenga `resultado_por_jugada` real)
  - Endpoint `api/ticker` real
  - _Requisitos: 6.1, 6.2_

- [ ] 9. Integración con A
  - Cuando A avise que `resultado_por_jugada` es real: reconstruir la cinta con los 5 tipos
  - Revisar en `api/jugada` de A que `girando` aparece en el receptor durante su giro
  - _Requisitos: 1.4, 6.1_

- [ ] 10. Verificación final del backend de B
  - `scratch/verifica_giro_aire.py` completo con las 8 semanas: casos sintéticos, forma, números, tiempo < 300 ms
  - _Requisitos: 7.1, 7.2, 7.3, 7.4, 8.1, 8.2_
