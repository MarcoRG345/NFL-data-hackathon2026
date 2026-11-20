"""
Módulo de vuelo (ventaja al lanzar) - backend/calculos/vuelo.py
P3 revisado: Analiza separación del objetivo EN el lanzamiento
Usa la tabla base `objetivo` de A2.
"""
import pandas as pd
import numpy as np

from backend.config import (
    ABIERTO_YD,
    SEP_CERRADA_YD,
    TENDENCIA_UMBRAL_YD,
    BOOTSTRAP_REPS,
    BOOTSTRAP_SEMILLA,
    NIVEL_IC,
)
from backend.estado import estado

MIN_N_IC = 20


def construir(filtro: str = "decisivo") -> pd.DataFrame:
    """
    Construye tabla de ventaja al lanzar usando la tabla base `objetivo`
    
    Lee de estado.tablas["objetivo"] (ya tiene sep_lanza, sep_antes, tendencia)
    Guarda en estado.resultados["ventaja_al_lanzar"]
    
    Returns:
        DataFrame con: gameId, playId, objetivo_id, franja_sep, tendencia_cat, completo
    """
    objetivo = estado.tablas["objetivo"].copy()
    jugadas = estado.tablas["jugadas"].copy()
    
    # Solo objetivos válidos (identificados por texto)
    objetivo = objetivo[objetivo["valido"] == True].copy()
    
    # Merge con jugadas para obtener passResult
    objetivo = objetivo.merge(
        jugadas[["gameId", "playId", "passResult"]],
        on=["gameId", "playId"],
        how="left"
    )
    
    # Clasificar franja de separación al lanzar
    objetivo["franja_sep"] = pd.cut(
        objetivo["sep_lanza"],
        bins=[0, SEP_CERRADA_YD, ABIERTO_YD, float("inf")],
        labels=["cerrado", "disputado", "abierto"],
        include_lowest=True
    )
    
    # Clasificar tendencia
    objetivo["tendencia_cat"] = pd.cut(
        objetivo["tendencia"],
        bins=[-float("inf"), -TENDENCIA_UMBRAL_YD, TENDENCIA_UMBRAL_YD, float("inf")],
        labels=["cerrandose", "estable", "abriendose"]
    )
    
    # Completo
    objetivo["completo"] = (objetivo["passResult"] == "C")
    
    # Seleccionar columnas
    resultado = objetivo[[
        "gameId", "playId", "nflId_objetivo", "franja_sep", 
        "tendencia_cat", "completo", "sep_lanza"
    ]].copy()
    
    resultado = resultado.rename(columns={"nflId_objetivo": "objetivo_id"})
    
    # Guardar en estado
    estado.resultados["ventaja_al_lanzar"] = resultado
    
    return resultado


def sigue_libre_por_jugada(filtro: str = "decisivo") -> pd.DataFrame:
    """
    Devuelve para cada jugada si el objetivo está abierto al lanzar
    Función pública para la síntesis de A
    
    Returns:
        DataFrame con: gameId, playId, valido, sigue_libre
    """
    if "ventaja_al_lanzar" not in estado.resultados:
        construir(filtro)
    
    ventaja = estado.resultados["ventaja_al_lanzar"].copy()
    
    # sigue_libre = objetivo a >= ABIERTO_YD en el lanzamiento
    ventaja["sigue_libre"] = ventaja["sep_lanza"] >= ABIERTO_YD
    ventaja["valido"] = True
    
    return ventaja[["gameId", "playId", "valido", "sigue_libre"]]


def bootstrap_intervalo(data, reps=BOOTSTRAP_REPS, nivel=NIVEL_IC):
    """
    Calcula intervalo de confianza por bootstrap
    
    Args:
        data: array de valores (0 o 1 para porcentajes)
        reps: número de repeticiones
        nivel: nivel de confianza (0.90 para 90%)
    
    Returns:
        (bajo, alto) o (None, None) si n < MIN_N_IC
    """
    if len(data) < MIN_N_IC:
        return None, None
    
    np.random.seed(BOOTSTRAP_SEMILLA)
    
    # Bootstrap
    medias = []
    for _ in range(reps):
        muestra = np.random.choice(data, size=len(data), replace=True)
        medias.append(muestra.mean() * 100)  # convertir a %
    
    # Percentiles
    alpha = 1 - nivel
    bajo = np.percentile(medias, alpha/2 * 100)
    alto = np.percentile(medias, (1 - alpha/2) * 100)
    
    return bajo, alto


