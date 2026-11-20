"""
Tabla base `presion`: cuándo llega la presión al mariscal (QB = `pff_role` "Pass"), una fila por jugada.

Entrada : datos["cuadros"], datos["jugadas"].
Salida  : gameId, playId, frame_presion, t_presion (s desde el snap, NaN si nunca llega),
          nflId_rusher (el que llegó primero; NaN si fue por sack), por_sack (bool),
          fuente ("distancia" | "sack" | "ninguna").
Regla   : primer cuadro tras el snap y antes del lanzamiento con un `Pass Rush` a <= radio del QB.
          Sin lanzamiento, se busca hasta el sack (si hay) o el último cuadro. Se deja de buscar
          desde el primer cuadro en que el QB está más allá de la línea de golpeo (x_qb > linea_golpeo).
          Si no llegó por distancia y hubo sack (passResult S o evento de sack): cuadro del sack
          (`frame_sack`; si no hay evento, el último cuadro), por_sack = True.
`calcular_presion(cuadros, jugadas, radio)` permite repetir con otros radios (robustez 1.5 y 3.0).
"""
import numpy as np
import pandas as pd

from backend.columnas import ROLE_PASS, ROLE_PASS_RUSH
from backend.config import FPS, RADIO_PRESION

PARTIDOS_POR_BLOQUE = 4
COLS_J = ["gameId", "playId", "frame_snap", "frame_lanza", "frame_sack", "frame_ultimo", "linea_golpeo"]


def _bloque(qb: pd.DataFrame, rush: pd.DataFrame, radio: float) -> pd.DataFrame:
    m = qb.merge(rush, on=["gameId", "playId", "frameId"], how="inner")
    d = np.hypot(m["x_qb"].to_numpy() - m["x"].to_numpy(), m["y_qb"].to_numpy() - m["y"].to_numpy())
    m = m.assign(d=d.astype("float32"))
    m = m[(m["d"] <= radio) & (m["frameId"] > m["frame_snap"]) & (m["frameId"] <= m["f_hasta"])
          & (m["frameId"] < m["f_cruza"])]
    m = m.sort_values(["frameId", "d"], kind="stable").drop_duplicates(["gameId", "playId"])
    return m[["gameId", "playId", "frameId", "nflId"]]


def calcular_presion(cuadros: pd.DataFrame, jugadas: pd.DataFrame, radio: float = RADIO_PRESION) -> pd.DataFrame:
    j = jugadas[COLS_J + ["passResult"]].copy()
    rol = cuadros["pff_role"]
    qb = cuadros.loc[rol == ROLE_PASS, ["gameId", "playId", "frameId", "x", "y"]]
    qb = qb.rename(columns={"x": "x_qb", "y": "y_qb"})
    rush = cuadros.loc[rol == ROLE_PASS_RUSH, ["gameId", "playId", "frameId", "nflId", "x", "y"]]

    # primer cuadro con el QB pasada la línea de golpeo (se deja de buscar desde ahí)
    qb = qb.merge(j[["gameId", "playId", "frame_snap", "linea_golpeo"]], on=["gameId", "playId"], how="inner")
    cruza = qb.loc[qb["x_qb"] > qb["linea_golpeo"]].groupby(["gameId", "playId"])["frameId"].min()
    cruza = cruza.rename("f_cruza").reset_index()
    j = j.merge(cruza, on=["gameId", "playId"], how="left")
    j["f_cruza"] = j["f_cruza"].fillna(2**30).astype("int64")
    # último cuadro permitido: antes del lanzamiento; sin lanzamiento, el sack o el último cuadro
    j["f_hasta"] = np.where(j["frame_lanza"].notna(), j["frame_lanza"].astype("float64") - 1,
                            j["frame_sack"].fillna(j["frame_ultimo"]).astype("float64")).astype("int64")
    qb = qb.drop(columns=["frame_snap", "linea_golpeo"]).merge(
        j[["gameId", "playId", "frame_snap", "f_hasta", "f_cruza"]].astype({"frame_snap": "int32"}),
        on=["gameId", "playId"], how="inner")

    juegos = np.sort(qb["gameId"].unique())
    partes = []
    for i in range(0, len(juegos), PARTIDOS_POR_BLOQUE):
        ids = juegos[i:i + PARTIDOS_POR_BLOQUE]
        partes.append(_bloque(qb[qb["gameId"].isin(ids)], rush[rush["gameId"].isin(ids)], radio))
    llega = pd.concat(partes, ignore_index=True).rename(columns={"frameId": "frame_dist", "nflId": "nflId_rusher"})

    out = j[["gameId", "playId", "frame_snap", "frame_sack", "frame_ultimo", "passResult"]].merge(
        llega, on=["gameId", "playId"], how="left", validate="one_to_one")
    por_dist = out["frame_dist"].notna()
    hubo_sack = (out["passResult"].astype(str) == "S") | out["frame_sack"].notna()
    por_sack = ~por_dist & hubo_sack
    f_sack = out["frame_sack"].fillna(out["frame_ultimo"]).astype("float64")
    frame = np.where(por_dist, out["frame_dist"], np.where(por_sack, f_sack, np.nan))
    out["frame_presion"] = pd.Series(frame, index=out.index).astype("Int32")
    out["t_presion"] = ((frame - out["frame_snap"].astype("float64")) / FPS).astype("float32")
    out["por_sack"] = por_sack
    out["fuente"] = np.where(por_dist, "distancia", np.where(por_sack, "sack", "ninguna"))
    out["fuente"] = out["fuente"].astype("category")
    out.loc[~por_dist, "nflId_rusher"] = np.nan
    out["nflId_rusher"] = out["nflId_rusher"].astype("Int32")
    return out[["gameId", "playId", "frame_presion", "t_presion", "nflId_rusher", "por_sack", "fuente"]]


def construir_presion(cuadros: pd.DataFrame, jugadas: pd.DataFrame) -> pd.DataFrame:
    return calcular_presion(cuadros, jugadas, RADIO_PRESION)
