"""Modelos de respuesta de la persona A (carrera, síntesis, cancha). Campo por campo con contrato-api.md."""
from typing import Literal

from pydantic import BaseModel

from .comun import Filtro, Intervalo, Vista


# --- api/resumen ---
class Kpis(BaseModel):
    pct_gana_receptor: float
    pct_gana_defensa: float
    conv_gana_receptor: float | None
    conv_gana_defensa: float | None
    reloj_defensa_mediana: float | None
    conv_equipo: float | None
    eslabon_equipo: Literal["P1", "P2", "P3", "—"] | None


class PasoCadena(BaseModel):
    paso: str
    pct: float


class ResumenResp(BaseModel):
    filtro: Filtro
    vista: Vista
    n: int
    kpis: Kpis
    cadena_liga: list[PasoCadena]
    insight: str


# --- api/carrera/curvas ---
class PuntoCurva(BaseModel):
    t: float
    pct_libre: float
    pct_presion: float


class CurvasResp(BaseModel):
    filtro: Filtro
    n: int
    puntos: list[PuntoCurva]
    mediana_libre: float | None
    mediana_presion: float | None
    ventaja: float | None


# --- api/carrera/distancia ---
class GrupoDistancia(BaseModel):
    grupo: Literal["3.º y 1–3", "3.º y 4–6", "3.º y 7+", "4.º down"]
    n: int
    conv_gana: float | None
    conv_pierde: float | None
    ic_gana: Intervalo | None
    ic_pierde: Intervalo | None


class DistanciaResp(BaseModel):
    filtro: Filtro
    grupos: list[GrupoDistancia]


# --- api/carrera/resultado ---
class ResultadoResp(BaseModel):
    filtro: Filtro
    n: int
    pct_gana_receptor: float
    pct_gana_defensa: float
    pct_sin_presion: float
    pct_sack_con_libre: float


# --- api/equipos ---
class MedianasEquipos(BaseModel):
    t_presion: float | None
    p1: float | None
    p2: float | None
    p3: float | None
    conv: float | None


class EquipoFila(BaseModel):
    equipo: str
    n: int
    t_presion_mediana: float | None
    p2_se_libera: float | None
    p1_gana_carrera: float | None
    p3_sigue_libre: float | None
    conv: float | None
    cadena: list[float]
    eslabon: Literal["P1", "P2", "P3", "—"]
    cuadrante: Literal[
        "Todo funciona",
        "Se liberan, pero no hay tiempo",
        "La línea aguanta, nadie se libera",
        "Nada funciona",
        "Muestra pequeña",
    ]


class EquiposResp(BaseModel):
    filtro: Filtro
    vista: Vista
    medianas: MedianasEquipos
    equipos: list[EquipoFila]


# --- api/jugadas-ejemplo (la respuesta es list[EjemploJugada]) ---
class EjemploJugada(BaseModel):
    id: str
    gameId: int
    playId: int
    titulo: str
    ganador: Literal["receptor", "defensa"]
    situacion: str


# --- api/jugada ---
class ContextoJugada(BaseModel):
    down: int
    yardsToGo: int
    cuarto: int
    reloj: str
    marcador_texto: str
    descripcion: str
    resultado: str


class RelojesJugada(BaseModel):
    t_presion: float | None
    t_libre: float | None
    ganador: Literal["receptor", "defensa", "sin_presion"]
    margen: float | None


class BalonJugada(BaseModel):
    t_lanza: float
    t_llega: float
    x_lanza: float
    y_lanza: float
    x_llega: float
    y_llega: float


class EventoJugada(BaseModel):
    t: float
    nombre: str


class BalonCuadro(BaseModel):
    x: float
    y: float
    altura: float


class JugadorCuadro(BaseModel):
    nflId: int
    x: float
    y: float
    s: float
    dir: float
    giro_grados: float
    girando: bool
    lado: Literal["ataque", "defensa"]
    jersey: int | None
    posicion: str
    rol: Literal["qb", "receptor", "defensor", "rusher", "otro"]


class CuadroJugada(BaseModel):
    t: float
    separacion: float | None
    receptor_libre: bool
    presion_llego: bool
    balon: BalonCuadro
    jugadores: list[JugadorCuadro]


class JugadaResp(BaseModel):
    contexto: ContextoJugada
    linea_golpeo: float
    linea_primer_down: float
    relojes: RelojesJugada
    balon: BalonJugada
    eventos: list[EventoJugada]
    cuadros: list[CuadroJugada]
