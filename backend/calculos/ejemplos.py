"""Jugadas ejemplo y cuadros del replay. DUEÑA: A."""
import numpy as np
import pandas as pd

from backend.estado import estado
from backend.config import ABIERTO_YD, INICIO_LIBRE_SEG, RADIO_PRESION, FPS
from backend.columnas import ROLE_PASS, ROLE_PASS_ROUTE, ROLE_COVERAGE, ROLE_PASS_RUSH, TEAM_FOOTBALL
from . import giros, relojes

def jugadas_ejemplo() -> list[dict]:
    """Devuelve 3 jugadas reales: una gana receptor, una gana defensa/sack, una sin presión."""
    res_carrera = relojes.resultado_por_jugada()
    jugadas = estado.tablas["jugadas"]
    
    # Filtrar decisivo
    ids_decisivo = jugadas.loc[jugadas["decisivo"], ["gameId", "playId"]]
    res_decisivo = res_carrera.merge(ids_decisivo, on=["gameId", "playId"], how="inner")
    
    # Seleccionar una de cada tipo
    ejemplos = []
    
    # 1. Gana receptor
    gana_rec = res_decisivo[res_decisivo["resultado"] == "gana_receptor"]
    if len(gana_rec) > 0:
        fila = gana_rec.iloc[0]
        j = jugadas[(jugadas["gameId"] == fila["gameId"]) & (jugadas["playId"] == fila["playId"])].iloc[0]
        ejemplos.append({
            "id": f"rec-{fila['gameId']}-{fila['playId']}",
            "gameId": int(fila["gameId"]),
            "playId": int(fila["playId"]),
            "titulo": "Receptor gana la carrera",
            "ganador": "receptor",
            "situacion": f"{j['down']}.º y {j['yardsToGo']} · {j['quarter']}.º cuarto"
        })
    
    # 2. Gana defensa o sack
    gana_def = res_decisivo[res_decisivo["resultado"] == "gana_defensa"]
    if len(gana_def) > 0:
        fila = gana_def.iloc[0]
        j = jugadas[(jugadas["gameId"] == fila["gameId"]) & (jugadas["playId"] == fila["playId"])].iloc[0]
        ejemplos.append({
            "id": f"def-{fila['gameId']}-{fila['playId']}",
            "gameId": int(fila["gameId"]),
            "playId": int(fila["playId"]),
            "titulo": "Defensa gana la carrera",
            "ganador": "defensa",
            "situacion": f"{j['down']}.º y {j['yardsToGo']} · {j['quarter']}.º cuarto"
        })
    
    # 3. Sin presión (mapear a "receptor" para el esquema)
    sin_pres = res_decisivo[res_decisivo["resultado"] == "sin_presion"]
    if len(sin_pres) > 0:
        fila = sin_pres.iloc[0]
        j = jugadas[(jugadas["gameId"] == fila["gameId"]) & (jugadas["playId"] == fila["playId"])].iloc[0]
        ejemplos.append({
            "id": f"sin-{fila['gameId']}-{fila['playId']}",
            "gameId": int(fila["gameId"]),
            "playId": int(fila["playId"]),
            "titulo": "Sin presión sobre el QB",
            "ganador": "receptor",  # mapear a receptor para el esquema
            "situacion": f"{j['down']}.º y {j['yardsToGo']} · {j['quarter']}.º cuarto"
        })
    
    return ejemplos


