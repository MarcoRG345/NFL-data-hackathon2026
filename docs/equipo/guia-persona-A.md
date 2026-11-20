# Guía de la Persona A · La carrera y la cancha

**Tu parte:** P1 (¿quién gana la carrera y cuánto vale?), la síntesis por equipo y la cancha interactiva. Haces backend y dashboard de tu parte.
**Tu rama:** `a-carrera`
**Tus specs:** `.kiro/specs/logica-carrera/` (backend, 11 tareas) y `.kiro/specs/dashboard-carrera/` (frontend, 7 tareas)
**Tus skills:** `logica-carrera`, `calculo-carrera`, `backend-api-datos`, `estadistica-intervalos`, `cancha-y-jugadores`, `dashboard-dos-relojes`
**Tu verificación:** `scratch/verifica_carrera.py`

## Tus archivos

| Backend | Dashboard |
|---|---|
| `calculos/relojes.py`, `sintesis.py`, `ejemplos.py` | `secciones/Resumen.tsx`, `P1DosRelojes.tsx`, `Sintesis.tsx` |
| `esquemas/carrera.py`, `routers/carrera.py` | `componentes/CanchaJugada.tsx`, `Cuadrante.tsx`, `Embudo.tsx` |
| `scratch/prueba_carrera.py`, `verifica_carrera.py`, `resultados-carrera.md` | Los mocks de tus endpoints |

## Conexiones con B

| Recibes de B | Para | Mientras tanto |
|---|---|---|
| `giros.giro_por_cuadro(cuadros)` | La flecha curva en la cancha | Sale "sin giro": la cancha funciona igual |
| `vuelo.sigue_libre_por_jugada()` | El paso P3 de la cadena | P3 = mediana de la liga para todos |

| Le das a B | Para | Avisa en `ESTADO.md` |
|---|---|---|
| `relojes.resultado_por_jugada()` | La cinta de jugadas clave | Al terminar la tarea 3 de `logica-carrera` |

## Orden recomendado (alternando backend y frontend)

| # | Fase | Spec · tarea | Qué sale |
|---|---|---|---|
| 1 | 2. Datos | logica-carrera · 1 | Prueba de vida → GO / NO-GO con B |
| 2 | Esqueleto | esqueleto · 1–9 (juntas) | Etiqueta `esqueleto` |
| 3 | 3. Preparación | logica-carrera · 2 y 3 | Relojes por jugada; función para B |
| 4 | 3. Preparación | dashboard-carrera · 1 y 2 | Cancha completa con el mock |
| — | | **Merge 1** | |
| 5 | 4. Modelado | logica-carrera · 4 y 5 | Curvas, resultado, distancia, H1 |
| 6 | 4. Modelado | dashboard-carrera · 3 y 4 | Resumen y P1 con mocks |
| 7 | 4. Modelado | logica-carrera · 6 y 7 | Cadena por equipo, resumen, insight |
| 8 | 4. Modelado | dashboard-carrera · 5 | Síntesis con mocks |
| 9 | 4. Modelado | logica-carrera · 8 y 9 | Jugadas ejemplo y `api/jugada` real |
| — | | **Merge 2: app completa** | |
| 10 | 5. Evaluación | logica-carrera · 10; dashboard-carrera · 6 | Integración con B; estados y accesibilidad; revisión cruzada |
| 11 | 6. Despliegue | dashboard-carrera · 7; logica-carrera · 11 | Conexión a la API; verificación con 8 semanas |

## Cómo arrancar cada sesión

1. `git pull` de `main` hacia `a-carrera`.
2. Chat nuevo de Kiro (modelo Auto) y el prompt "Ejecutar una tarea" de `prompts.md`, con el spec y el número.
3. Para frontend, adjunta capturas de la maqueta (prompt "Construir una sección").
4. Al terminar: revisar la salida, commit y tu sección de `ESTADO.md`.

## Checklist de calidad

- [ ] Los 5 casos sintéticos de relojes pasan.
- [ ] Las curvas son no decrecientes y el reparto de resultados suma 100.
- [ ] H1 con intervalo y tabla de robustez en `resultados-carrera.md`.
- [ ] En `api/jugada`, la separación coincide con la distancia receptor ↔ defensor.
- [ ] La flecha de un receptor que avanza apunta a la derecha; los relojes se congelan en su evento.
- [ ] Tocar un equipo cambia cuadrante, embudo y tabla a la vez.
- [ ] Ningún `NaN` en el JSON; cada endpoint < 300 ms con 8 semanas.
- [ ] Ningún número escrito a mano en el dashboard.

## Errores de la práctica que no hay que repetir

- Línea de golpeo del cuadro del snap: usa la de `normalizacion.py`.
- Kiro instaló `requests`: usa `urllib`.
- Kiro siguió sin esperar el OK: cancela y recuérdale `equipo.md`.
- Resultados perdidos al llenarse el chat: pide siempre "dime qué archivos escribiste".
