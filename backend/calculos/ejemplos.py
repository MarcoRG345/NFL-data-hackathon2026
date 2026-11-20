"""Jugadas ejemplo y cuadros del replay. DUEÑA: A. (Esqueleto: jugada sintética, determinista.)

La jugada de mentira tiene 22 jugadores y 36 cuadros (0.0 a 3.5 s, cada 0.1 s). La línea de golpeo está en x = 50.
`separacion` de cada cuadro = la del receptor más libre (máximo, entre receptores, de la distancia al defensor
más cercano), calculada con las coordenadas ya redondeadas.
"""
import math
import random

import numpy as np
import pandas as pd

from . import giros

ABIERTO_YD = 3.0
INICIO_LIBRE_SEG = 1.0
RADIO_PRESION = 2.0
LOS = 50.0
T_LANZA = 3.0
T_FIN = 3.5

_EJEMPLOS = [
    {"id": "ejemplo-receptor", "gameId": 2022090800, "playId": 101, "ganador": "receptor",
     "titulo": "(Ejemplo) El receptor se libera antes de la presión",
     "situacion": "3.º y 6 · 2.º cuarto"},
    {"id": "ejemplo-defensa", "gameId": 2022091100, "playId": 202, "ganador": "defensa",
     "titulo": "(Ejemplo) La presión llega primero",
     "situacion": "3.º y 8 · 4.º cuarto"},
]


def jugadas_ejemplo() -> list[dict]:
    return [dict(e) for e in _EJEMPLOS]


def _ganador_pedido(game_id: int, play_id: int) -> str:
    for e in _EJEMPLOS:
        if e["gameId"] == game_id and e["playId"] == play_id:
            return e["ganador"]
    return "receptor"


# (nflId, jersey, posición, rol, lado, x0, y0)
def _plantilla() -> list[tuple]:
    j = []
    j.append((1001, 12, "QB", "qb", "ataque", 45.0, 26.7))
    j.append((1002, 28, "RB", "otro", "ataque", 44.0, 30.0))
    for k, y in enumerate((21.5, 24.0, 26.7, 29.4, 32.0)):
        j.append((1003 + k, 60 + k, "OL", "otro", "ataque", 49.0, y))
    for k, (pos, y) in enumerate((("WR", 40.0), ("WR", 12.0), ("WR", 20.0), ("TE", 33.5))):
        j.append((1008 + k, 80 + k, pos, "receptor", "ataque", 50.0, y))
    for k, y in enumerate((22.0, 25.5, 28.0, 31.5)):
        j.append((2001 + k, 90 + k, "DE" if k in (0, 3) else "DT", "rusher", "defensa", 51.5, y))
    for k, y in enumerate((20.0, 26.7, 33.0)):
        j.append((2005 + k, 50 + k, "LB", "otro", "defensa", 54.0, y))
    for k, y in enumerate((42.0, 14.0, 18.0, 35.0)):
        j.append((2008 + k, 20 + k, "CB" if k < 3 else "FS", "defensor", "defensa", 56.0, y))
    return j


def _trayectorias(ganador: str) -> dict[int, np.ndarray]:
    """Posiciones (x, y) sin redondear por jugador: arreglo (n_cuadros, 2)."""
    ts = np.round(np.arange(0, T_FIN + 1e-9, 0.1), 1)
    rng = random.Random(7)  # determinista
    t_p = 2.4 if ganador == "defensa" else 2.9
    pend = 1.2 if ganador == "defensa" else 2.5   # cuánto crece la separación del objetivo tras 1.0 s
    plantilla = _plantilla()
    pos: dict[int, np.ndarray] = {}
    qb = np.stack([45.0 - 4.0 * np.minimum(ts, 1.5) / 1.5, 26.7 + 0.0 * ts], axis=1)
    pos[1001] = qb
    receptores = [pf for pf in plantilla if pf[3] == "receptor"]
    rec_xy = {}
    for k, pf in enumerate(receptores):
        vx, vy = (7.5, -1.5) if k == 0 else (6.0 + k * 0.5, 0.8 * (-1) ** k)
        rec_xy[pf[0]] = np.stack([pf[5] + vx * ts, pf[6] + vy * ts], axis=1)
        pos[pf[0]] = rec_xy[pf[0]]
    defensores = [pf for pf in plantilla if pf[3] == "defensor"]
    direcciones = [(0.6, -0.8), (-0.6, 0.8), (0.0, 1.0), (0.8, 0.6)]
    for k, (pf, rec) in enumerate(zip(defensores, receptores)):
        if k == 0:
            brecha = 1.0 + pend * np.maximum(0.0, ts - INICIO_LIBRE_SEG)
        else:
            brecha = np.minimum(1.0 + 0.3 * ts, 2.4)
        dx, dy = direcciones[k]
        pos[pf[0]] = rec_xy[rec[0]] + brecha[:, None] * np.array([dx, dy])
    # rushers hacia el QB
    dir_ini = [(1.0, -0.35), (1.0, -0.1), (1.0, 0.1), (1.0, 0.35)]
    for k, pf in enumerate([p for p in plantilla if p[3] == "rusher"]):
        ux, uy = dir_ini[k]
        norma = math.hypot(ux, uy)
        ux, uy = ux / norma, uy / norma
        if k == 0:
            dist = np.maximum(1.0, 7.0 - (5.0 / t_p) * ts)
        else:
            dist = np.maximum(3.0, 8.5 - 1.2 * ts)
        pos[pf[0]] = qb + dist[:, None] * np.array([ux, uy])
    for pf in plantilla:
        if pf[0] not in pos:  # OL, RB, LB: casi quietos
            ruido = rng.uniform(-0.3, 0.3)
            pos[pf[0]] = np.stack([pf[5] + 0.0 * ts, pf[6] + ruido * np.minimum(ts, 1.0)], axis=1)
    return pos


