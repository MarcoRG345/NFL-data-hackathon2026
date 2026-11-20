"""Modelos y tipos compartidos (esqueleto). Espejo de contrato-api.md."""
import math
from typing import Annotated, Literal

import numpy as np
from pydantic import BaseModel, Field

Filtro = Literal["decisivo", "pocas_yardas", "reloj_final", "marcador_cerrado", "normal"]
Vista = Literal["ofe", "def"]
Modo = Literal["decisivo", "normal"]
Capa = Literal["giro", "vuelo"]

# [bajo, alto] al 90 %. En los modelos se usa como `Intervalo | None`.
Intervalo = Annotated[list[float], Field(min_length=2, max_length=2)]


class EstadoDatos(BaseModel):
    listo: bool
    cargando: bool
    error: str | None
    semanas: int
    n_jugadas: int


class ErrorDetalle(BaseModel):
    detalle: str


def a_json(valor, decimales: int | None = None):
    """numpy -> Python, NaN/inf -> None, redondeo opcional. Recursivo en dict, list y tuple."""
    if isinstance(valor, dict):
        return {k: a_json(v, decimales) for k, v in valor.items()}
    if isinstance(valor, (list, tuple)):
        return [a_json(v, decimales) for v in valor]
    if isinstance(valor, np.generic):
        valor = valor.item()
    if isinstance(valor, float):
        if math.isnan(valor) or math.isinf(valor):
            return None
        return round(valor, decimales) if decimales is not None else valor
    return valor
