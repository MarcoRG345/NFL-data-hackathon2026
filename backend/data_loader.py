"""
Carga de datos: lee el tracking partido por partido, normaliza, recorta y arma las tablas de entrada.

Entrada : data/games.csv, plays.csv, players.csv, pffScoutingData.csv y data/tracking/tracking_<gameId>.csv.
          La semana de cada partido sale de games.csv; DATOS_SEMANAS elige qué partidos se leen.
Salida  : dict con
  games, plays, players, scouting   DataFrames completos (chicos)
  cuadros                           tracking normalizado (ataque hacia la derecha), solo QB, Pass Route,
                                    Coverage, Pass Rush y balón, del cuadro del snap al ÚLTIMO cuadro
                                    disponible de cada jugada (pass_arrived no existe en estos datos)
  eventos                           una fila por jugada válida: frame_snap, frame_lanza, frame_sack,
                                    frame_ultimo, linea_golpeo, fuente_linea, marcada, diff_cprime_D
  excluidas                         conteo de jugadas excluidas por motivo
No calcula métricas (eso es de base/ y calculos/). No escribe a disco.
"""
import time

import numpy as np
import pandas as pd

from backend.columnas import (
    COL_ABSOLUTE_YARDLINE_NUMBER, COL_FRAME_ID, COL_GAME_ID, COL_NFL_ID, COL_PFF_ROLE,
    COL_PLAY_DESCRIPTION, COL_PLAY_ID, COL_WEEK,
    EVENT_AUTO_BALLSNAP, EVENT_AUTO_PASSFORWARD, EVENT_BALL_SNAP, EVENT_PASS_FORWARD,
    EVENT_QB_SACK, EVENT_QB_STRIP_SACK, ROL_BALON, ROLES_A_CONSERVAR, TEAM_FOOTBALL,
)
from backend.config import DATA_DIR, DATOS_SEMANAS, TRACKING_DIR
from backend.normalizacion import calcular_linea_golpeo, normalizar_direccion

COLS_TRACKING = [
    "gameId", "playId", "nflId", "frameId", "jerseyNumber", "team", "playDirection",
    "x", "y", "s", "a", "dis", "o", "dir", "event",
]
DTYPES_TRACKING = {
    "gameId": "int32", "playId": "int32", "nflId": "float32", "frameId": "int32",
    "jerseyNumber": "float32", "team": "category", "playDirection": "category",
    "x": "float32", "y": "float32", "s": "float32", "a": "float32", "dis": "float32",
    "o": "float32", "dir": "float32", "event": "category",
}
# Columnas que quedan en `cuadros`
COLS_CUADROS = [
    "gameId", "playId", "nflId", "frameId", "jerseyNumber", "team",
    "x", "y", "s", "a", "dis", "o", "dir", "pff_role",
]
EVENTOS_INTERES = [
    EVENT_BALL_SNAP, EVENT_AUTO_BALLSNAP, EVENT_PASS_FORWARD, EVENT_AUTO_PASSFORWARD,
    EVENT_QB_SACK, EVENT_QB_STRIP_SACK,
]
ROLES_CATEGORIAS = sorted(ROLES_A_CONSERVAR) + [ROL_BALON]


def _leer_partido(ruta) -> pd.DataFrame:
    """Lee un partido con tipos pequeños. 'None' en `event` ya llega como NaN (= sin evento)."""
    trk = pd.read_csv(ruta, usecols=COLS_TRACKING, dtype=DTYPES_TRACKING)
    # el balón no tiene nflId: -1; el resto cabe exacto en float32 (ids < 16 M)
    trk["nflId"] = trk["nflId"].fillna(-1).astype("int32")
    trk["jerseyNumber"] = trk["jerseyNumber"].fillna(-1).astype("int16")
    return trk