def jugada(game_id: int, play_id: int) -> dict:
    """Devuelve detalles completos de una jugada con sus cuadros."""
    jugadas = estado.tablas["jugadas"]
    cuadros_completos = estado.tablas["cuadros"]
    sep_cuadros = estado.tablas["sep_cuadros"]
    presion = estado.tablas["presion"]
    res_carrera = relojes.resultado_por_jugada()
    
    # Buscar jugada
    j = jugadas[(jugadas["gameId"] == game_id) & (jugadas["playId"] == play_id)]
    if len(j) == 0:
        raise ValueError(f"Jugada no encontrada: gameId={game_id}, playId={play_id}")
    j = j.iloc[0]
    
    # Resultado de carrera
    res = res_carrera[(res_carrera["gameId"] == game_id) & (res_carrera["playId"] == play_id)]
    if len(res) > 0:
        res = res.iloc[0]
        t_libre = float(res["t_libre"]) if pd.notna(res["t_libre"]) else None
        ganador_val = str(res["resultado"])
        # Mapear a valores del esquema
        if ganador_val == "gana_receptor":
            ganador = "receptor"
        elif ganador_val == "gana_defensa":
            ganador = "defensa"
        else:
            ganador = "sin_presion"
        margen = float(res["margen"]) if pd.notna(res["margen"]) else None
    else:
        t_libre = None
        ganador = "sin_presion"
        margen = None
    
    # Presión
    pres = presion[(presion["gameId"] == game_id) & (presion["playId"] == play_id)]
    t_presion = float(pres.iloc[0]["t_presion"]) if len(pres) > 0 and pd.notna(pres.iloc[0]["t_presion"]) else None
    
    # Cuadros de la jugada
    cuadros_jug = cuadros_completos[(cuadros_completos["gameId"] == game_id) & 
                                     (cuadros_completos["playId"] == play_id)].copy()
    
    # Aplicar giros
    cuadros_jug = giros.giro_por_cuadro(cuadros_jug)
    
    # Separación por cuadro (máximo entre receptores)
    sep_jug = sep_cuadros[(sep_cuadros["gameId"] == game_id) & (sep_cuadros["playId"] == play_id)]
    sep_max_por_frame = sep_jug.groupby("frameId")["separacion"].max().reset_index()
    libre_por_frame = sep_jug.groupby("frameId")["libre"].any().reset_index()
    
    # Presión por cuadro
    frame_presion = int(pres.iloc[0]["frame_presion"]) if len(pres) > 0 and pd.notna(pres.iloc[0]["frame_presion"]) else None
    
    # Balón
    balon = cuadros_jug[cuadros_jug["team"] == TEAM_FOOTBALL].copy()
    frame_lanza = int(j["frame_lanza"]) if pd.notna(j["frame_lanza"]) else None
    frame_ultimo = int(j["frame_ultimo"])
    
    if frame_lanza:
        balon_lanza = balon[balon["frameId"] == frame_lanza]
        if len(balon_lanza) > 0:
            bl = balon_lanza.iloc[0]
            x_lanza, y_lanza = float(bl["x"]), float(bl["y"])
            t_lanza = float((frame_lanza - j["frame_snap"]) / FPS)
        else:
            x_lanza = y_lanza = t_lanza = None
    else:
        x_lanza = y_lanza = t_lanza = None
    
    balon_ultimo = balon[balon["frameId"] == frame_ultimo]
    if len(balon_ultimo) > 0:
        bu = balon_ultimo.iloc[0]
        x_llega, y_llega = float(bu["x"]), float(bu["y"])
        t_llega = float((frame_ultimo - j["frame_snap"]) / FPS)
    else:
        x_llega = y_llega = t_llega = None
    
    # Eventos
    eventos = [{"t": 0.0, "nombre": "Snap"}]
    if t_libre:
        eventos.append({"t": round(t_libre, 2), "nombre": "Receptor libre"})
    if t_presion:
        eventos.append({"t": round(t_presion, 2), "nombre": "Presión"})
    if t_lanza:
        eventos.append({"t": round(t_lanza, 2), "nombre": "Pase"})
    eventos.sort(key=lambda e: e["t"])
    
    # Construir cuadros
    cuadros_out = []
    frames = sorted(cuadros_jug["frameId"].unique())
    for frame_id in frames:
        t = float((frame_id - j["frame_snap"]) / FPS)
        frame_data = cuadros_jug[cuadros_jug["frameId"] == frame_id]
        
        # Separación
        sep_frame = sep_max_por_frame[sep_max_por_frame["frameId"] == frame_id]
        separacion = float(sep_frame.iloc[0]["separacion"]) if len(sep_frame) > 0 else None
        
        libre_frame = libre_por_frame[libre_por_frame["frameId"] == frame_id]
        receptor_libre = bool(libre_frame.iloc[0]["libre"]) if len(libre_frame) > 0 else False
        
        presion_llego = frame_presion is not None and frame_id >= frame_presion
        
        # Balón
        balon_frame = frame_data[frame_data["team"] == TEAM_FOOTBALL]
        if len(balon_frame) > 0:
            bf = balon_frame.iloc[0]
            balon_dict = {"x": round(float(bf["x"]), 1), "y": round(float(bf["y"]), 1), "altura": 0.0}
            if frame_lanza and frame_id > frame_lanza:
                frac = (frame_id - frame_lanza) / max(1, frame_ultimo - frame_lanza)
                balon_dict["altura"] = round(float(np.sin(np.pi * min(1.0, frac))), 2)
        else:
            balon_dict = {"x": 0.0, "y": 0.0, "altura": 0.0}
        
        # Jugadores
        jugadores = []
        for _, p in frame_data[frame_data["team"] != TEAM_FOOTBALL].iterrows():
            rol_str = str(p["pff_role"])
            if rol_str == ROLE_PASS:
                rol = "qb"
            elif rol_str == ROLE_PASS_ROUTE:
                rol = "receptor"
            elif rol_str == ROLE_COVERAGE:
                rol = "defensor"
            elif rol_str == ROLE_PASS_RUSH:
                rol = "rusher"
            else:
                rol = "otro"
            
            lado = "ataque" if str(p["team"]) == str(j["possessionTeam"]) else "defensa"
            
            jugadores.append({
                "nflId": int(p["nflId"]),
                "x": round(float(p["x"]), 1),
                "y": round(float(p["y"]), 1),
                "s": round(float(p["s"]), 1),
                "dir": round(float(p["dir"]), 1),
                "giro_grados": round(float(p.get("giro_grados", 0.0)), 1),
                "girando": bool(p.get("girando", False)),
                "lado": lado,
                "jersey": int(p["jerseyNumber"]) if pd.notna(p.get("jerseyNumber")) else None,
                "posicion": rol,
                "rol": rol
            })
        
        cuadros_out.append({
            "t": round(t, 2),
            "separacion": round(separacion, 1) if separacion is not None else None,
            "receptor_libre": receptor_libre,
            "presion_llego": presion_llego,
            "balon": balon_dict,
            "jugadores": jugadores
        })
    
    # Contexto
    marcador = f"{j['possessionTeam']} {j['pts_ataque']} - {j['defensiveTeam']} {j['pts_defensa']}"
    contexto = {
        "down": int(j["down"]),
        "yardsToGo": int(j["yardsToGo"]),
        "cuarto": int(j["quarter"]),
        "reloj": str(j["gameClock"]),
        "marcador_texto": marcador,
        "descripcion": str(j["playDescription"])[:100],
        "resultado": str(j["passResult"]) if pd.notna(j["passResult"]) else ""
    }
    
    return {
        "contexto": contexto,
        "linea_golpeo": round(float(j["linea_golpeo"]), 1),
        "linea_primer_down": round(float(j["linea_golpeo"] + j["yardsToGo"]), 1),
        "relojes": {
            "t_presion": round(t_presion, 2) if t_presion else None,
            "t_libre": round(t_libre, 2) if t_libre else None,
            "ganador": ganador,
            "margen": round(margen, 2) if margen else None
        },
        "balon": {
            "t_lanza": round(t_lanza, 2) if t_lanza else None,
            "t_llega": round(t_llega, 2) if t_llega else None,
            "x_lanza": round(x_lanza, 1) if x_lanza else None,
            "y_lanza": round(y_lanza, 1) if y_lanza else None,
            "x_llega": round(x_llega, 1) if x_llega else None,
            "y_llega": round(y_llega, 1) if y_llega else None
        },
        "eventos": eventos,
        "cuadros": cuadros_out
    }
