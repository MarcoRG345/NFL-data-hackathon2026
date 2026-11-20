"""Relojes y carrera. DUEÑA: A. (Esqueleto: valores de mentira, marcados como ejemplo.)"""
import pandas as pd

_N_BASE = {"decisivo": 1240, "pocas_yardas": 410, "reloj_final": 230, "marcador_cerrado": 360, "normal": 3100}

COLUMNAS_RESULTADO = ["gameId", "playId", "t_libre", "t_presion", "resultado", "margen", "sack_con_libre"]


def n_filtro(filtro: str) -> int:
    return _N_BASE[filtro]


def resultado_por_jugada() -> pd.DataFrame:
    """Conexión interna (la usa B en api/ticker).

    "De mentira" = DataFrame vacío con estas columnas; tratar como TODAS `sin_presion`
    (la cinta usa solo giro y aire). Valores reales: resultado en {gana_receptor, gana_defensa,
    sin_presion}; margen = t_presion - t_libre (s); sack_con_libre (bool).
    """
    return pd.DataFrame({
        "gameId": pd.Series(dtype="int64"),
        "playId": pd.Series(dtype="int64"),
        "t_libre": pd.Series(dtype="float64"),
        "t_presion": pd.Series(dtype="float64"),
        "resultado": pd.Series(dtype="object"),
        "margen": pd.Series(dtype="float64"),
        "sack_con_libre": pd.Series(dtype="bool"),
    }, columns=COLUMNAS_RESULTADO)


def resultado(filtro: str) -> dict:
    n = n_filtro(filtro)
    return {
        "filtro": filtro, "n": n,
        "pct_gana_receptor": 41.2, "pct_gana_defensa": 33.6,
        "pct_sin_presion": 25.2,  # 41.2 + 33.6 + 25.2 = 100
        "pct_sack_con_libre": 6.4,
    }


def _mediana_curva(puntos: list[dict], campo: str) -> float | None:
    """Primer t (interpolado, 2 decimales) en que la curva llega a 50 %."""
    for a, b in zip(puntos, puntos[1:]):
        if a[campo] < 50 <= b[campo]:
            frac = (50 - a[campo]) / (b[campo] - a[campo])
            return round(a["t"] + frac * (b["t"] - a["t"]), 2)
    return None


def curvas(filtro: str) -> dict:
    puntos = []
    for i in range(41):
        t = round(i * 0.1, 1)
        libre = 0.0 if t < 1.0 else min(72.0, 72.0 * (1 - 2.718281828 ** (-(t - 1.0) * 1.1)))
        presion = 0.0 if t < 1.2 else min(68.0, 68.0 * (1 - 2.718281828 ** (-(t - 1.2) * 0.9)))
        puntos.append({"t": t, "pct_libre": round(libre, 1), "pct_presion": round(presion, 1)})
    m_libre = _mediana_curva(puntos, "pct_libre")
    m_presion = _mediana_curva(puntos, "pct_presion")
    ventaja = round(m_presion - m_libre, 2) if m_libre is not None and m_presion is not None else None
    return {
        "filtro": filtro, "n": n_filtro(filtro), "puntos": puntos,
        "mediana_libre": m_libre, "mediana_presion": m_presion, "ventaja": ventaja,
    }


def distancia(filtro: str) -> dict:
    filas = [
        ("3.º y 1–3", 210, 58.1, 41.4, [52.0, 64.0], [34.8, 48.2]),
        ("3.º y 4–6", 260, 44.5, 31.0, [39.1, 50.0], [25.7, 36.5]),
        ("3.º y 7+", 330, 33.7, 19.2, [28.9, 38.6], [14.9, 23.6]),
        ("4.º down", 90, 49.0, 36.5, [40.2, 57.8], [28.0, 45.0]),
    ]
    return {"filtro": filtro, "grupos": [
        {"grupo": g, "n": n, "conv_gana": cg, "conv_pierde": cp, "ic_gana": icg, "ic_pierde": icp}
        for g, n, cg, cp, icg, icp in filas
    ]}
