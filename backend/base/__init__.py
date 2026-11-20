"""Tablas base compartidas. `construir_tablas_base(datos)` llena jugadas, sep_cuadros, presion y objetivo."""
import time

from backend.base.objetivo import construir_objetivo
from backend.base.presion import construir_presion
from backend.base.separacion import construir_sep_cuadros
from backend.base.situacion import construir_jugadas


def construir_tablas_base(datos: dict) -> dict:
    """Recibe el dict de la carga (o `estado.tablas`), agrega las 4 tablas base en él y lo devuelve."""
    t0 = time.time()
    datos["jugadas"] = construir_jugadas(datos["eventos"], datos["plays"], datos["games"])
    print(f"[base] jugadas: {len(datos['jugadas']):,} ({time.time() - t0:.1f} s)")
    datos["sep_cuadros"] = construir_sep_cuadros(datos["cuadros"], datos["jugadas"])
    print(f"[base] sep_cuadros: {len(datos['sep_cuadros']):,} ({time.time() - t0:.1f} s)")
    datos["presion"] = construir_presion(datos["cuadros"], datos["jugadas"])
    print(f"[base] presion: {len(datos['presion']):,} ({time.time() - t0:.1f} s)")
    datos["objetivo"] = construir_objetivo(datos["jugadas"], datos["cuadros"], datos["players"],
                                           datos["sep_cuadros"])
    print(f"[base] objetivo: {len(datos['objetivo']):,} ({time.time() - t0:.1f} s)")
    return datos
