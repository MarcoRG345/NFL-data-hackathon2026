"""Verificaciones 1-5 de la skill calculo-carrera + métricas de carga. Uso: DATOS_SEMANAS=1 .venv/bin/python scratch/prueba_base.py"""
import resource
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np
import pandas as pd

from backend.base import construir_tablas_base
from backend.config import DATOS_SEMANAS
from backend.data_loader import cargar_datos_base

pd.set_option("display.width", 250, "display.max_columns", 30, "display.max_colwidth", 120)
t0 = time.time()
datos = cargar_datos_base()
t1 = time.time()
construir_tablas_base(datos)
t2 = time.time()
print(f"\n=== TIEMPOS (semanas {DATOS_SEMANAS}) ===\ncarga {t1-t0:.1f} s | tablas base {t2-t1:.1f} s | total {t2-t0:.1f} s")
print(f"pico RSS: {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024:.0f} MB")
print("\n=== TABLAS ===")
for k in ("cuadros", "eventos", "jugadas", "sep_cuadros", "presion", "objetivo"):
    print(f"{k:12s} filas {len(datos[k]):>9,}  memoria {datos[k].memory_usage(deep=True).sum()/1e6:7.1f} MB")

J, S, P, O = datos["jugadas"], datos["sep_cuadros"], datos["presion"], datos["objetivo"]
C = datos["cuadros"]

print("\n=== V1 CONTEOS ===")
con_pase = J["passResult"].astype(str).isin(["C", "I"])
print("jugadas válidas:", len(J), "| decisivas:", int(J.decisivo.sum()), "| pocas_yardas:", int(J.pocas_yardas.sum()),
      "| reloj_final:", int(J.reloj_final.sum()), "| marcador_cerrado:", int(J.marcador_cerrado.sum()),
      "| normal:", int(J.normal.sum()))
print("con pase C/I:", int(con_pase.sum()), "| con lanzamiento:", int(J.frame_lanza.notna().sum()))
print("passResult:", J.passResult.value_counts().to_dict())
print("con presión (total):", int(P.t_presion.notna().sum()), "| por distancia:", int((P.fuente == "distancia").sum()),
      "| por sack:", int((P.fuente == "sack").sum()), "| ninguna:", int((P.fuente == "ninguna").sum()))
print("con objetivo válido:", int(O.valido.sum()), "de", len(O))
print("claves únicas jugadas/presion/objetivo:", J[["gameId", "playId"]].duplicated().sum(),
      P[["gameId", "playId"]].duplicated().sum(), O[["gameId", "playId"]].duplicated().sum(), "duplicados")
print("nulos en jugadas (down, reloj_seg, linea_golpeo, t_fin):", J[["down", "reloj_seg", "linea_golpeo", "t_fin"]].isna().sum().to_dict())
print("t_fin: min %.1f mediana %.1f max %.1f" % (J.t_fin.min(), J.t_fin.median(), J.t_fin.max()))

print("\n=== V2 pass_arrived ===")
print("pass_arrived no existe en estos datos (nota de pregunta.md): se recorta al ÚLTIMO cuadro y se mide en pass_forward.")
print(f"% jugadas con pass_forward/autoevent_passforward: {100*J.frame_lanza.notna().mean():.1f}% "
      f"| % de las C/I con lanzamiento: {100*J.loc[con_pase,'frame_lanza'].notna().mean():.1f}%")
print("segundos entre lanzamiento y último cuadro (mediana):", float(((J.frame_ultimo - J.frame_lanza) / 10).median()))

print("\n=== V3 SEPARACIÓN EN pass_forward (objetivo y cualquier receptor) ===")
print("sep_cuadros: min %.2f max %.2f nulos %d" % (S.separacion.min(), S.separacion.max(), S.separacion.isna().sum()))
print("negativos:", int((S.separacion < 0).sum()), "| > 40:", int((S.separacion > 40).sum()))
lz = J[["gameId", "playId", "frame_lanza"]].dropna().astype({"frame_lanza": "int32"})
s_lz = S.merge(lz, left_on=["gameId", "playId", "frameId"], right_on=["gameId", "playId", "frame_lanza"])
print("todos los receptores en pass_forward  (n=%d): p10 %.2f  mediana %.2f  p90 %.2f" % (
    len(s_lz), *s_lz.separacion.quantile([.1, .5, .9])))
o_ok = O[O.valido].sep_lanza.dropna()
print("receptor objetivo en pass_forward     (n=%d): p10 %.2f  mediana %.2f  p90 %.2f" % (
    len(o_ok), *o_ok.quantile([.1, .5, .9])))
