"""
Tabla base `sep_cuadros`: separación de cada receptor (`Pass Route`) en cada cuadro, del snap al último cuadro.

Entrada : datos["cuadros"], datos["jugadas"].
Salida  : DataFrame con gameId, playId, nflId (receptor), frameId, t (s desde el snap), x, y,
          separacion (yd al `Coverage` más cercano EN ESE cuadro), nflId_def, libre.
          libre = separacion >= ABIERTO_YD y t >= INICIO_LIBRE_SEG.
Método  : por bloques de partidos, merge receptores × defensores por (gameId, playId, frameId),
          distancia euclidiana y mínimo por (receptor, cuadro). Sin ciclos por fila.
"""
import numpy as np
import pandas as pd

from backend.columnas import ROLE_COVERAGE, ROLE_PASS_ROUTE
from backend.config import ABIERTO_YD, FPS, INICIO_LIBRE_SEG

PARTIDOS_POR_BLOQUE = 4
CLAVE = ["gameId", "playId", "frameId", "nflId"]


def _bloque(rec: pd.DataFrame, cov: pd.DataFrame) -> pd.DataFrame:
    m = rec.merge(cov, on=["gameId", "playId", "frameId"], how="inner")
    d = np.hypot(m["x"].to_numpy() - m["x_def"].to_numpy(), m["y"].to_numpy() - m["y_def"].to_numpy())
    m["separacion"] = d.astype("float32")
    m = m.sort_values("separacion", kind="stable").drop_duplicates(CLAVE)
    return m[CLAVE + ["x", "y", "separacion", "nflId_def"]]


def construir_sep_cuadros(cuadros: pd.DataFrame, jugadas: pd.DataFrame, abierto: float = ABIERTO_YD) -> pd.DataFrame:
    rol = cuadros["pff_role"]
    rec = cuadros.loc[rol == ROLE_PASS_ROUTE, ["gameId", "playId", "frameId", "nflId", "x", "y"]]
    cov = cuadros.loc[rol == ROLE_COVERAGE, ["gameId", "playId", "frameId", "nflId", "x", "y"]]
    cov = cov.rename(columns={"nflId": "nflId_def", "x": "x_def", "y": "y_def"})

    juegos = np.sort(rec["gameId"].unique())
    partes = []
    for i in range(0, len(juegos), PARTIDOS_POR_BLOQUE):
        ids = juegos[i:i + PARTIDOS_POR_BLOQUE]
        partes.append(_bloque(rec[rec["gameId"].isin(ids)], cov[cov["gameId"].isin(ids)]))
    out = pd.concat(partes, ignore_index=True)
    del partes

    snap = jugadas[["gameId", "playId", "frame_snap"]].astype({"frame_snap": "int32"})
    out = out.merge(snap, on=["gameId", "playId"], how="left", validate="many_to_one")
    out["t"] = ((out["frameId"] - out["frame_snap"]) / FPS).astype("float32")
    out["libre"] = (out["separacion"] >= abierto) & (out["t"] >= INICIO_LIBRE_SEG)
    out = out.drop(columns=["frame_snap"])
    out = out.astype({"nflId_def": "int32"})
    return out.sort_values(["gameId", "playId", "nflId", "frameId"]).reset_index(drop=True)
