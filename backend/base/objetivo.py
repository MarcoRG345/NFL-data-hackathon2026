"""
Tabla base `objetivo`: receptor objetivo de cada pase con passResult C o I (una fila por esa jugada).

Entrada : datos["jugadas"] (con playDescription), datos["cuadros"], datos["players"], `sep_cuadros`.
Salida  : gameId, playId, nflId_objetivo, aproximado, valido, metodo ("texto"|"ninguno"),
          dist_balon (yd, receptor elegido ↔ balón en el último cuadro),
          sep_lanza (separación del objetivo en frame_lanza), sep_antes (0.5 s antes), tendencia (lanza − antes).

Regla del texto (metodo = "texto", aproximado = False):
  1. De playDescription se toma lo que sigue al primer " to " después de la palabra "pass", hasta el
     siguiente " to ", " for ", " pushed", " ran ", " (", " [", " at ", " out ", coma, un punto seguido de
     "Penalty"/"Ball"/"The"/"Replay"/"XX-" o el punto final.
     Ej.: "J.Herbert pass short right to K.Allen to KC 36 for 15 yards" -> "K.Allen".
  2. Se quita el sufijo (Jr., Sr., II, III, IV, V). Inicial = primera letra. Apellido = lo que sigue al primer
     punto, solo letras en minúscula (quita guiones, puntos y espacios): "J.Smith-Schuster" -> "smithschuster",
     "E.St. Brown" -> "stbrown", "D.J.Moore" -> "jmoore".
  3. De displayName de cada `Pass Route` del equipo atacante en la jugada: inicial = primera letra del nombre,
     apellido = todo lo que sigue al primer token, sin sufijo y solo letras ("DJ Moore" -> "moore").
  4. Coincide si la inicial es igual y el apellido es igual (exacto). Si ninguno es exacto, se acepta el
     que termine igual que el otro (p. ej. "jmoore" vs "moore", mínimo 3 letras). Se exige UN solo candidato
     en su nivel; si hay 0 o más de 1, no hay objetivo.
Sin respaldo por balón: si no hay coincidencia única, la fila queda valido = False, metodo = "ninguno",
nflId_objetivo nulo y aproximado = False. `aproximado` se conserva solo por compatibilidad (siempre False).
"""
import numpy as np
import pandas as pd

from backend.columnas import ROLE_PASS_ROUTE, TEAM_FOOTBALL
from backend.config import FPS

RE_OBJETIVO = (r"\bpass\b.*?\sto\s+(.+?)"
               r"(?=\s+to\s|\s+for\s|\s+pushed|\s+ran\s|\s+\(|\s+\[|\s+at\s|\s+out\s|,"
               r"|\.\s+(?:Penalty|Ball|The |Replay|[A-Z]{2,3}-)|\.$|$)")
RE_SUFIJO = r"\s+(?:Jr|Sr|II|III|IV|V)\.?$"


def _letras(s: pd.Series) -> pd.Series:
    return s.str.lower().str.replace(r"[^a-z]", "", regex=True)


def _texto_objetivo(desc: pd.Series) -> pd.DataFrame:
    """Inicial y apellido (solo letras) del nombre que sigue a ' to ' en la descripción."""
    nom = desc.str.extract(RE_OBJETIVO, expand=False).str.strip()
    nom = nom.str.replace(RE_SUFIJO, "", regex=True)
    ini = nom.str.extract(r"^([A-Za-z])", expand=False).str.lower()
    resto = nom.str.extract(r"^[^.]*\.(.*)$", expand=False)  # lo que sigue al primer punto
    ultimo = _letras(resto.where(resto.notna(), nom))
    ini = ini.where(resto.notna())  # sin punto (nombre sin inicial): no se compara la inicial
    return pd.DataFrame({"txt_nombre": nom, "txt_ini": ini, "txt_ult": ultimo.replace("", np.nan)})


def _nombre_jugador(players: pd.DataFrame) -> pd.DataFrame:
    nom = players["displayName"].fillna("").str.strip().str.replace(RE_SUFIJO, "", regex=True)
    partes = nom.str.split(" ", n=1, expand=True)
    if partes.shape[1] < 2:
        partes[1] = None
    ini = partes[0].str[:1].str.lower()
    ult = _letras(partes[1].where(partes[1].notna(), partes[0]))
    return pd.DataFrame({"nflId": players["nflId"].astype("int32"), "dp_ini": ini, "dp_ult": ult})


