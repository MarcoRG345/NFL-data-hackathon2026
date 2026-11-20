"""Giros por ruta y matriz ángulo × velocidad. DUEÑA: B. (Esqueleto: valores de mentira.)"""
import pandas as pd


def giro_por_cuadro(cuadros: pd.DataFrame) -> pd.DataFrame:
    """Conexión interna (la usa A en api/jugada para la flecha curva).

    "De mentira": devuelve la misma tabla con `giro_grados = 0.0` (positivo = a la derecha) y
    `girando = False`. B lo reemplaza por el cálculo real sin cambiar la firma.
    """
    salida = cuadros.copy()
    salida["giro_grados"] = 0.0
    salida["girando"] = False
    return salida


def _ic(centro: float, n: int) -> list[float] | None:
    if n < 20:
        return None
    ancho = round(6.0 / (n ** 0.5), 2)
    return [round(centro - ancho, 2), round(centro + ancho, 2)]


def resumen(filtro: str) -> dict:
    base = {"sin_giro": 0.4, "suave": 0.9, "brusco": 1.5}
    extra_franja = {"corta": 0.0, "media": 0.3, "larga": 0.6}
    ns = {"sin_giro": 210, "suave": 120, "brusco": 14}
    por_tipo = []
    for franja in ("corta", "media", "larga"):
        for tipo in ("sin_giro", "suave", "brusco"):
            n = ns[tipo] + (30 if franja == "media" else 0) - (60 if franja == "larga" and tipo != "sin_giro" else 0)
            n = max(n, 5)
            centro = round(base[tipo] + extra_franja[franja], 1)
            por_tipo.append({"franja": franja, "tipo": tipo, "n": n,
                             "sep_ganada": centro, "ic": _ic(centro, n)})
    matriz = []
    for a in range(6):
        for v in range(5):
            n = 40 + 12 * (5 - a) - 5 * v
            matriz.append({"angulo_bin": a, "vel_bin": v, "n": n,
                           "pct_gana_carrera": round(34.0 + 3.5 * a + 2.0 * (4 - v), 1)})
    return {
        "filtro": filtro, "n": sum(p["n"] for p in por_tipo), "por_tipo": por_tipo, "matriz": matriz,
        "insight": "(Ejemplo, datos de mentira) Un giro brusco gana más separación que una ruta recta.",
    }
