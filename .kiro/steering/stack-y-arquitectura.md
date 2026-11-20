---
inclusion: always
---

# Stack y arquitectura del proyecto

`rules.md` (de los organizadores) manda sobre este archivo. Aquí solo se aterriza qué usamos de ese stack y dónde va cada cosa.

## Tecnología permitida y para qué la usamos

| Capa | Tecnología (versión fija) | Uso en el proyecto |
|---|---|---|
| Datos | Python 3.12, pandas 2.2.3, numpy 2.1.3 | Carga, normalización, tablas derivadas, bootstrap |
| API | FastAPI 0.115.14, Uvicorn 0.34.3, Pydantic 2.11.7 | Endpoints bajo `api/`, modelos de respuesta |
| Frontend | React 18.3.1, TypeScript 5.7.3, Vite 5.4.21 | Una sola página con menú lateral (sin router) |
| Estilos | Tailwind 3.4.19 (sintaxis v3) | Tema oscuro, tarjetas, animaciones CSS |
| Gráficas | Recharts 3.10.1 | Líneas, barras, dispersión, áreas de referencia |
| Cancha, mapas, trayectorias | SVG y `div` hechos a mano | Sin librerías extra |
| Pruebas (opcional) | pytest, httpx | Verificación de endpoints |

**Prohibido** (aunque el prototipo de Lovable lo use): React 19, Tailwind 4, TanStack, react-router, Radix/shadcn, lucide-react, framer-motion, plotly, d3, cualquier `npm install` o `pip install`. Íconos = SVG en línea. Animaciones = CSS + animaciones de Recharts + un hook propio con `requestAnimationFrame`.

## Arquitectura

```
backend/
  main.py              app FastAPI, /health, carga en segundo plano, incluye los 2 routers
  config.py            constantes comunes
  columnas.py          nombres reales de columnas
  normalizacion.py     giro 180°, línea de golpeo (de la práctica)
  data_loader.py       carga y recorte; construye las tablas base
  base/                (esqueleto) separacion.py, presion.py, objetivo.py, situacion.py
  calculos/            A: relojes.py, sintesis.py, ejemplos.py | B: giros.py, vuelo.py, mapas.py, ticker.py
  esquemas/            comun.py (esqueleto) | carrera.py (A) | giro_aire.py (B)  ← modelos Pydantic
  routers/             carrera.py (A) | giro_aire.py (B)
dashboard/src/
  main.tsx, App.tsx    layout: Ticker + Sidebar + Encabezado + sección activa
  index.css            directivas Tailwind, keyframes (cinta, pulso, aparece), fuentes
  types.ts             tipos del contrato (espejo de esquemas/)
  api.ts               fetch('api/...') con interruptor de mocks por endpoint
  mocks/               un JSON por endpoint
  estado/              contexto global: sección, vista, filtro, equipo
  hooks/               useApi (carga, 503, reintento), useTween (animación 0→1)
  lib/                 colores.ts (paleta y escala de calor), formato.ts
  componentes/         comunes (esqueleto) + CanchaJugada, Embudo, Cuadrante (A) + MapaCalor, Trayectorias (B)
  layout/              Ticker (B), Sidebar y Encabezado (esqueleto)
  secciones/           Resumen, P1DosRelojes, Sintesis (A) | P2Giro, P3Aire, ComoLeer (B)
```

## Flujo de datos

1. Al arrancar, `main.py` lanza la carga en un hilo. `api/estado-datos` dice si terminó.
2. `data_loader.py` lee cada semana, normaliza, recorta a los jugadores y cuadros necesarios y arma las tablas base: `jugadas` (una fila por jugada), `cuadros` (posiciones recortadas), `sep_cuadros` (separación por receptor y cuadro), `presion` (t_presion por jugada), `objetivo` (receptor objetivo por jugada).
3. Cada módulo de `calculos/` construye sus resultados una vez, en memoria, al final de la carga. Los endpoints solo leen y filtran.
4. Nada se escribe a disco desde la app. `scratch/` es solo para scripts de análisis.
5. El frontend pide cada sección al entrar en ella; mientras carga muestra un esqueleto; con 503 reintenta cada 3 s.

## Convenciones

- Rutas del frontend siempre `fetch('api/...')`, sin diagonal inicial.
- Cada respuesta trae `n` y el `filtro` usado.
- Nombres en español, sin acentos en identificadores (`separacion`, `conversion`).
- Windows: `.venv\Scripts\python.exe`; build del dashboard con el script de la plantilla.
- Primero con 1 semana (`DATOS_SEMANAS=1`); las 8 solo al final.
