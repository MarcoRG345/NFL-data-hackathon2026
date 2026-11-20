"""Estado global compartido (esqueleto). Lo leen los routers y lo escribe la carga en segundo plano.

`main.py` (hilo de carga) debe hacer, al arrancar: estado.cargando = True; al terminar:
estado.tablas[...] = ..., estado.semanas = N, estado.n_jugadas = N, estado.listo = True,
estado.cargando = False. Si falla: estado.error = "mensaje".
Por defecto `listo` es False: los endpoints responden 503 hasta que alguien lo ponga en True.
"""

# Las 32 abreviaturas de la liga (para validar el parámetro `equipo`).
EQUIPOS: list[str] = [
    "ARI", "ATL", "BAL", "BUF", "CAR", "CHI", "CIN", "CLE",
    "DAL", "DEN", "DET", "GB", "HOU", "IND", "JAX", "KC",
    "LA", "LAC", "LV", "MIA", "MIN", "NE", "NO", "NYG",
    "NYJ", "PHI", "PIT", "SEA", "SF", "TB", "TEN", "WAS",
]


class EstadoGlobal:
    def __init__(self) -> None:
        self.cargando: bool = False
        self.listo: bool = False
        self.error: str | None = None
        self.errores_modulo: dict[str, str] = {}
        self.semanas: int = 0
        self.n_jugadas: int = 0
        self.tablas: dict = {}      # jugadas, cuadros, sep_cuadros, presion, objetivo
        self.resultados: dict = {}  # un valor por módulo de calculos/


estado = EstadoGlobal()
