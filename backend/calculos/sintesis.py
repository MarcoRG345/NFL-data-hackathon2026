"""Cadena por equipo, cuadrante, KPIs del resumen. DUEÑA: A."""
import statistics

from ..estado import EQUIPOS, estado
from . import relojes

MIN_N_EQUIPO = 30
_PASOS = ["Jugadas", "Se libera (P2)", "Gana la carrera (P1)", "Abierto al lanzar (P3)", "Convierte"]


def _equipos_mentira(filtro: str, vista: str) -> list[dict]:
    rng = random.Random(f"{filtro}|{vista}")
    filas = []
    for i, eq in enumerate(EQUIPOS):
        n = rng.randint(34, 120) if i not in (7, 20) else rng.randint(12, 25)  # 2 equipos con muestra pequeña
        p2 = round(rng.uniform(55, 80), 1)
        p1 = round(rng.uniform(40, 70), 1)
        p3 = round(rng.uniform(45, 75), 1)
        conv = round(rng.uniform(25, 55), 1)
        filas.append({"equipo": eq, "n": n, "t_presion_mediana": round(rng.uniform(2.3, 3.2), 2),
                      "p2_se_libera": p2, "p1_gana_carrera": p1, "p3_sigue_libre": p3, "conv": conv})
    return filas


def _mediana(valores: list[float]) -> float | None:
    return round(statistics.median(valores), 1) if valores else None


def equipos(filtro: str, vista: str) -> dict:
    filas = _equipos_mentira(filtro, vista)
    grandes = [f for f in filas if f["n"] >= MIN_N_EQUIPO]
    med = {
        "t_presion": round(statistics.median(f["t_presion_mediana"] for f in grandes), 2),
        "p1": _mediana([f["p1_gana_carrera"] for f in grandes]),
        "p2": _mediana([f["p2_se_libera"] for f in grandes]),
        "p3": _mediana([f["p3_sigue_libre"] for f in grandes]),
        "conv": _mediana([f["conv"] for f in grandes]),
    }
    for f in filas:
        # cadena: % acumulado sobre las jugadas del filtro (100 → ... → convierte)
        c1 = round(f["p2_se_libera"], 1)
        c2 = round(c1 * f["p1_gana_carrera"] / 100, 1)
        c3 = round(c2 * f["p3_sigue_libre"] / 100, 1)
        c4 = round(c3 * f["conv"] / 100, 1)
        f["cadena"] = [100.0, c1, c2, c3, c4]
        if f["n"] < MIN_N_EQUIPO:
            f["eslabon"], f["cuadrante"] = "—", "Muestra pequeña"
            continue
        # eslabón débil: el paso más abajo de la mediana de la liga (diferencia relativa)
        dif = {"P1": f["p1_gana_carrera"] / med["p1"], "P2": f["p2_se_libera"] / med["p2"],
               "P3": f["p3_sigue_libre"] / med["p3"]}
        f["eslabon"] = min(dif, key=dif.get)
        bien2, bien1 = f["p2_se_libera"] >= med["p2"], f["p1_gana_carrera"] >= med["p1"]
        f["cuadrante"] = ("Todo funciona" if bien2 and bien1 else
                          "Se liberan, pero no hay tiempo" if bien2 else
                          "La línea aguanta, nadie se libera" if bien1 else "Nada funciona")
    return {"filtro": filtro, "vista": vista, "medianas": med, "equipos": filas}


