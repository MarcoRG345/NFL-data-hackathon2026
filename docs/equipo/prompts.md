# Prompts para Kiro

Un chat nuevo por tarea grande. Modelo Auto; Sonnet solo si falla dos veces en lo mismo. Antes: `git pull`. Después: commit y `ESTADO.md`.

## Una sola vez, al instalar el kit

### Poner al día la steering vieja

```
Lee todos los archivos de .kiro/steering/. La pregunta oficial ahora es la de pregunta.md (la carrera de los dos relojes), y la arquitectura es la de stack-y-arquitectura.md.

Propón (sin editar todavía) cambios a proyecto.md, analisis-datos.md y diccionario-datos.md para que:
- no mencionen las preguntas de la práctica como objetivo;
- apunten a pregunta.md, contrato-api.md y stack-y-arquitectura.md;
- conserven lo que sigue sirviendo: normalización, línea de golpeo, nombres reales de columnas, comandos de Windows.

No toques rules.md, pregunta.md, equipo.md, stack-y-arquitectura.md ni contrato-api.md. Espera mi OK.
```

## Para cualquier tarea de un spec

### Ejecutar una tarea

```
Ejecuta SOLO la tarea [N] del spec [esqueleto | logica-carrera | dashboard-carrera | logica-giro-aire | dashboard-giro-aire]. Lee antes su requirements.md y design.md, y las skills que menciona.
Reglas: solo toca los archivos que equipo.md me asigna (o los compartidos si el spec es esqueleto); no instales nada; prueba con DATOS_SEMANAS=1; ejecuta lo que escribas con .venv\Scripts\python.exe o el build del dashboard.
Al terminar dime: archivos cambiados, comando que corriste y su salida, y qué falta. Marca la tarea como hecha y actualiza mi sección de ESTADO.md. No sigas con la siguiente.
```

### Construir una sección con la maqueta de referencia

Adjunta capturas de esa sección del lienzo de diseño.

```
Construye la sección [Resumen | P1 | P2 | P3 | Síntesis | Cómo leer esto] según la tarea [N] de mi spec, con la skill dashboard-dos-relojes. Te adjunto capturas de la maqueta: copia el diseño (layout, colores, tipografía, animaciones), no sus números. Usa los mocks de src/mocks y los tipos de types.ts. Solo React 18, Tailwind 3 y Recharts 3; nada de librerías nuevas. Al terminar corre el build y dime si hay errores.
```

### Conectar una sección a la API real

```
El backend de [mis endpoints] ya es real en main. Apaga el mock de [endpoint] en api.ts y revisa la sección [nombre] contra la API (backend en el puerto 8000; el proxy de Vite ya existe). Si algún campo no coincide con types.ts, NO lo arregles en el frontend: dime qué campo falla y en qué endpoint. Deja el mock en el repo como respaldo.
```

### Avisar a la otra persona

```
Actualiza mi sección de ESTADO.md: la función [nombre] ya es real (no datos de mentira). Escribe qué devuelve, con un ejemplo de 2 filas, y desde qué commit.
```

### Revisión cruzada (fase 5)

```
Revisa los resultados de mi compañera en scratch/resultados-[carrera | giro-aire].md sin cambiar su código. Para cada número principal dime: si el n es suficiente, si el intervalo es razonable, si algo parece un error de definición según pregunta.md, y una prueba rápida que lo confirmaría. Escribe tus notas en ESTADO.md, sección "Revisión cruzada".
```

## Emergencias

**Atorado (más de 15 minutos o 2 fallos):**
```
Para. Dime en 3 líneas qué falla y propón la versión más simple que funcione en 10 minutos, aunque se vea menos bonita (ver "Si algo tarda" en la skill correspondiente). No escribas nada hasta mi OK.
```

**El build falla:**
```
El build falla con este error: [pegar]. Arregla solo ese error, sin cambiar dependencias ni configuración. Si está en un componente no esencial, propón desactivarlo temporalmente.
```

**La carga es lenta o se queda sin memoria:**
```
La carga con [N] semanas tarda [X] o falla con [error]. Mide cuánto pesa cada tabla en memoria y propón cómo bajarlo sin cambiar resultados (menos columnas, tipos más chicos, descartar cuadros que no usa ninguna tabla base). Si no hay tiempo, propón cuántas semanas usar y qué texto agregar en "Cómo leer esto".
```

**`--check` en rojo:**
```
--check falla con esto: [pegar]. Explícame en una línea qué regla de rules.md se rompe y arregla solo eso. No instales nada.
```

**Conflicto de Git:** lo resuelve la dueña del archivo, a mano, nunca Kiro. Si es un archivo compartido, se resuelve juntas.
