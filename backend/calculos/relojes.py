"""Relojes y carrera. DUEÑA: A."""
import numpy as np
import pandas as pd

from backend.config import ABIERTO_YD, BOOTSTRAP_REPS, BOOTSTRAP_SEMILLA, INICIO_LIBRE_SEG, NIVEL_IC
from backend.estado import estado

COLUMNAS_RESULTADO = ["gameId", "playId", "t_libre", "t_presion", "resultado", "margen", "sack_con_libre"]
MIN_N_IC = 20


def _construir_resultado() -> pd.DataFrame:
    """Construye tabla con resultado de carrera por jugada."""
    jugadas = estado.tablas["jugadas"].copy()
    presion = estado.tablas["presion"].copy()
    sep_cuadros = estado.tablas["sep_cuadros"].copy()
    
    # t_presion desde tabla presion
    res = jugadas[["gameId", "playId"]].merge(
        presion[["gameId", "playId", "t_presion", "por_sack"]],
        on=["gameId", "playId"],
        how="left"
    )
    
    # t_libre: primer cuadro desde INICIO_LIBRE_SEG con algún receptor libre
    # La columna "libre" ya garantiza t >= INICIO_LIBRE_SEG, así que t_libre nunca es < 1.0s
    libre = sep_cuadros[sep_cuadros["libre"] == True].copy()
    t_libre = libre.groupby(["gameId", "playId"])["t"].min().reset_index().rename(columns={"t": "t_libre"})
    # Validación: t_libre debe ser >= INICIO_LIBRE_SEG
    assert (t_libre["t_libre"] >= INICIO_LIBRE_SEG).all(), f"Hay t_libre < {INICIO_LIBRE_SEG}: {t_libre[t_libre['t_libre'] < INICIO_LIBRE_SEG]}"
    res = res.merge(t_libre, on=["gameId", "playId"], how="left")
    
    # resultado de la carrera
    tiene_libre = res["t_libre"].notna()
    tiene_presion = res["t_presion"].notna()
    gana_receptor = tiene_libre & tiene_presion & (res["t_libre"] < res["t_presion"])
    gana_defensa = tiene_presion & ~(tiene_libre & (res["t_libre"] < res["t_presion"]))
    sin_presion = ~tiene_presion
    
    res["resultado"] = "sin_presion"
    res.loc[gana_receptor, "resultado"] = "gana_receptor"
    res.loc[gana_defensa, "resultado"] = "gana_defensa"
    res["resultado"] = res["resultado"].astype("category")
    
    # margen = t_presion - t_libre (puede ser NaN)
    res["margen"] = (res["t_presion"] - res["t_libre"]).astype("float32")
    
    # sack_con_libre: hubo sack y había receptor libre antes
    res["sack_con_libre"] = res["por_sack"] & tiene_libre
    
    return res[COLUMNAS_RESULTADO]


def resultado_por_jugada() -> pd.DataFrame:
    """Conexión interna (la usa B en api/ticker).

    Valores reales: resultado en {gana_receptor, gana_defensa, sin_presion};
    margen = t_presion - t_libre (s); sack_con_libre (bool).
    """
    if "resultado_carrera" not in estado.resultados:
        estado.resultados["resultado_carrera"] = _construir_resultado()
    return estado.resultados["resultado_carrera"]


def n_filtro(filtro: str) -> int:
    jugadas = estado.tablas["jugadas"]
    return int(jugadas[filtro].sum())


