"""Verifica estado y forma de cada endpoint del contrato (solo biblioteca estándar).
Uso: python scratch/verifica_esqueleto.py [--base http://127.0.0.1:8000/] [--esperar 60]"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.request

LENTO_MS = 300
resultados = []  # (ok, nombre, detalle)


def pedir(base, ruta):
    """Devuelve (status, cuerpo_json_o_None, ms)."""
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(base + ruta, timeout=30) as r:
            cuerpo, st = r.read(), r.status
    except urllib.error.HTTPError as e:
        cuerpo, st = e.read(), e.code
    ms = (time.perf_counter() - t0) * 1000
    try:
        return st, json.loads(cuerpo), ms
    except Exception:
        return st, None, ms


def reg(ok, nombre, detalle=""):
    resultados.append(ok)
    print(f"{'OK   ' if ok else 'FALLA'} {nombre}" + (f"  [{detalle}]" if detalle else ""))


# ---- formas esperadas (de contrato-api.md): dict = claves exactas; [x] = lista de x; None = cualquier valor
FORMAS = {
    "resumen": {"filtro": None, "vista": None, "n": None,
                "kpis": {k: None for k in ["pct_gana_receptor", "pct_gana_defensa", "conv_gana_receptor",
                                            "conv_gana_defensa", "reloj_defensa_mediana", "conv_equipo",
                                            "eslabon_equipo"]},
                "cadena_liga": [{"paso": None, "pct": None}], "insight": None},
    "curvas": {"filtro": None, "n": None, "puntos": [{"t": None, "pct_libre": None, "pct_presion": None}],
               "mediana_libre": None, "mediana_presion": None, "ventaja": None},
    "distancia": {"filtro": None, "grupos": [{k: None for k in
                  ["grupo", "n", "conv_gana", "conv_pierde", "ic_gana", "ic_pierde"]}]},
    "resultado": {k: None for k in ["filtro", "n", "pct_gana_receptor", "pct_gana_defensa",
                                    "pct_sin_presion", "pct_sack_con_libre"]},
    "equipos": {"filtro": None, "vista": None,
                "medianas": {k: None for k in ["t_presion", "p1", "p2", "p3", "conv"]},
                "equipos": [{k: None for k in ["equipo", "n", "t_presion_mediana", "p2_se_libera",
                                               "p1_gana_carrera", "p3_sigue_libre", "conv", "cadena",
                                               "eslabon", "cuadrante"]}]},
    "ejemplos": [{k: None for k in ["id", "gameId", "playId", "titulo", "ganador", "situacion"]}],
    "jugada": {
        "contexto": {k: None for k in ["down", "yardsToGo", "cuarto", "reloj", "marcador_texto",
                                       "descripcion", "resultado"]},
        "linea_golpeo": None, "linea_primer_down": None,
        "relojes": {k: None for k in ["t_presion", "t_libre", "ganador", "margen"]},
        "balon": {k: None for k in ["t_lanza", "t_llega", "x_lanza", "y_lanza", "x_llega", "y_llega"]},
        "eventos": [{"t": None, "nombre": None}],
        "cuadros": [{"t": None, "separacion": None, "receptor_libre": None, "presion_llego": None,
                     "balon": {"x": None, "y": None, "altura": None},
                     "jugadores": [{k: None for k in ["nflId", "x", "y", "s", "dir", "giro_grados", "girando",
                                                      "lado", "jersey", "posicion", "rol"]}]}]},
    "ticker": [{"texto": None, "tipo": None}],
    "giros": {"filtro": None, "n": None,
              "por_tipo": [{k: None for k in ["franja", "tipo", "n", "sep_ganada", "ic"]}],
              "matriz": [{k: None for k in ["angulo_bin", "vel_bin", "n", "pct_gana_carrera"]}],
              "insight": None},
    "vuelo": {"filtro": None, "n": None, "n_aproximado": None,
              "por_separacion": [{k: None for k in ["franja", "n", "pct_completo", "ic"]}],
              "por_tendencia": [{k: None for k in ["tendencia", "n", "pct_completo", "ic"]}],
              "insight": None},
    "mapa": {"capa": None, "modo": None, "n": None, "tam_celda": None, "x_min": None, "x_max": None,
             "celdas": [{k: None for k in ["col", "fila", "x0", "x1", "y0", "y1", "n", "valor", "valor_norm"]}],
             "escala": {"min": None, "max": None, "unidad": None}},
}


def claves(obj, forma, ruta="$"):
    """Lista de diferencias de claves (faltantes/extras). Revisa todos los elementos de cada lista."""
    errs = []
    if isinstance(forma, dict):
        if not isinstance(obj, dict):
            return [f"{ruta}: se esperaba objeto"]
        falt, extra = set(forma) - set(obj), set(obj) - set(forma)
        if falt:
            errs.append(f"{ruta}: faltan {sorted(falt)}")
        if extra:
            errs.append(f"{ruta}: sobran {sorted(extra)}")
        for k, sub in forma.items():
            if sub is not None and k in obj:
                errs += claves(obj[k], sub, f"{ruta}.{k}")
    elif isinstance(forma, list):
        if not isinstance(obj, list):
            return [f"{ruta}: se esperaba lista"]
        for i, el in enumerate(obj):
            errs += claves(el, forma[0], f"{ruta}[{i}]")
            if len(errs) > 5:
                break
    return errs


def prueba_endpoint(base, nombre, ruta, forma, reglas=None, lentos=None):
    st, js, ms = pedir(base, ruta)
    if lentos is not None and ms >= LENTO_MS:
        lentos.append((ruta, ms))
    if st != 200:
        reg(False, f"{ruta} -> forma", f"status {st} {js}")
        return js
    errs = claves(js, FORMAS[forma])
    reg(not errs, f"{ruta} -> claves exactas", "; ".join(errs[:5]) + f" {ms:.0f} ms" if errs else f"{ms:.0f} ms")
    if reglas and not errs:
        for desc, fn in reglas:
            try:
                ok, det = fn(js)
            except Exception as e:  # noqa: BLE001
                ok, det = False, repr(e)
            reg(ok, f"{ruta} -> {desc}", det)
    return js


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8000/")
    ap.add_argument("--esperar", type=float, default=60)
    a = ap.parse_args()
    base = a.base if a.base.endswith("/") else a.base + "/"

    st, js, _ = pedir(base, "health")
    reg(st == 200 and js == {"status": "ok"}, "health", str(js))

    st, js, _ = pedir(base, "api/estado-datos")
    reg(st == 200 and isinstance(js, dict) and set(js) == {"listo", "cargando", "error", "semanas", "n_jugadas"},
        "api/estado-datos claves exactas", str(js))

    # Con listo=false, el 503 debe ser correcto
    t_ini = time.time()
    listo = bool(js and js.get("listo"))
    comprobado_503 = False
    while True:
        if not listo and not comprobado_503:
            st503, js503, _ = pedir(base, "api/resumen")
            reg(st503 == 503 and js503 == {"detalle": "cargando"}, "api/resumen con listo=false -> 503 {'detalle':'cargando'}",
                f"{st503} {js503}")
            comprobado_503 = True
        if listo or time.time() - t_ini >= a.esperar:
            break
        time.sleep(3)
        _, js, _ = pedir(base, "api/estado-datos")
        listo = bool(js and js.get("listo"))

    if not listo:
        print("\nNo se puso listo: solo se verificó el 503.")
        fin()
        return

    lentos = []
    P = lambda *args, **kw: prueba_endpoint(base, *args, lentos=lentos, **kw)  # noqa: E731

    P("resumen", "api/resumen", "resumen", reglas=[("cadena_liga 5 pasos", lambda j: (len(j["cadena_liga"]) == 5, str(len(j["cadena_liga"]))))])
    P("resumen_eq", "api/resumen?equipo=KC", "resumen")
    P("curvas", "api/carrera/curvas", "curvas", reglas=[
        ("41 puntos", lambda j: (len(j["puntos"]) == 41, str(len(j["puntos"])))),
        ("curvas no decrecientes", lambda j: (all(
            b["pct_libre"] >= a_["pct_libre"] and b["pct_presion"] >= a_["pct_presion"]
            for a_, b in zip(j["puntos"], j["puntos"][1:])), ""))])
    P("distancia", "api/carrera/distancia", "distancia", reglas=[("4 grupos", lambda j: (len(j["grupos"]) == 4, str(len(j["grupos"]))))])
    P("resultado", "api/carrera/resultado", "resultado", reglas=[
        ("suma 100 ± 0.1", lambda j: (abs(j["pct_gana_receptor"] + j["pct_gana_defensa"] + j["pct_sin_presion"] - 100) <= 0.1,
                                      str(j["pct_gana_receptor"] + j["pct_gana_defensa"] + j["pct_sin_presion"])))])

    def reglas_equipos(j):
        mal = [e["equipo"] for e in j["equipos"] if len(e["cadena"]) != 5]
        return (not mal, str(mal))

    def reglas_peq(j):
        mal = [e["equipo"] for e in j["equipos"] if e["n"] < 30 and (e["cuadrante"] != "Muestra pequeña" or e["eslabon"] != "—")]
        return (not mal, str(mal))
    P("equipos", "api/equipos", "equipos", reglas=[("cadena de 5 por equipo", reglas_equipos),
                                                   ("n<30 -> 'Muestra pequeña' y '—'", reglas_peq)])
    ej = P("ejemplos", "api/jugadas-ejemplo", "ejemplos", reglas=[("al menos 2", lambda j: (len(j) >= 2, str(len(j))))])

    if isinstance(ej, list) and ej:
        def reglas_j(j):
            return None
        P("jugada", f"api/jugada?gameId={ej[0]['gameId']}&playId={ej[0]['playId']}", "jugada", reglas=[
            ("≥ 35 cuadros", lambda j: (len(j["cuadros"]) >= 35, str(len(j["cuadros"])))),
            ("22 jugadores por cuadro", lambda j: (all(len(c["jugadores"]) == 22 for c in j["cuadros"]),
                                                   str({len(c["jugadores"]) for c in j["cuadros"]})))])
    else:
        reg(False, "api/jugada", "sin jugadas-ejemplo")

    P("ticker", "api/ticker", "ticker", reglas=[("8 a 10 items", lambda j: (8 <= len(j) <= 10, str(len(j))))])
    P("giros", "api/giros/resumen", "giros", reglas=[("matriz 30 celdas", lambda j: (len(j["matriz"]) == 30, str(len(j["matriz"]))))])
    P("vuelo", "api/vuelo/resumen", "vuelo", reglas=[
        ("3 franjas y 3 tendencias", lambda j: (len(j["por_separacion"]) == 3 and len(j["por_tendencia"]) == 3, ""))])
    for capa in ("giro", "vuelo"):
        P("mapa", f"api/mapa?capa={capa}", "mapa", reglas=[
            ("celdas n ≥ 5", lambda j: (all(c["n"] >= 5 for c in j["celdas"]), f"{len(j['celdas'])} celdas")),
            ("valor_norm en [0,1]", lambda j: (all(0 <= c["valor_norm"] <= 1 for c in j["celdas"]), ""))])

    # Errores
    st, js, _ = pedir(base, "api/resumen?filtro=zzz")
    reg(st == 422, "api/resumen?filtro=zzz -> 422", str(st))
    st, js, _ = pedir(base, "api/mapa")
    reg(st == 422, "api/mapa sin capa -> 422", str(st))
    st, js, _ = pedir(base, "api/resumen?equipo=XXX")
    reg(st == 404, "api/resumen?equipo=XXX -> 404", str(st))

    # Tiempos
    if lentos:
        for ruta, ms in lentos:
            reg(False, f"tiempo {ruta} < {LENTO_MS} ms", f"{ms:.0f} ms LENTO")
    else:
        reg(True, f"tiempo de todos los endpoints < {LENTO_MS} ms")
    fin()


def fin():
    fallas = resultados.count(False)
    print(f"\nTotal: {len(resultados)} pruebas, {len(resultados) - fallas} OK, {fallas} FALLA")
    sys.exit(1 if fallas else 0)


if __name__ == "__main__":
    main()
