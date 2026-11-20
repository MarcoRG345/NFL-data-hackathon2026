"""Modelos de respuesta de la persona B (giro, ventaja al lanzar, mapas, ticker). Campo por campo con contrato-api.md."""
from typing import Literal

from pydantic import BaseModel

from .comun import Capa, Filtro, Intervalo, Modo


# --- api/ticker (la respuesta es list[ItemTicker]) ---
class ItemTicker(BaseModel):
    texto: str
    tipo: Literal["receptor", "defensa", "sin_presion", "giro", "aire"]


# --- api/giros/resumen ---
class GiroPorTipo(BaseModel):
    franja: Literal["corta", "media", "larga"]
    tipo: Literal["sin_giro", "suave", "brusco"]
    n: int
    sep_ganada: float | None
    ic: Intervalo | None


class CeldaMatriz(BaseModel):
    angulo_bin: int  # 0–5
    vel_bin: int     # 0–4 (0 = conserva más)
    n: int
    pct_gana_carrera: float | None


class GirosResp(BaseModel):
    filtro: Filtro
    n: int
    por_tipo: list[GiroPorTipo]
    matriz: list[CeldaMatriz]
    insight: str


# --- api/vuelo/resumen ---
class VueloPorSeparacion(BaseModel):
    franja: Literal["cerrado", "disputado", "abierto"]
    n: int
    pct_completo: float | None
    ic: Intervalo | None  # null si n < 20


class VueloPorTendencia(BaseModel):
    tendencia: Literal["cerrandose", "estable", "abriendose"]
    n: int
    pct_completo: float | None
    ic: Intervalo | None  # null si n < 20


class VueloResp(BaseModel):
    filtro: Filtro
    n: int
    n_aproximado: int
    por_separacion: list[VueloPorSeparacion]
    por_tendencia: list[VueloPorTendencia]
    insight: str


# --- api/mapa ---
class CeldaMapa(BaseModel):
    col: int
    fila: int
    x0: float
    x1: float
    y0: float
    y1: float
    n: int
    valor: float
    valor_norm: float


class EscalaMapa(BaseModel):
    min: float
    max: float
    unidad: str


class MapaResp(BaseModel):
    capa: Capa
    modo: Modo
    n: int
    tam_celda: float
    x_min: float
    x_max: float
    celdas: list[CeldaMapa]
    escala: EscalaMapa
