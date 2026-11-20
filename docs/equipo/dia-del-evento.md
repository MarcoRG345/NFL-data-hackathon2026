# El día del evento (3 horas, sin pitch)

La app llega terminada. Las 3 horas son para correrla con los datos oficiales, verificar y enviar.

## Antes de entrar

- [ ] Las dos computadoras con el repo en `main` actualizado y la etiqueta `app-completa` de la práctica.
- [ ] Los CSV de práctica en una USB (por si los oficiales tardan).
- [ ] Al menos 15 créditos de Kiro por cuenta.
- [ ] Este archivo y `prompts.md` abiertos.

## Cronograma

| Hora | A | B | Juntas |
|---|---|---|---|
| 0:00–0:20 | Copiar CSV a `data/`, levantar backend con 1 semana, prompt "Perfil rápido" | Levantar dashboard, revisar que todas las secciones cargan | **0:20 decidir:** ¿mismos datos que en la práctica? |
| 0:20–1:20 | Recalcular su parte con las 8 semanas; comparar con `resultados-carrera.md` | Recalcular su parte; comparar con `resultados-giro-aire.md` | Si cambiaron columnas: prompt "Adaptar columnas" (A) |
| **1:20** | | | **App completa con datos oficiales**: merge y etiqueta `evento-completa` |
| 1:20–2:20 | Revisa los números de B; ajusta los textos de sus secciones | Revisa los números de A; ajusta los textos de sus secciones | 1:50 merge de ajustes |
| **2:20** | | | **Congelar**: nada nuevo |
| 2:20–2:45 | Prompt "Verificación final" | Prueba manual de cada sección y filtro | |
| 2:45–3:00 | | | `.hackathon\setup.cmd --entregar` desde una sola computadora y enviar |

Si a la 1:20 algo no está completo, se recorta (ver "Si algo tarda" en cada skill). Si a las 2:40 `--check` falla, se envía la etiqueta `evento-completa`.

## Prompts del día

**Perfil rápido (A, 0:05):**
```
Copié los CSV del evento en data/. Sin cambiar archivos, revisa con la skill exploracion-datos-grandes: qué archivos y semanas hay, si las columnas de columnas.py existen con el mismo nombre, si están los eventos ball_snap, pass_forward y pass_arrived y los roles Pass Route, Coverage y Pass Rush, y si el número de jugadas y partidos coincide con scratch/perfil-datos.md. Solo repórtame.
```

**Adaptar columnas (A, solo si cambiaron):**
```
Según el perfil cambiaron estas columnas: [lista]. Adáptalas SOLO en backend/columnas.py y config.py. No cambies la lógica. Corre scratch/verifica_esqueleto.py con 1 semana y muéstrame la salida.
```

**Recalcular y comparar (cada una):**
```
Con los datos del evento y las 8 semanas, corre scratch/verifica_[carrera | giro_aire].py y compara con scratch/resultados-[carrera | giro-aire].md. Dime qué números cambiaron más de 2 puntos y si las jugadas ejemplo siguen existiendo. Guarda la versión nueva como scratch/resultados-evento-[A | B].md.
```

**Verificación final (2:20):**
```
Sin cambiar código: 1) corre .hackathon\setup.cmd --check y muéstrame la salida; 2) corre el build del dashboard; 3) con el backend levantado SIN .env, llama a /health y a cada endpoint del contrato con urllib y dime cuáles responden 200; 4) busca fetch('/api', localhost o 127.0.0.1 en dashboard/src; 5) busca escrituras a disco (open con "w", to_csv, to_parquet) fuera de scratch/. Solo repórtame.
```
