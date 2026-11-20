"""Endpoints de la persona B (ticker, giros, ventaja al lanzar, mapas)."""
from fastapi import APIRouter

from ..calculos import giros, mapas, ticker as calc_ticker, vuelo
from ..esquemas.comun import Capa, ErrorDetalle, Filtro, Modo, a_json
from ..esquemas.giro_aire import GirosResp, ItemTicker, MapaResp, VueloResp
from .dependencias import DEP_DATOS, RutaDetalle, valida_equipo

router = APIRouter(prefix="/api", route_class=RutaDetalle, responses={503: {"model": ErrorDetalle}})


@router.get("/ticker", response_model=list[ItemTicker], dependencies=DEP_DATOS)
def ticker(filtro: Filtro = "decisivo"):
    return a_json(calc_ticker.ticker(filtro))


@router.get("/giros/resumen", response_model=GirosResp, dependencies=DEP_DATOS)
def giros_resumen(filtro: Filtro = "decisivo"):
    return a_json(giros.resumen(filtro))


@router.get("/vuelo/resumen", response_model=VueloResp, dependencies=DEP_DATOS)
def vuelo_resumen(filtro: Filtro = "decisivo"):
    return a_json(vuelo.resumen(filtro))


@router.get("/mapa", response_model=MapaResp, dependencies=DEP_DATOS)
def mapa(capa: Capa, modo: Modo = "decisivo", equipo: str | None = None):
    valida_equipo(equipo)
    return a_json(mapas.mapa(capa, modo, equipo))
