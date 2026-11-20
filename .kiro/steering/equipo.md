---
inclusion: always
---

# Trabajo en equipo (2 personas, cada una con su Kiro)

Cada persona es dueña de una parte completa, del cálculo a la pantalla. Antes de crear o cambiar un archivo, revisa esta tabla. Si no es de la persona con la que trabajas, **no lo toques**: dime qué cambio haría falta.

## Quién es dueña de qué

| Archivos | Dueña |
|---|---|
| `backend/calculos/relojes.py`, `sintesis.py`, `ejemplos.py`; `backend/esquemas/carrera.py`; `backend/routers/carrera.py` | A |
| `dashboard/src/secciones/Resumen.tsx`, `P1DosRelojes.tsx`, `Sintesis.tsx`; `componentes/CanchaJugada.tsx`, `Embudo.tsx`, `Cuadrante.tsx` | A |
| `.kiro/specs/logica-carrera/`, `.kiro/specs/dashboard-carrera/`, `scratch/prueba_carrera.py`, `scratch/verifica_carrera.py`, `scratch/resultados-carrera.md`, los mocks de sus endpoints | A |
| `backend/calculos/giros.py`, `vuelo.py`, `mapas.py`, `ticker.py`; `backend/esquemas/giro_aire.py`; `backend/routers/giro_aire.py` | B |
| `dashboard/src/secciones/P2Giro.tsx`, `P3Aire.tsx`, `ComoLeer.tsx`; `componentes/MapaCalor.tsx`, `Trayectorias.tsx`; `layout/Ticker.tsx` | B |
| `.kiro/specs/logica-giro-aire/`, `.kiro/specs/dashboard-giro-aire/`, `scratch/prueba_giro_aire.py`, `scratch/verifica_giro_aire.py`, `scratch/resultados-giro-aire.md`, los mocks de sus endpoints | B |
| **Compartidos** (se hacen juntas en el esqueleto y luego solo con PR revisado): `backend/main.py`, `config.py`, `data_loader.py`, `backend/base/`, `backend/esquemas/comun.py`, `dashboard/src/App.tsx`, `index.css`, `types.ts`, `api.ts`, `estado/`, `hooks/`, `lib/`, `layout/Sidebar.tsx`, `layout/Encabezado.tsx`, componentes comunes, `.kiro/steering/`, `.kiro/skills/` | Las dos |
| **Nadie**: `.hackathon/`, `.kiro/steering/rules.md`, `package.json`, `package-lock.json`, `vite.config.ts`, `postcss.config.js`, `tsconfig.json`, `.env.example`, `setup-log.txt`, `data/` | — |

`tailwind.config.js` e `index.html` solo se tocan en el esqueleto (tema de colores y fuentes) y luego quedan congelados.

## Cuando necesitas algo de la otra parte

- Usa la función del contrato (`contrato-api.md`, "Conexiones internas"). Si aún devuelve datos de mentira, sigue trabajando con eso.
- Nunca copies ni reescribas el código de la otra persona en tus archivos.

## Git: lo que Kiro NO hace

- No ejecutes `git push`, `pull`, `merge`, `checkout`, `rebase`, `reset` ni `stash`. Puedes sugerir un mensaje de commit.
- Ramas: `main` (solo en puntos de control), `a-carrera`, `b-giro-aire`.
- Nunca van a Git: `data/*.csv`, `.env`, `.venv/`, `node_modules/`, `dashboard/dist/`, `scratch/`.

## Instalaciones: prohibidas

No instales nada (`pip`, `uv add`, `npm install`). Si algo parece necesitar una librería, detente y propón cómo hacerlo con el stack (`stack-y-arquitectura.md`). Para HTTP en scripts usa `urllib`.

## Comandos en Windows

- Python: `.venv\Scripts\python.exe` · uv: `.hackathon\.tools\uv\uv.exe` · verificación: `.hackathon\setup.cmd --check`.

## Forma de trabajar

- Una tarea del spec a la vez. Al terminar: archivos cambiados, comando corrido y su salida.
- Ejecuta antes de decir que funciona. Si falla, muestra el error tal cual.
- Más de 15 minutos o 2 fallos en lo mismo: detente y propón una versión más simple.
- Pruebas con 1 semana. La app no escribe a disco y funciona sin `.env`.
- Al terminar cada tarea, actualiza tu sección de `ESTADO.md`.
