"""
Tabla base `jugadas`: una fila por jugada válida (contexto, banderas de filtro, cuadros y tiempos de eventos).

Entrada : datos["eventos"], datos["plays"], datos["games"] (los deja la carga).
Salida  : DataFrame `jugadas`, ordenado por gameId, playId.
Reglas (steering pregunta.md):
  decisivo         down 3 o 4
  pocas_yardas     down 3 o 4 con yardsToGo <= 3
  reloj_final      <= 120 s restantes en el 2.º o 4.º cuarto (se aplica tal cual, sin exigir down)
  marcador_cerrado 4.º cuarto con |diferencia| <= 8 (tal cual, sin exigir down)
  normal           down 1 o 2
  convirtio        playResult >= yardsToGo
  t_fin            lanzamiento si hubo; si no el sack; si no el último cuadro (segundos desde el snap)
No calcula métricas por equipo.
"""
import numpy as np
import pandas as pd

from backend.config import FPS

COLS_PLAYS = [
    "gameId", "playId", "playDescription", "quarter", "down", "yardsToGo", "possessionTeam",
    "defensiveTeam", "gameClock", "preSnapHomeScore", "preSnapVisitorScore", "passResult",
    "playResult", "pff_passCoverageType", "dropBackType",
]


def _reloj_a_segundos(s: pd.Series) -> pd.Series:
    """'MM:SS' (o ':SS') a segundos. Texto vacío o raro -> NaN."""
    partes = s.astype("string").str.strip().str.split(":", n=1, expand=True)
    if partes.shape[1] < 2:
        return pd.Series(np.nan, index=s.index)
    mm = pd.to_numeric(partes[0].replace("", "0"), errors="coerce")
    ss = pd.to_numeric(partes[1], errors="coerce")
    return (mm * 60 + ss).astype("float32")


def construir_jugadas(eventos: pd.DataFrame, plays: pd.DataFrame, games: pd.DataFrame) -> pd.DataFrame:
    ev = eventos.drop(columns=[c for c in ("marcada", "diff_cprime_D", "fuente_linea") if c in eventos.columns])
    j = ev.merge(plays[COLS_PLAYS], on=["gameId", "playId"], how="left", validate="one_to_one")
    j = j.merge(games[["gameId", "week", "homeTeamAbbr", "visitorTeamAbbr"]], on="gameId",
                how="left", validate="many_to_one")

    j["reloj_seg"] = _reloj_a_segundos(j["gameClock"])
    es_local = j["possessionTeam"] == j["homeTeamAbbr"]
    j["pts_ataque"] = np.where(es_local, j["preSnapHomeScore"], j["preSnapVisitorScore"]).astype("int16")
    j["pts_defensa"] = np.where(es_local, j["preSnapVisitorScore"], j["preSnapHomeScore"]).astype("int16")
    j["dif_marcador"] = (j["pts_ataque"] - j["pts_defensa"]).astype("int16")  # desde el ataque

    down, ytg, q = j["down"], j["yardsToGo"], j["quarter"]
    tercero_cuarto = down.isin([3, 4])
    j["decisivo"] = tercero_cuarto
    j["pocas_yardas"] = tercero_cuarto & (ytg <= 3)
    j["reloj_final"] = (j["reloj_seg"] <= 120) & q.isin([2, 4])
    j["marcador_cerrado"] = (q == 4) & (j["dif_marcador"].abs() <= 8)
    j["normal"] = down.isin([1, 2])
    j["convirtio"] = j["playResult"] >= ytg

    # tiempos desde el snap (s) y cuadro de cierre de la jugada
    fin = j["frame_lanza"].fillna(j["frame_sack"]).fillna(j["frame_ultimo"])
    j["frame_fin"] = fin.astype("Int32")
    snap = j["frame_snap"].astype("float64")
    for nombre, col in (("t_lanza", "frame_lanza"), ("t_sack", "frame_sack"),
                        ("t_ultimo", "frame_ultimo"), ("t_fin", "frame_fin")):
        j[nombre] = ((j[col].astype("float64") - snap) / FPS).astype("float32")

    for c in ("down", "quarter", "yardsToGo", "playResult"):
        j[c] = j[c].astype("int16")
    for c in ("possessionTeam", "defensiveTeam", "passResult", "pff_passCoverageType", "dropBackType"):
        j[c] = j[c].astype("category")
    j = j.drop(columns=["homeTeamAbbr", "visitorTeamAbbr", "preSnapHomeScore", "preSnapVisitorScore"])
    return j.sort_values(["gameId", "playId"]).reset_index(drop=True)
