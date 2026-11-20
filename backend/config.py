"""
Configuración global del proyecto.
"""
import os
from pathlib import Path

# ============================================================================
# RUTAS
# ============================================================================
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# ============================================================================
# SEMANAS A CARGAR
# ============================================================================
def parsear_semanas(s: str) -> list[int]:
    """
    Parsea DATOS_SEMANAS desde el entorno.
    
    Acepta:
    - "1" → [1]
    - "1-8" → [1, 2, 3, 4, 5, 6, 7, 8]
    - "1,3,5" → [1, 3, 5]
    
    Lanza ValueError si el formato no es válido.
    """
    s = s.strip()
    if not s:
        raise ValueError("DATOS_SEMANAS vacío")
    
    # Rango "1-8"
    if "-" in s:
        partes = s.split("-")
        if len(partes) != 2:
            raise ValueError(f"Formato de rango inválido: {s}")
        try:
            inicio = int(partes[0].strip())
            fin = int(partes[1].strip())
            return list(range(inicio, fin + 1))
        except ValueError:
            raise ValueError(f"Formato de rango inválido: {s}")
    
    # Lista "1,3,5"
    if "," in s:
        try:
            return [int(x.strip()) for x in s.split(",")]
        except ValueError:
            raise ValueError(f"Formato de lista inválido: {s}")
    
    # Un solo número "1"
    try:
        return [int(s)]
    except ValueError:
        raise ValueError(f"Formato inválido: {s}")


DATOS_SEMANAS = parsear_semanas(os.getenv("DATOS_SEMANAS", "1"))

# ============================================================================
# RUTAS DE TRACKING
# ============================================================================
# Un archivo por partido: data/tracking/tracking_<gameId>.csv. La semana sale de data/games.csv.
TRACKING_DIR = DATA_DIR / "tracking"

# ============================================================================
# CONSTANTES DEL PROYECTO (steering pregunta.md)
# ============================================================================
RADIO_PRESION = 2.0          # yd: un Pass Rush "llega" al QB a esta distancia o menos (robustez 1.5 y 3.0)
ABIERTO_YD = 3.0             # yd: receptor libre / abierto (robustez 2.0 y 4.0)
INICIO_LIBRE_SEG = 1.0       # s: "libre" solo cuenta desde 1.0 s tras el snap
GIRO_VENTANA_SEG = 0.5       # s: ventana del cambio de dir (robustez 0.3 y 0.7)
GIRO_SUAVE = 30.0            # grados
GIRO_BRUSCO = 60.0           # grados (robustez 45 y 90)
VEL_MIN_GIRO = 2.0           # yd/s antes y después del giro
RADIO_OBJETIVO = 3.0         # yd: solo para el respaldo del receptor objetivo
SEP_CERRADA_YD = 1.5         # yd: separación cerrada al lanzar
TENDENCIA_UMBRAL_YD = 0.5    # yd: abriéndose / cerrándose
MIN_N_EQUIPO = 30            # jugadas mínimas por equipo
BOOTSTRAP_REPS = 1000
BOOTSTRAP_SEMILLA = 42
NIVEL_IC = 0.90              # intervalos de 90%
FRANJAS = {"corta": (0.0, 5.0), "media": (5.0, 15.0), "larga": (15.0, float("inf"))}  # yd de profundidad

# ============================================================================
# CONSTANTES DE PROCESAMIENTO
# ============================================================================
FPS = 10  # frames por segundo en el tracking
