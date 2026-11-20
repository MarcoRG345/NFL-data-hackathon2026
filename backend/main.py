"""App FastAPI. Desarrollo: .venv/bin/uvicorn backend.main:app --reload (Windows: .venv\\Scripts\\uvicorn)."""
import os
from pathlib import Path


def cargar_env():
    f = Path(__file__).resolve().parent.parent / ".env"
    if f.exists():
        for linea in f.read_text(encoding="utf-8-sig").splitlines():
            linea = linea.strip()
            if linea and not linea.startswith("#") and "=" in linea:
                k, v = linea.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


cargar_env()

import threading  # noqa: E402
import time  # noqa: E402
from contextlib import asynccontextmanager  # noqa: E402

from fastapi import FastAPI  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

from backend.estado import estado  # noqa: E402
from backend.routers import carrera, giro_aire  # noqa: E402

DIST = Path(__file__).resolve().parent.parent / "dashboard" / "dist"


def _construir_tablas_base(datos: dict) -> None:
    """Construye jugadas, sep_cuadros, presion y objetivo dentro de `estado.tablas`."""
    from backend.base import construir_tablas_base

    construir_tablas_base(datos)


def _cargar_en_segundo_plano() -> None:
    from backend.data_loader import cargar_datos_base

    estado.cargando, estado.listo, estado.error = True, False, None
    t0 = time.time()
    try:
        datos = cargar_datos_base()
        for nombre in ("games", "plays", "players", "scouting", "cuadros", "eventos"):
            estado.tablas[nombre] = datos[nombre]
        estado.resultados["carga"] = {"excluidas": datos["excluidas"], "segundos": round(time.time() - t0, 1)}
        _construir_tablas_base(estado.tablas)  # tarea 3: jugadas, sep_cuadros, presion, objetivo
        games = datos["games"]
        estado.semanas = int(games.loc[games["gameId"].isin(datos["eventos"]["gameId"]), "week"].nunique())
        estado.n_jugadas = int(len(datos["eventos"]))
        estado.listo = True
    except Exception as e:  # la app no se cae: el error se muestra en api/estado-datos
        estado.error = f"{type(e).__name__}: {e}"
        print(f"[carga] ERROR {estado.error}")
    finally:
        estado.cargando = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    threading.Thread(target=_cargar_en_segundo_plano, daemon=True, name="carga").start()
    yield


app = FastAPI(title="Hackathon NFL UNAM", lifespan=lifespan)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


app.include_router(carrera.router)
app.include_router(giro_aire.router)

# El build del dashboard se sirve al final para no tapar /health ni /api.
if DIST.is_dir():
    app.mount("/", StaticFiles(directory=DIST, html=True), name="dashboard")