def resumen(filtro: str = "decisivo") -> dict:
    """
    Genera resumen de ventaja al lanzar
    
    Args:
        filtro: nombre del filtro (para metadata)
    
    Returns:
        dict con: filtro, n, n_aproximado, por_separacion, por_tendencia, insight
    """
    if "ventaja_al_lanzar" not in estado.resultados:
        construir(filtro)
    
    ventaja_df = estado.resultados["ventaja_al_lanzar"].copy()
    
    n_total = len(ventaja_df)
    n_aproximado = 0  # Ya no hay aproximados con la tabla objetivo
    
    # Por separación
    por_separacion = []
    for franja in ["cerrado", "disputado", "abierto"]:
        subset = ventaja_df[ventaja_df["franja_sep"] == franja]
        if len(subset) == 0:
            continue
        
        n = len(subset)
        completos = subset["completo"].astype(int)
        pct_completo = completos.mean() * 100
        
        ic_bajo, ic_alto = bootstrap_intervalo(completos.values)
        
        por_separacion.append({
            "franja": franja,
            "n": n,
            "pct_completo": round(pct_completo, 1) if not pd.isna(pct_completo) else None,
            "ic": [round(ic_bajo, 1), round(ic_alto, 1)] if ic_bajo is not None else None
        })
    
    # Por tendencia
    por_tendencia = []
    for tend in ["abriendose", "estable", "cerrandose"]:
        subset = ventaja_df[ventaja_df["tendencia_cat"] == tend]
        if len(subset) == 0:
            continue
        
        n = len(subset)
        completos = subset["completo"].astype(int)
        pct_completo = completos.mean() * 100
        
        ic_bajo, ic_alto = bootstrap_intervalo(completos.values)
        
        por_tendencia.append({
            "tendencia": tend,
            "n": n,
            "pct_completo": round(pct_completo, 1) if not pd.isna(pct_completo) else None,
            "ic": [round(ic_bajo, 1), round(ic_alto, 1)] if ic_bajo is not None else None
        })
    
    # Insight: comparar abierto vs cerrado y abriéndose vs cerrándose
    abierto_pct = next((x["pct_completo"] for x in por_separacion if x["franja"] == "abierto"), None)
    cerrado_pct = next((x["pct_completo"] for x in por_separacion if x["franja"] == "cerrado"), None)
    
    abriendose_pct = next((x["pct_completo"] for x in por_tendencia if x["tendencia"] == "abriendose"), None)
    cerrandose_pct = next((x["pct_completo"] for x in por_tendencia if x["tendencia"] == "cerrandose"), None)
    
    if abierto_pct is not None and cerrado_pct is not None:
        diff_sep = abierto_pct - cerrado_pct
    else:
        diff_sep = None
    
    if abriendose_pct is not None and cerrandose_pct is not None:
        diff_tend = abriendose_pct - cerrandose_pct
    else:
        diff_tend = None
    
    if diff_sep is not None and diff_tend is not None:
        insight = (f"La ventaja al lanzar predice conversión: +{diff_sep:.1f} puntos con objetivo abierto "
                  f"(>={ABIERTO_YD} yd); +{diff_tend:.1f} puntos abriéndose vs cerrándose.")
    elif diff_sep is not None:
        insight = f"Objetivo abierto (>={ABIERTO_YD} yd): +{diff_sep:.1f} puntos de conversión."
    elif diff_tend is not None:
        insight = f"Abriéndose vs cerrándose: +{diff_tend:.1f} puntos de conversión."
    else:
        insight = "Datos insuficientes para insight."
    
    return {
        "filtro": filtro,
        "n": n_total,
        "n_aproximado": n_aproximado,
        "por_separacion": por_separacion,
        "por_tendencia": por_tendencia,
        "insight": insight
    }
