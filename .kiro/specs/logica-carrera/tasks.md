# Tareas · Lógica del backend de la carrera (Persona A)

Rama `a-carrera`. Una tarea a la vez, con `DATOS_SEMANAS=1` salvo que diga otra cosa. Al terminar cada una: archivos cambiados, comando y salida; actualizar la sección A de `ESTADO.md`.

- [ ] 1. Prueba de vida de la presión (fase 2, antes del esqueleto)
  - Script `scratch/prueba_carrera.py` reutilizando la llegada de presión de la práctica: % de jugadas con presión, mediana de `t_presion`, coincidencia con PFF, jugadas decisivas por equipo, conversión de 3.º/4.º según quién gana (con `ABIERTO_YD` 3.0 desde 1.0 s), con n
  - Guardar en `scratch/resultados-carrera.md`; decidir GO / NO-GO con B
  - _Requisitos: 1.1, 4.3_

- [ ] 2. Relojes por jugada
  - `relojes.construir`: `t_libre`, `primer_libre_id`, resultado, margen, `sack_con_libre`
  - Escribir los 5 casos sintéticos en `scratch/verifica_carrera.py` y pasarlos
  - Imprimir 3 jugadas reales cuadro por cuadro y revisarlas a mano
  - _Requisitos: 1.1, 1.2, 1.3, 1.4_

- [ ] 3. Función para B y aviso
  - `resultado_por_jugada()` real; anotar en `ESTADO.md` columnas y commit
  - _Requisitos: 1.5_

- [ ] 4. Curvas y resultado
  - `curvas(filtro)` y `resultado(filtro)` precalculados para los 5 filtros; pruebas de no decreciente y suma 100
  - Endpoints `api/carrera/curvas` y `api/carrera/resultado` reales
  - _Requisitos: 2.1, 2.2, 3.1, 8.1, 8.2_

- [ ] 5. Distancia, H1 y robustez
  - `distancia(filtro)` con bootstrap vectorizado (skill `estadistica-intervalos`); grupos según filtro; `null` con n < 20
  - H1 con bootstrap de la diferencia; tabla de robustez (radios, umbral de libre, solo Man) en `resultados-carrera.md`
  - Endpoint `api/carrera/distancia` real
  - _Requisitos: 4.1, 4.2, 4.3_

- [ ] 6. Cadena por equipo
  - `sintesis.construir`: pasos P2, P1, P3 (con `vuelo.sigue_libre_por_jugada()`, aunque aún sea de mentira), conversión final, tasas, cadena, medianas, eslabón, cuadrante; regla de n < 30
  - Endpoint `api/equipos` real; revisar 3 equipos a mano
  - _Requisitos: 5.1, 5.2, 5.3_

- [ ] 7. Resumen e insight
  - `sintesis.resumen` con KPIs, cadena de la liga e insight por vista; caché por equipo; 404 de equipo
  - Endpoint `api/resumen` real
  - _Requisitos: 6.1, 6.2_

- [ ] 8. Jugadas ejemplo
  - `ejemplos.construir` con los criterios de la skill; `cargar_cuadros_completos(ids)` releyendo solo esas semanas
  - Endpoint `api/jugadas-ejemplo` real
  - _Requisitos: 7.1, 7.2_

- [ ] 9. Cuadros del replay
  - Roles, separación contra el `defensor`, balón real con altura, relojes, eventos, contexto; `giros.giro_por_cuadro` aunque aún sea de mentira
  - Endpoint `api/jugada` real; prueba "separación = distancia receptor ↔ defensor"
  - Exportar la primera jugada a `dashboard/src/mocks/` para reemplazar el mock (avisar a quien tenga el dashboard abierto)
  - _Requisitos: 7.3, 7.4_

- [ ] 10. Integración con B
  - Cuando B avise: confirmar que `giro_por_cuadro` marca giros en las jugadas ejemplo y que P3 ya no es la mediana para todos; reconstruir y revisar 3 equipos
  - _Requisitos: 5.2, 7.3_

- [ ] 11. Verificación final del backend de A
  - `scratch/verifica_carrera.py` completo con las 8 semanas: casos sintéticos, forma, números, tiempo < 300 ms
  - _Requisitos: 8.3, 8.4, 9.1, 9.2_
