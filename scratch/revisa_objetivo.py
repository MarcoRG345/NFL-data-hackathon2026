"""Revisa los casos donde la descripción trae un nombre pero el método no fue 'texto'."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd

from backend.base import construir_tablas_base
from backend.data_loader import cargar_datos_base

pd.set_option("display.width", 250, "display.max_colwidth", 200)
d = construir_tablas_base(cargar_datos_base())
J, O = d["jugadas"], d["objetivo"]
m = O.merge(J[["gameId", "playId", "playDescription", "passResult"]])
print(m.metodo.value_counts(normalize=True).round(3).to_dict())
tiene = m.playDescription.str.contains(r"pass[^.]*? to ")
print("con nombre en texto:", int(tiene.sum()), "-> texto:", int((tiene & (m.metodo == "texto")).sum()))
print(m.loc[tiene & (m.metodo != "texto"), ["metodo", "playDescription"]].to_string())
print("sin nombre en texto:", m[~tiene].metodo.value_counts().to_dict())