def _eventos_por_jugada(trk: pd.DataFrame) -> pd.DataFrame:
    """Una fila por jugada con frame_snap, frame_lanza, frame_sack, frame_ultimo (vectorizado)."""
    ev = trk.loc[trk["event"].isin(EVENTOS_INTERES), ["gameId", "playId", "event", "frameId"]].copy()
    ev["event"] = ev["event"].astype(str)
    piv = ev.groupby(["gameId", "playId", "event"])["frameId"].min().unstack("event")
    for c in EVENTOS_INTERES:
        if c not in piv.columns:
            piv[c] = np.nan
    out = pd.DataFrame(index=piv.index)
    out["frame_snap"] = piv[EVENT_BALL_SNAP].fillna(piv[EVENT_AUTO_BALLSNAP])
    out["frame_lanza"] = piv[EVENT_PASS_FORWARD].fillna(piv[EVENT_AUTO_PASSFORWARD])
    out["frame_sack"] = piv[[EVENT_QB_SACK, EVENT_QB_STRIP_SACK]].min(axis=1)
    out = out.reset_index()
    # todas las jugadas del partido, incluso las que no tienen ninguno de estos eventos
    todas = trk.groupby(["gameId", "playId"], observed=True)["frameId"].max().rename("frame_ultimo").reset_index()
    return todas.merge(out, on=["gameId", "playId"], how="left", validate="one_to_one")


def _linea_golpeo(trk: pd.DataFrame, ev_ok: pd.DataFrame, plays_g: pd.DataFrame) -> pd.DataFrame:
    """Línea de golpeo con normalizacion.py. Se le pasa solo el balón, con `event` = 'ball_snap'
    en frame_snap (así también funciona cuando el snap viene de autoevent_ballsnap)."""
    ball = trk.loc[trk["team"] == TEAM_FOOTBALL, ["gameId", "playId", "frameId", "x", "y", "playDirection"]]
    ball = ball.merge(ev_ok[["gameId", "playId", "frame_snap"]], on=["gameId", "playId"],
                      how="inner", validate="many_to_one")
    ball["event"] = np.where(ball["frameId"] == ball["frame_snap"], EVENT_BALL_SNAP, "None")
    ball["nflId"] = np.nan  # normalizacion.py identifica el balón por nflId NaN
    ball["playDirection"] = ball["playDirection"].astype(str)
    ball = normalizar_direccion(ball.drop(columns=["frame_snap"]))
    return calcular_linea_golpeo(ball, plays_g)


