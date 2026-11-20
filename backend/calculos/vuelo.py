"""Ventaja al lanzar (separación del objetivo en pass_forward y su tendencia). DUEÑA: B.
(Esqueleto: valores de mentira.) Nota: "vuelo" = ventaja al lanzar; no hay cuadros del balón en el aire."""
import pandas as pd


def sigue_libre_por_jugada() -> pd.DataFrame:
    """Conexión interna (la usa A en la cadena, paso P3).

    "De mentira": DataFrame VACÍO con gameId, playId, valido, sigue_libre
    (`sigue_libre` = abierto en el lanzamiento). Con la tabla vacía A usa la mediana de la liga para P3.
    """
    return pd.DataFrame({
        "gameId": pd.Series(dtype="int64"),
        "playId": pd.Series(dtype="int64"),
        "valido": pd.Series(dtype="bool"),
        "sigue_libre": pd.Series(dtype="bool"),
    }, columns=["gameId", "playId", "valido", "sigue_libre"])


def _ic(centro: float, n: int) -> list[float] | None:
    if n < 20:  # contrato: ic es null si n < 20
        return None
    ancho = round(45.0 / (n ** 0.5), 1)
    return [round(max(0.0, centro - ancho), 1), round(min(100.0, centro + ancho), 1)]


def resumen(filtro: str) -> dict:
    sep = [("cerrado", 140, 48.6), ("disputado", 230, 61.3), ("abierto", 310, 74.8)]
    ten = [("cerrandose", 180, 55.2), ("estable", 400, 64.9), ("abriendose", 12, 78.3)]
    return {
        "filtro": filtro, "n": 680, "n_aproximado": 37,
        "por_separacion": [{"franja": f, "n": n, "pct_completo": p, "ic": _ic(p, n)} for f, n, p in sep],
        "por_tendencia": [{"tendencia": t, "n": n, "pct_completo": p, "ic": _ic(p, n)} for t, n, p in ten],
        "insight": "(Ejemplo, datos de mentira) Con el objetivo abierto al lanzar se completan más pases.",
    }
