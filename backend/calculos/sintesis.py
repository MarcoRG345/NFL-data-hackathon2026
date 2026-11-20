"""Cadena por equipo, cuadrante, KPIs del resumen. DUEÑA: A. (Esqueleto: valores de mentira.)"""
import random
import statistics

from ..estado import EQUIPOS
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
    res = relojes.resultado(filtro)
    cadena = [100.0, 68.4, 41.2, 27.5, 12.9]
    kpis = {
        "pct_gana_receptor": res["pct_gana_receptor"], "pct_gana_defensa": res["pct_gana_defensa"],
        "conv_gana_receptor": 46.8, "conv_gana_defensa": 27.3, "reloj_defensa_mediana": 2.71,
        "conv_equipo": None, "eslabon_equipo": None,
    }
    if equipo is not None:
        fila = next(f for f in equipos(filtro, vista)["equipos"] if f["equipo"] == equipo)
        kpis["conv_equipo"], kpis["eslabon_equipo"] = fila["conv"], fila["eslabon"]
    return {
        "filtro": filtro, "vista": vista, "n": res["n"], "kpis": kpis,
        "cadena_liga": [{"paso": p, "pct": c} for p, c in zip(_PASOS, cadena)],
        "insight": "(Ejemplo, datos de mentira) Cuando el receptor gana la carrera, la conversión sube casi 20 puntos.",
    }