def cargar_datos_base() -> dict:
    t0 = time.time()
    print("[carga] leyendo games, plays, players, pffScoutingData...")
    games = pd.read_csv(DATA_DIR / "games.csv")
    plays = pd.read_csv(DATA_DIR / "plays.csv")
    players = pd.read_csv(DATA_DIR / "players.csv")
    scouting = pd.read_csv(DATA_DIR / "pffScoutingData.csv")

    roles = scouting[[COL_GAME_ID, COL_PLAY_ID, COL_NFL_ID, COL_PFF_ROLE]].copy()
    roles = roles[roles[COL_PFF_ROLE].isin(ROLES_A_CONSERVAR)].dropna(subset=[COL_NFL_ID])
    roles = roles.astype({COL_GAME_ID: "int32", COL_PLAY_ID: "int32", COL_NFL_ID: "int32"})

    equipos = sorted(set(games["homeTeamAbbr"]) | set(games["visitorTeamAbbr"])) + [TEAM_FOOTBALL]
    tipo_team = pd.CategoricalDtype(equipos)
    tipo_rol = pd.CategoricalDtype(ROLES_CATEGORIAS)

    partidos = games.loc[games[COL_WEEK].isin(DATOS_SEMANAS), [COL_GAME_ID, COL_WEEK]]
    partidos = partidos.sort_values([COL_WEEK, COL_GAME_ID]).reset_index(drop=True)
    print(f"[carga] semanas {DATOS_SEMANAS}: {len(partidos)} partidos")

    excluidas = {"no_play": 0, "dos_puntos": 0, "sin_ball_snap": 0, "sin_registro_plays": 0}
    lista_cuadros, lista_eventos = [], []
    semana_previa = None
    for i, (gid, sem) in enumerate(zip(partidos[COL_GAME_ID], partidos[COL_WEEK]), start=1):
        if sem != semana_previa:
            print(f"[carga] semana {sem} ({i}/{len(partidos)} partidos)")
            semana_previa = sem
        ruta = TRACKING_DIR / f"tracking_{gid}.csv"
        if not ruta.exists():
            print(f"[carga]   falta {ruta.name}, se omite")
            continue
        trk = _leer_partido(ruta)

        # --- eventos y exclusiones ---
        ev = _eventos_por_jugada(trk)
        plays_g = plays.loc[plays[COL_GAME_ID] == gid,
                            [COL_GAME_ID, COL_PLAY_ID, COL_PLAY_DESCRIPTION, COL_ABSOLUTE_YARDLINE_NUMBER]]
        ev = ev.merge(plays_g, on=["gameId", "playId"], how="left", validate="one_to_one")
        sin_reg = ev[COL_PLAY_DESCRIPTION].isna()
        no_play = ev[COL_PLAY_DESCRIPTION].str.contains("No Play", na=False)
        dos_pts = ev[COL_PLAY_DESCRIPTION].str.contains("TWO-POINT", case=False, na=False)  # = down 0 en plays.csv
        sin_snap = ev["frame_snap"].isna()
        # cada jugada excluida se cuenta en un solo motivo (orden: sin registro, No Play, dos puntos, sin snap)
        excluidas["sin_registro_plays"] += int(sin_reg.sum())
        excluidas["no_play"] += int((no_play & ~sin_reg).sum())
        excluidas["dos_puntos"] += int((dos_pts & ~no_play & ~sin_reg).sum())
        excluidas["sin_ball_snap"] += int((sin_snap & ~dos_pts & ~no_play & ~sin_reg).sum())
        ev_ok = ev[~sin_reg & ~no_play & ~dos_pts & ~sin_snap].copy()
        if ev_ok.empty:
            del trk
            continue

        # --- línea de golpeo (normalizacion.py) ---
        linea = _linea_golpeo(trk, ev_ok, plays_g[plays_g[COL_PLAY_ID].isin(ev_ok["playId"])])
        ev_ok = ev_ok.merge(linea, on=["gameId", "playId"], how="left", validate="one_to_one")

        # --- recorte: snap → último cuadro disponible ---
        rango = ev_ok[["gameId", "playId", "frame_snap", "frame_ultimo"]].astype(
            {"frame_snap": "int32", "frame_ultimo": "int32"})
        trk = trk.merge(rango, on=["gameId", "playId"], how="inner", validate="many_to_one")
        trk = trk[(trk["frameId"] >= trk["frame_snap"]) & (trk["frameId"] <= trk["frame_ultimo"])]

        # --- roles de PFF (many_to_one) y recorte por rol ---
        trk = trk.merge(roles[roles[COL_GAME_ID] == gid], on=["gameId", "playId", "nflId"],
                        how="left", validate="many_to_one")
        es_balon = trk["team"] == TEAM_FOOTBALL
        trk[COL_PFF_ROLE] = trk[COL_PFF_ROLE].astype(object)
        trk.loc[es_balon, COL_PFF_ROLE] = ROL_BALON
        trk = trk[trk[COL_PFF_ROLE].notna()]

        # --- normalizar (ataque hacia la derecha) y dejar solo lo necesario ---
        trk = normalizar_direccion(trk)
        trk["team"] = trk["team"].astype(object).astype(tipo_team)
        trk[COL_PFF_ROLE] = trk[COL_PFF_ROLE].astype(tipo_rol)
        lista_cuadros.append(trk[COLS_CUADROS].reset_index(drop=True))
        lista_eventos.append(ev_ok.drop(columns=[COL_PLAY_DESCRIPTION, COL_ABSOLUTE_YARDLINE_NUMBER]))
        del trk

    if not lista_cuadros:
        raise ValueError("No se cargó ningún partido de tracking.")
    cuadros = pd.concat(lista_cuadros, ignore_index=True)
    eventos = pd.concat(lista_eventos, ignore_index=True)
    del lista_cuadros, lista_eventos
    for c in ["frame_snap", "frame_lanza", "frame_sack", "frame_ultimo"]:
        eventos[c] = eventos[c].astype("Int32")

    print(f"[carga] jugadas válidas: {len(eventos):,}; cuadros: {len(cuadros):,}; excluidas: {excluidas}")
    print(f"[carga] listo en {time.time() - t0:.1f} s")
    return {
        "games": games, "plays": plays, "players": players, "scouting": scouting,
        "cuadros": cuadros, "eventos": eventos, "excluidas": excluidas,
        "n_partidos": len(partidos),
    }