def jugada(game_id: int, play_id: int) -> dict:
    ganador_pedido = _ganador_pedido(game_id, play_id)
    ts = np.round(np.arange(0, T_FIN + 1e-9, 0.1), 1)
    plantilla = _plantilla()
    pos = _trayectorias(ganador_pedido)

    # velocidades y rumbo (antes de redondear)
    filas = []
    for pf in plantilla:
        xy = pos[pf[0]]
        vel = np.gradient(xy, 0.1, axis=0)
        rapidez = np.hypot(vel[:, 0], vel[:, 1])
        rumbo = np.degrees(np.arctan2(vel[:, 0], vel[:, 1])) % 360.0
        for i, t in enumerate(ts):
            filas.append({"frame": i, "nflId": pf[0], "x": round(float(xy[i, 0]), 1),
                          "y": round(float(xy[i, 1]), 1), "s": round(float(rapidez[i]), 1),
                          "dir": round(float(rumbo[i]), 1), "lado": pf[4], "jersey": pf[1],
                          "posicion": pf[2], "rol": pf[3]})
    tabla = giros.giro_por_cuadro(pd.DataFrame(filas))  # conexión interna con B (0 / False mientras tanto)

    t_presion = t_libre = None
    cuadros = []
    balon_xy_lanza = None
    qb_x = qb_y = 0.0
    for i, t in enumerate(ts):
        t = float(t)
        sub = tabla[tabla["frame"] == i]
        rec = sub[sub["rol"] == "receptor"]
        dfn = sub[sub["rol"] == "defensor"]
        seps = []
        for _, r in rec.iterrows():
            seps.append(min(math.hypot(r["x"] - d["x"], r["y"] - d["y"]) for _, d in dfn.iterrows()))
        sep = round(max(seps), 1)
        libre = bool(sep >= ABIERTO_YD and t >= INICIO_LIBRE_SEG)
        qb = sub[sub["rol"] == "qb"].iloc[0]
        rushers = sub[sub["rol"] == "rusher"]
        presion = bool(any(math.hypot(r["x"] - qb["x"], r["y"] - qb["y"]) <= RADIO_PRESION
                           for _, r in rushers.iterrows()) and t > 0)
        if libre and t_libre is None:
            t_libre = round(t, 2)
        if presion and t_presion is None:
            t_presion = round(t, 2)
        if t <= T_LANZA:
            bx, by = float(qb["x"]), float(qb["y"])
            if abs(t - T_LANZA) < 1e-9:
                balon_xy_lanza = (bx, by)
            altura = 0.0
        else:
            frac = (t - T_LANZA) / (T_FIN - T_LANZA)
            fin = tabla[(tabla["frame"] == len(ts) - 1) & (tabla["nflId"] == 1008)].iloc[0]
            bx = balon_xy_lanza[0] + (float(fin["x"]) - balon_xy_lanza[0]) * frac
            by = balon_xy_lanza[1] + (float(fin["y"]) - balon_xy_lanza[1]) * frac
            altura = math.sin(math.pi * min(1.0, (t - T_LANZA) / 1.0))
        cuadros.append({
            "t": round(t, 2), "separacion": sep, "receptor_libre": libre, "presion_llego": presion,
            "balon": {"x": round(bx, 1), "y": round(by, 1), "altura": round(altura, 2)},
            "jugadores": [
                {"nflId": int(r["nflId"]), "x": float(r["x"]), "y": float(r["y"]), "s": float(r["s"]),
                 "dir": float(r["dir"]), "giro_grados": float(r["giro_grados"]), "girando": bool(r["girando"]),
                 "lado": r["lado"], "jersey": int(r["jersey"]), "posicion": r["posicion"], "rol": r["rol"]}
                for _, r in sub.iterrows()],
        })

    if t_presion is None:
        ganador = "sin_presion"
    elif t_libre is not None and t_libre < t_presion:
        ganador = "receptor"
    else:
        ganador = "defensa"
    margen = round(t_presion - t_libre, 2) if t_presion is not None and t_libre is not None else None
    ult = cuadros[-1]["balon"]
    eventos = [{"t": 0.0, "nombre": "Snap"}]
    if t_libre is not None:
        eventos.append({"t": t_libre, "nombre": "Receptor libre"})
    if t_presion is not None:
        eventos.append({"t": t_presion, "nombre": "Llega la presión"})
    eventos.append({"t": T_LANZA, "nombre": "Pase"})
    eventos.sort(key=lambda e: e["t"])
    return {
        "contexto": {
            "down": 3, "yardsToGo": 6, "cuarto": 2 if ganador == "receptor" else 4, "reloj": "04:12",
            "marcador_texto": "(Ejemplo) KC 17 - BUF 14",
            "descripcion": "(Ejemplo, jugada sintética) Pase corto por la derecha.",
            "resultado": "Pase completo, 9 yd" if ganador == "receptor" else "Pase incompleto",
        },
        "linea_golpeo": LOS, "linea_primer_down": LOS + 6.0,
        "relojes": {"t_presion": t_presion, "t_libre": t_libre, "ganador": ganador, "margen": margen},
        "balon": {"t_lanza": T_LANZA, "t_llega": cuadros[-1]["t"],
                  "x_lanza": round(balon_xy_lanza[0], 1), "y_lanza": round(balon_xy_lanza[1], 1),
                  "x_llega": ult["x"], "y_llega": ult["y"]},
        "eventos": eventos,
        "cuadros": cuadros,
    }