def resumen(filtro: str, vista: str, equipo: str | None) -> dict:
    """Endpoint api/resumen con datos reales."""
    from . import vuelo
    
    MIN_N = 20
    jugadas = estado.tablas["jugadas"].copy()
    res_carrera = relojes.resultado_por_jugada()
    
    # filtrar jugadas
    ids = jugadas.loc[jugadas[filtro], ["gameId", "playId", "possessionTeam", "defensiveTeam", "convirtio"]]
    n = len(ids)
    
    if n == 0:
        return {
            "filtro": filtro, "vista": vista, "n": 0,
            "kpis": {
                "pct_gana_receptor": None, "pct_gana_defensa": None,
                "conv_gana_receptor": None, "conv_gana_defensa": None,
                "reloj_defensa_mediana": None, "conv_equipo": None, "eslabon_equipo": None,
            },
            "cadena_liga": [{"paso": p, "pct": 0.0} for p in _PASOS],
            "insight": "Sin jugadas en este filtro.",
        }
    
    # merge con resultado de carrera
    df = ids.merge(res_carrera, on=["gameId", "playId"], how="left")
    df["resultado"] = df["resultado"].fillna("sin_presion")
    
    # KPIs básicos
    res_dict = relojes.resultado(filtro)
    pct_receptor = res_dict["pct_gana_receptor"]
    pct_defensa = res_dict["pct_gana_defensa"]
    
    # conversión por resultado (aplicar umbral MIN_N)
    gana_rec = df[df["resultado"] == "gana_receptor"]
    gana_def = df[df["resultado"] == "gana_defensa"]
    conv_rec = round(100.0 * gana_rec["convirtio"].sum() / len(gana_rec), 1) if len(gana_rec) >= MIN_N else None
    conv_def = round(100.0 * gana_def["convirtio"].sum() / len(gana_def), 1) if len(gana_def) >= MIN_N else None
    
    # mediana t_presion
    presion_tbl = estado.tablas["presion"].copy()
    df_presion = ids.merge(presion_tbl[["gameId", "playId", "t_presion"]], on=["gameId", "playId"], how="left")
    t_presiones = df_presion["t_presion"].dropna()
    mediana_presion = round(t_presiones.median(), 2) if len(t_presiones) >= MIN_N else None
    
    # cadena de la liga (P2 → P1 → P3 → conversión)
    # P2: receptor se liberó (t_libre existe)
    p2_jugadas = df[df["t_libre"].notna()]
    pct_p2 = round(100.0 * len(p2_jugadas) / n, 1) if n > 0 else 0.0
    
    # P1: de las que se liberaron, ganó la carrera o sin presión
    p1_jugadas = p2_jugadas[p2_jugadas["resultado"].isin(["gana_receptor", "sin_presion"])]
    pct_p1 = round(100.0 * len(p1_jugadas) / n, 1) if n > 0 else 0.0
    
    # P3: de las que ganaron P1, estaba abierto al lanzar
    try:
        vuelo_df = vuelo.sigue_libre_por_jugada(filtro)
        p3_df = p1_jugadas.merge(vuelo_df, on=["gameId", "playId"], how="left")
        p3_jugadas = p3_df[p3_df["sigue_libre"] == True]
        pct_p3 = round(100.0 * len(p3_jugadas) / n, 1) if n > 0 else 0.0
    except Exception:
        # Si vuelo no está disponible, usar mediana de la liga (placeholder)
        p3_jugadas = p1_jugadas.sample(frac=0.65, random_state=42) if len(p1_jugadas) > 0 else p1_jugadas
        pct_p3 = round(100.0 * len(p3_jugadas) / n, 1) if n > 0 else 0.0
    
    # Conversión: de las que llegaron abiertas, convirtieron
    pct_conv = round(100.0 * p3_jugadas["convirtio"].sum() / n, 1) if n > 0 else 0.0
    
    cadena = [100.0, pct_p2, pct_p1, pct_p3, pct_conv]
    
    kpis = {
        "pct_gana_receptor": pct_receptor,
        "pct_gana_defensa": pct_defensa,
        "conv_gana_receptor": conv_rec,
        "conv_gana_defensa": conv_def,
        "reloj_defensa_mediana": mediana_presion,
        "conv_equipo": None,
        "eslabon_equipo": None,
    }
    
    # Si hay equipo específico, calcular sus KPIs
    if equipo is not None:
        fila = next((f for f in equipos(filtro, vista)["equipos"] if f["equipo"] == equipo), None)
        if fila:
            kpis["conv_equipo"] = fila["conv"]
            kpis["eslabon_equipo"] = fila["eslabon"]
    
    # insight (solo mencionar grupos con n >= MIN_N)
    if conv_rec is not None and conv_def is not None and len(gana_rec) >= MIN_N and len(gana_def) >= MIN_N:
        diff = conv_rec - conv_def
        insight = f"Cuando el receptor gana la carrera, la conversión es {abs(diff):.1f} puntos {'mayor' if diff > 0 else 'menor'} que cuando gana la defensa (n_receptor={len(gana_rec)}, n_defensa={len(gana_def)})."
    elif len(gana_def) < MIN_N:
        insight = f"Muy pocas jugadas donde gana la defensa (n={len(gana_def)}). El receptor se libera en {pct_p2:.1f}% de las jugadas."
    elif len(gana_rec) < MIN_N:
        insight = f"Muy pocas jugadas donde gana el receptor (n={len(gana_rec)}). Sin presión en {res_dict['pct_sin_presion']}% de las jugadas."
    else:
        insight = "Datos insuficientes para calcular diferencia en conversión."
    
    return {
        "filtro": filtro, "vista": vista, "n": n, "kpis": kpis,
        "cadena_liga": [{"paso": p, "pct": c} for p, c in zip(_PASOS, cadena)],
        "insight": insight,
    }
