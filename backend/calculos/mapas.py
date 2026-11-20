"""Mapas de calor sobre la cancha. DUEÑA: B. (Esqueleto: valores de mentira, deterministas.)"""
import random

TAM_CELDA = 2.5
X_MIN = -15.0
X_MAX = 45.0
ANCHO_CANCHA = 53.3
MIN_N_CELDA = 5


def mapa(capa: str, modo: str, equipo: str | None) -> dict:
    rng = random.Random(f"{capa}|{modo}|{equipo}")
    n_cols = int((X_MAX - X_MIN) / TAM_CELDA)       # 24
    n_filas = int(-(-ANCHO_CANCHA // TAM_CELDA))    # 22
    vmin, vmax = (0.0, 4.0) if capa == "giro" else (1.0, 6.0)
    crudas = []
    for col in range(n_cols):
        for fila in range(n_filas):
            x0 = X_MIN + col * TAM_CELDA
            cercania = max(0.0, 1.0 - abs(x0 - 8.0) / 30.0)  # más jugadas cerca de la línea
            n = int(rng.random() * 40 * cercania + rng.random() * 3)
            if n < MIN_N_CELDA:
                continue
            crudas.append((col, fila, n, round(rng.uniform(vmin, vmax), 1)))
    celdas = []
    for col, fila, n, valor in crudas:
        x0 = round(X_MIN + col * TAM_CELDA, 1)
        y0 = round(fila * TAM_CELDA, 1)
        celdas.append({
            "col": col, "fila": fila, "x0": x0, "x1": round(x0 + TAM_CELDA, 1),
            "y0": y0, "y1": round(min(y0 + TAM_CELDA, ANCHO_CANCHA), 1), "n": n, "valor": valor,
            "valor_norm": round((valor - vmin) / (vmax - vmin), 3),
        })
    return {
        "capa": capa, "modo": modo, "n": sum(c["n"] for c in celdas),
        "tam_celda": TAM_CELDA, "x_min": X_MIN, "x_max": X_MAX, "celdas": celdas,
        "escala": {"min": vmin, "max": vmax, "unidad": "yd"},
    }