print("receptores por jugada (mediana):", S.groupby(["gameId", "playId"]).nflId.nunique().median())
print("separación a t=0 (snap) mediana: %.2f" % S[S.t == 0].separacion.median())

print("\n=== V4 PRESIÓN vs PFF (pff_hurry/hit/sack de los Pass Rush) ===")
sc = datos["scouting"]
pr = sc[sc.pff_role == "Pass Rush"].copy()
pr["p"] = pr[["pff_hit", "pff_hurry", "pff_sack"]].fillna(0).sum(axis=1) > 0
pff = pr.groupby(["gameId", "playId"]).p.any().rename("pff").reset_index()
m = J[["gameId", "playId"]].merge(pff, how="left").merge(P[["gameId", "playId", "t_presion", "fuente"]])
m["pff"] = m.pff.fillna(False)
m["mia"] = m.t_presion.notna()
m["mia_dist"] = m.fuente == "distancia"
for nombre, col in (("distancia o sack", "mia"), ("solo distancia", "mia_dist")):
    tp = int((m.pff & m[col]).sum())
    print(f"{nombre:17s}: PFF presión {int(m.pff.sum())} | mía {int(m[col].sum())} | ambos {tp} | "
          f"detecta {100*tp/m.pff.sum():.1f}% de PFF | {100*tp/m[col].sum():.1f}% de las mías son PFF | "
          f"acuerdo global (ambos o ninguno) {100*(m.pff == m[col]).mean():.1f}%")
for r in (1.5, 3.0):
    from backend.base.presion import calcular_presion
    pp = calcular_presion(C, J, r)
    print(f"radio {r}: con presión {100*pp.t_presion.notna().mean():.1f}% (por distancia {100*(pp.fuente=='distancia').mean():.1f}%)")
print("t_presion (por distancia): p10 %.2f mediana %.2f p90 %.2f" % tuple(P[P.fuente == "distancia"].t_presion.quantile([.1, .5, .9])))
print("%% presión: por distancia %.1f | por sack %.1f | sin presión %.1f" % tuple(
    100 * (P.fuente == f).mean() for f in ("distancia", "sack", "ninguna")))

print("\n=== V5 OBJETIVO ===")
print("método: " + " | ".join(f"{k} {100*v:.1f}%" for k, v in O.metodo.value_counts(normalize=True).items()), f"(n={len(O)})")
print("distancia al balón del objetivo por texto (mediana): %.2f yd" % O[O.metodo == "texto"].dist_balon.median())
O2 = O.merge(J[["gameId", "playId", "playDescription", "passResult"]]).merge(
    datos["players"][["nflId", "displayName"]].rename(columns={"nflId": "nflId_objetivo"}), how="left")
# muestra de 20 al azar con texto: nombre del texto vs displayName elegido
conn = O2[O2.metodo == "texto"].sample(20, random_state=7)
print("20 al azar con método texto:")
ok = 0
for _, r in conn.iterrows():
    ap = str(r.playDescription).split(" to ")[1].split(" ")[0].rstrip(".,") if " to " in str(r.playDescription) else "?"
    ult = ap.split(".")[-1].lower()[:4]
    bien = ult[:3] in str(r.displayName).lower().replace(" ", "")
    ok += bien
    print(f"  {'OK ' if bien else 'MAL'} {r.displayName:25s} <- {r.playDescription[:95]}")
print(f"coincidencia en la muestra: {ok}/20 = {100*ok/20:.0f}%")
print("\nMuestra de 5 filas de objetivo vs playDescription (aleatoria, mezcla de métodos):")
for _, r in O2.sample(5, random_state=3).iterrows():
    print(f"  metodo={r.metodo} aprox={r.aproximado} valido={r.valido} objetivo={r.displayName} dist_balon={r.dist_balon} "
          f"sep_lanza={r.sep_lanza} sep_antes={r.sep_antes}\n    -> {r.playDescription}")
# validación independiente del texto: ¿el objetivo "texto" es de los más cercanos al balón en el último cuadro?
print("\n%% de 'texto' cuyo objetivo está a <=3 yd del balón en el último cuadro: %.1f%%" % (
    100 * (O[O.metodo == "texto"].dist_balon <= 3).mean()))
print("sep_lanza nulos entre válidos: %d de %d" % (O[O.valido].sep_lanza.isna().sum(), int(O.valido.sum())))
print("tendencia: p10 %.2f mediana %.2f p90 %.2f" % tuple(O.tendencia.dropna().quantile([.1, .5, .9])))
print("\npico RSS final: %.0f MB" % (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024))