def construir_objetivo(jugadas: pd.DataFrame, cuadros: pd.DataFrame, players: pd.DataFrame,
                       sep_cuadros: pd.DataFrame) -> pd.DataFrame:
    j = jugadas.loc[jugadas["passResult"].astype(str).isin(["C", "I"]),
                    ["gameId", "playId", "playDescription", "frame_lanza", "frame_ultimo"]].reset_index(drop=True)
    j = pd.concat([j, _texto_objetivo(j["playDescription"])], axis=1)

    # receptores de cada jugada con pase (una fila por receptor)
    rec = cuadros.loc[cuadros["pff_role"] == ROLE_PASS_ROUTE, ["gameId", "playId", "nflId"]].drop_duplicates()
    rec = rec.merge(j[["gameId", "playId"]], on=["gameId", "playId"], how="inner")
    rec = rec.merge(_nombre_jugador(players), on="nflId", how="left")

    # --- 1) coincidencia por texto ---
    c = rec.merge(j[["gameId", "playId", "txt_ini", "txt_ult"]], on=["gameId", "playId"], how="inner")
    ini_ok = c["txt_ini"].isna() | (c["txt_ini"] == c["dp_ini"])
    a, b = c["txt_ult"].fillna(""), c["dp_ult"].fillna("")
    exacto = ini_ok & (a == b) & (a != "")
    largo = (a.str.len() >= 3) & (b.str.len() >= 3)
    flojo = ini_ok & largo & (
        pd.Series([x.endswith(y) or y.endswith(x) for x, y in zip(a, b)], index=c.index))
    c["exacto"], c["flojo"] = exacto, flojo & ~exacto
    n = c.groupby(["gameId", "playId"])[["exacto", "flojo"]].transform("sum")
    c["elegido"] = (c["exacto"] & (n["exacto"] == 1)) | (c["flojo"] & (n["exacto"] == 0) & (n["flojo"] == 1))
    texto = c.loc[c["elegido"], ["gameId", "playId", "nflId"]].rename(columns={"nflId": "nflId_texto"})
    j = j.merge(texto, on=["gameId", "playId"], how="left", validate="one_to_one")

    # --- 2) distancia al balón en el último cuadro (solo informativa; no elige objetivo) ---
    ult = j[["gameId", "playId", "frame_ultimo"]].astype({"frame_ultimo": "int32"}).rename(
        columns={"frame_ultimo": "frameId"})
    balon = cuadros.loc[cuadros["team"] == TEAM_FOOTBALL, ["gameId", "playId", "frameId", "x", "y"]]
    balon = ult.merge(balon, on=["gameId", "playId", "frameId"], how="inner").rename(
        columns={"x": "xb", "y": "yb"})
    pos = cuadros.loc[cuadros["pff_role"] == ROLE_PASS_ROUTE, ["gameId", "playId", "frameId", "nflId", "x", "y"]]
    pos = balon.merge(pos, on=["gameId", "playId", "frameId"], how="inner")
    pos["dist_balon"] = np.hypot(pos["x"] - pos["xb"], pos["y"] - pos["yb"]).astype("float32")

    hay_texto = j["nflId_texto"].notna()
    j["metodo"] = np.where(hay_texto, "texto", "ninguno")
    j["nflId_objetivo"] = np.where(hay_texto, j["nflId_texto"], np.nan)
    j["aproximado"] = False
    j["valido"] = hay_texto

    # distancia al balón del objetivo elegido
    dist = pos[["gameId", "playId", "nflId", "dist_balon"]].rename(columns={"nflId": "nflId_objetivo"})
    dist["nflId_objetivo"] = dist["nflId_objetivo"].astype("float64")
    j = j.merge(dist, on=["gameId", "playId", "nflId_objetivo"], how="left")

    # separación al lanzar y 0.5 s antes (desde sep_cuadros)
    sc = sep_cuadros[["gameId", "playId", "nflId", "frameId", "separacion"]].rename(
        columns={"nflId": "nflId_objetivo"})
    sc["nflId_objetivo"] = sc["nflId_objetivo"].astype("float64")
    medio = int(round(0.5 * FPS))
    for nombre, desfase in (("sep_lanza", 0), ("sep_antes", medio)):
        k = j[["gameId", "playId", "nflId_objetivo", "frame_lanza"]].copy()
        k["frameId"] = (k["frame_lanza"].astype("float64") - desfase)
        k = k.dropna(subset=["frameId"]).astype({"frameId": "int32"})
        k = k.merge(sc, on=["gameId", "playId", "nflId_objetivo", "frameId"], how="left")
        j[nombre] = _alinear(j, k)
    j["tendencia"] = (j["sep_lanza"] - j["sep_antes"]).astype("float32")

    j["nflId_objetivo"] = j["nflId_objetivo"].astype("Int32")
    j["metodo"] = j["metodo"].astype("category")
    cols = ["gameId", "playId", "nflId_objetivo", "aproximado", "valido", "metodo", "dist_balon",
            "sep_lanza", "sep_antes", "tendencia"]
    return j[cols].sort_values(["gameId", "playId"]).reset_index(drop=True)


def _alinear(j: pd.DataFrame, k: pd.DataFrame) -> pd.Series:
    """Devuelve la separación de `k` alineada con las filas de `j` por (gameId, playId)."""
    s = k.drop_duplicates(["gameId", "playId"]).set_index(["gameId", "playId"])["separacion"]
    idx = pd.MultiIndex.from_frame(j[["gameId", "playId"]])
    return pd.Series(s.reindex(idx).to_numpy(), index=j.index).astype("float32")
