# Guía de la Persona B · El giro, el aire y los mapas

**Tu parte:** P2 (¿cómo se libera el receptor?), P3 (¿la ventaja sobrevive en el aire?), los mapas de calor, las trayectorias del balón, la cinta de jugadas clave y "Cómo leer esto". Haces backend y dashboard de tu parte.
**Tu rama:** `b-giro-aire`
**Tus specs:** `.kiro/specs/logica-giro-aire/` (backend, 10 tareas) y `.kiro/specs/dashboard-giro-aire/` (frontend, 7 tareas)
**Tus skills:** `logica-giro-aire`, `calculo-carrera`, `backend-api-datos`, `estadistica-intervalos`, `mapas-de-calor`, `dashboard-dos-relojes`
**Tu verificación:** `scratch/verifica_giro_aire.py`

## Tus archivos

| Backend | Dashboard |
|---|---|
| `calculos/giros.py`, `vuelo.py`, `mapas.py`, `ticker.py` | `secciones/P2Giro.tsx`, `P3Aire.tsx`, `ComoLeer.tsx` |
| `esquemas/giro_aire.py`, `routers/giro_aire.py` | `componentes/MapaCalor.tsx`, `Trayectorias.tsx`; `layout/Ticker.tsx` |
| `scratch/prueba_giro_aire.py`, `verifica_giro_aire.py`, `resultados-giro-aire.md` | Los mocks de tus endpoints |

## Conexiones con A

| Le das a A | Para | Avisa en `ESTADO.md` |
|---|---|---|
| `giros.giro_por_cuadro(cuadros)` | La flecha curva de la cancha | Al terminar la tarea 2 de `logica-giro-aire` |
| `vuelo.sigue_libre_por_jugada()` | El paso P3 de la cadena | Al terminar la tarea 5 |

| Recibes de A | Para | Mientras tanto |
|---|---|---|
| `relojes.resultado_por_jugada()` | La cinta (tipos receptor, defensa y sin presión) | La cinta usa solo giro y aire |

La matriz de giros no depende de A: `gana_ruta` se calcula con la base.

## Orden recomendado (alternando backend y frontend)

| # | Fase | Spec · tarea | Qué sale |
|---|---|---|---|
| 1 | 2. Datos | logica-giro-aire · 1 | Prueba de vida → GO / NO-GO con A |
| 2 | Esqueleto | esqueleto · 1–9 (juntas) | Etiqueta `esqueleto` |
| 3 | 3. Preparación | logica-giro-aire · 2 y 3 | Giro por cuadro (aviso a A) y giro principal |
| 4 | 3. Preparación | dashboard-giro-aire · 1 | MapaCalor con el mock |
| — | | **Merge 1** | |
| 5 | 4. Modelado | logica-giro-aire · 4 | Resumen de giros, H2 |
| 6 | 4. Modelado | dashboard-giro-aire · 2 | Sección P2 con mocks |
| 7 | 4. Modelado | logica-giro-aire · 5 y 6 | Vuelo (aviso a A), H3 |
| 8 | 4. Modelado | dashboard-giro-aire · 3 y 4 | Trayectorias y sección P3 con mocks |
| 9 | 4. Modelado | logica-giro-aire · 7 y 8 | Mapas y cinta reales |
| 10 | 4. Modelado | dashboard-giro-aire · 5 | Cinta y Cómo leer esto |
| — | | **Merge 2: app completa** | |
| 11 | 5. Evaluación | logica-giro-aire · 9; dashboard-giro-aire · 6 | Integración con A; estados y accesibilidad; revisión cruzada |
| 12 | 6. Despliegue | dashboard-giro-aire · 7; logica-giro-aire · 10 | Conexión a la API; verificación con 8 semanas |

## Cómo arrancar cada sesión

1. `git pull` de `main` hacia `b-giro-aire`.
2. Chat nuevo de Kiro (modelo Auto) y el prompt "Ejecutar una tarea" de `prompts.md`, con el spec y el número.
3. Para frontend, adjunta capturas de la maqueta (prompt "Construir una sección").
4. Al terminar: revisar la salida, commit y tu sección de `ESTADO.md`.

## Checklist de calidad

- [ ] Los 3 casos sintéticos de giro pasan (incluido 350° → 10° = +20°).
- [ ] Menos del 70% de rutas con giro brusco (o el aviso de ruido está escrito).
- [ ] H2 y H3 con intervalo y robustez en `resultados-giro-aire.md`.
- [ ] Mapas de azul a rojo con leyenda y n; celdas con n < 5 fuera.
- [ ] Cada balón de las trayectorias tarda más cuanto más profundo es el pase.
- [ ] La cinta se desplaza sin salto y se detiene con movimiento reducido.
- [ ] En la cancha de A aparece la flecha curva cuando un receptor gira.
- [ ] Ningún `NaN` en el JSON; cada endpoint < 300 ms con 8 semanas.

## Cuidado especial con los giros

- `dir` salta cuando el jugador va lento: exige velocidad mínima antes y después.
- Envuelve las diferencias de ángulo antes de comparar.
- Positivo = giro a la derecha: A lo usa para el lado del arco en la cancha.