def resultado(filtro: str) -> dict:
    """Endpoint api/carrera/resultado con datos reales."""
    MIN_N = 20
    jugadas = estado.tablas["jugadas"]
    res = resultado_por_jugada()
    
    # filtrar jugadas
    ids = jugadas.loc[jugadas[filtro], ["gameId", "playId"]]
    res_filtro = res.merge(ids, on=["gameId", "playId"], how="inner")
    
    n = len(res_filtro)
    if n == 0:
        return {
            "filtro": filtro, "n": 0,
            "pct_gana_receptor": None, "pct_gana_defensa": None,
            "pct_sin_presion": None, "pct_sack_con_libre": None,
        }
    
    # contar resultados
    counts = res_filtro["resultado"].value_counts()
    n_receptor = counts.get("gana_receptor", 0)
    n_defensa = counts.get("gana_defensa", 0)
    n_sin = counts.get("sin_presion", 0)
    n_sack = res_filtro["sack_con_libre"].sum()
    
    # Aplicar umbral MIN_N para porcentajes
    pct_receptor = round(100.0 * n_receptor / n, 1) if n >= MIN_N else None
    pct_defensa = round(100.0 * n_defensa / n, 1) if n >= MIN_N else None
    pct_sin = round(100.0 * n_sin / n, 1) if n >= MIN_N else None
    pct_sack = round(100.0 * n_sack / n, 1) if n >= MIN_N else None
    
    return {
        "filtro": filtro, "n": n,
        "pct_gana_receptor": pct_receptor,
        "pct_gana_defensa": pct_defensa,
        "pct_sin_presion": pct_sin,
        "pct_sack_con_libre": pct_sack,
    }


def _mediana_curva(puntos: list[dict], campo: str, min_t: float = 0.0) -> float | None:
    """Primer t (interpolado, 2 decimales) en que la curva llega a 50 %.
    
    Si min_t > 0, no interpola antes de ese tiempo (devuelve exactamente min_t si
    la curva ya está >= 50% en ese punto).
    """
    for a, b in zip(puntos, puntos[1:]):
        # Si ya llegó a 50% antes de min_t, devolver min_t
        if min_t > 0 and a["t"] < min_t and b["t"] >= min_t and b[campo] >= 50:
            return round(min_t, 2)
        
        # Interpolación normal
        if a[campo] < 50 <= b[campo] and a["t"] >= min_t:
            frac = (50 - a[campo]) / (b[campo] - a[campo])
            return round(a["t"] + frac * (b["t"] - a["t"]), 2)
    return None


def curvas(filtro: str) -> dict:
    """Endpoint api/carrera/curvas con datos reales."""
    jugadas = estado.tablas["jugadas"]
    sep_cuadros = estado.tablas["sep_cuadros"].copy()
    presion = estado.tablas["presion"].copy()
    
    # filtrar jugadas
    ids = jugadas.loc[jugadas[filtro], ["gameId", "playId"]]
    n = len(ids)
    
    if n == 0:
        return {
            "filtro": filtro, "n": 0, "puntos": [],
            "mediana_libre": None, "mediana_presion": None, "ventaja": None,
        }
    
    # curva de t_libre: % de jugadas con receptor libre en cada momento
    sep_filt = sep_cuadros.merge(ids, on=["gameId", "playId"], how="inner")
    libre_por_jugada = sep_filt[sep_filt["libre"]].groupby(["gameId", "playId"])["t"].min().reset_index()
    
    # curva de t_presion: % de jugadas con presión en cada momento
    presion_filt = presion.merge(ids, on=["gameId", "playId"], how="inner")
    presion_filt = presion_filt[presion_filt["t_presion"].notna()]
    
    # generar puntos cada 0.1 s de 0 a 4
    puntos = []
    for i in range(41):
        t = round(i * 0.1, 1)
        n_libre = (libre_por_jugada["t"] <= t).sum() if len(libre_por_jugada) > 0 else 0
        n_presion = (presion_filt["t_presion"] <= t).sum() if len(presion_filt) > 0 else 0
        pct_libre = round(100.0 * n_libre / n, 1)
        pct_presion = round(100.0 * n_presion / n, 1)
        puntos.append({"t": t, "pct_libre": pct_libre, "pct_presion": pct_presion})
    
    # medianas (primer t donde la curva llega a 50%)
    # Para t_libre, no interpolar antes de INICIO_LIBRE_SEG
    m_libre = _mediana_curva(puntos, "pct_libre", min_t=INICIO_LIBRE_SEG)
    m_presion = _mediana_curva(puntos, "pct_presion")
    ventaja = round(m_presion - m_libre, 2) if m_libre is not None and m_presion is not None else None
    
    return {
        "filtro": filtro, "n": n, "puntos": puntos,
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
