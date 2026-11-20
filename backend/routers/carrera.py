"""Endpoints de la persona A (carrera, síntesis, cancha) + api/estado-datos (esqueleto).
Decisión: api/estado-datos vive aquí (un router menos que registrar); no usa la dependencia de 503."""
from fastapi import APIRouter

from ..calculos import ejemplos, relojes, sintesis
from ..esquemas.carrera import (
    CurvasResp, DistanciaResp, EjemploJugada, EquiposResp, JugadaResp, ResultadoResp, ResumenResp,
)
from ..esquemas.comun import ErrorDetalle, EstadoDatos, Filtro, Vista, a_json
from ..estado import estado
from .dependencias import DEP_DATOS, RutaDetalle, valida_equipo

router = APIRouter(prefix="/api", route_class=RutaDetalle, responses={503: {"model": ErrorDetalle}})


@router.get("/estado-datos", response_model=EstadoDatos)
def estado_datos():
    return EstadoDatos(listo=estado.listo, cargando=estado.cargando, error=estado.error,
                       semanas=estado.semanas, n_jugadas=estado.n_jugadas)


@router.get("/resumen", response_model=ResumenResp, dependencies=DEP_DATOS)
def resumen(filtro: Filtro = "decisivo", vista: Vista = "ofe", equipo: str | None = None):
    valida_equipo(equipo)
    return a_json(sintesis.resumen(filtro, vista, equipo))


@router.get("/carrera/curvas", response_model=CurvasResp, dependencies=DEP_DATOS)
def curvas(filtro: Filtro = "decisivo"):
    return a_json(relojes.curvas(filtro))


@router.get("/carrera/distancia", response_model=DistanciaResp, dependencies=DEP_DATOS)
def distancia(filtro: Filtro = "decisivo"):
    return a_json(relojes.distancia(filtro))


@router.get("/carrera/resultado", response_model=ResultadoResp, dependencies=DEP_DATOS)
def resultado(filtro: Filtro = "decisivo"):
    return a_json(relojes.resultado(filtro))


@router.get("/equipos", response_model=EquiposResp, dependencies=DEP_DATOS)
def equipos(filtro: Filtro = "decisivo", vista: Vista = "ofe"):
    return a_json(sintesis.equipos(filtro, vista))


@router.get("/jugadas-ejemplo", response_model=list[EjemploJugada], dependencies=DEP_DATOS)
def jugadas_ejemplo():
    return a_json(ejemplos.jugadas_ejemplo())


@router.get("/jugada", response_model=JugadaResp, dependencies=DEP_DATOS)
def jugada(gameId: int, playId: int):
    return a_json(ejemplos.jugada(gameId, playId))
