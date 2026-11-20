"""
backend/normalizacion.py

Normalización de dirección de jugada en el tracking del NFL Big Data Bowl 2023.

Convención: después de normalizar, TODAS las jugadas atacan hacia x creciente
(hacia la derecha). Los ángulos o y dir también se rotan para que sean
consistentes con esa dirección.
"""

import pandas as pd
import numpy as np

# ── Constantes ────────────────────────────────────────────────────────────────

ANCHO: float = 160 / 3          # 53.333... yardas (ancho de la cancha)
LARGO: float = 120.0            # yardas (largo incluyendo end zones)
COL_NORMALIZADO = "normalizado"


def normalizar_direccion(tracking: pd.DataFrame) -> pd.DataFrame:
    """Normaliza el tracking para que todas las jugadas ataquen hacia x creciente.

    Jugadas incluidas: todas las que trae el DataFrame.
    Jugadas excluidas: ninguna (la función no filtra; quien llama debe hacerlo).

    Transformación para filas con playDirection == "left":
        x   -> LARGO - x          (120 - x)
        y   -> ANCHO - y          (160/3 - y)
        o   -> (o + 180) % 360
        dir -> (dir + 180) % 360

    Columnas que NO cambian: s, a, dis, frameId, nflId, team, event, etc.
    s, a y dis son magnitudes escalares, no dependen de la dirección.

    Parámetros
    ----------
    tracking : pd.DataFrame
        DataFrame de tracking con al menos las columnas:
        playDirection, x, y. o y dir se transforman si están presentes.

    Retorna
    -------
    pd.DataFrame
        Copia normalizada con una columna booleana "normalizado" = True.
        Los dtypes de x, y, o, dir se conservan (float32 sigue float32).

    Lanza
    -----
    ValueError
        Si el DataFrame ya tiene la columna "normalizado" con valor True
        (protección contra doble normalización).
    ValueError
        Si falta la columna playDirection o x o y.
    """
    # Guardia: doble normalización
    if COL_NORMALIZADO in tracking.columns:
        if tracking[COL_NORMALIZADO].any():
            raise ValueError(
                "El DataFrame ya está normalizado (columna 'normalizado' == True). "
                "No se puede normalizar dos veces."
            )

    # Columnas requeridas
    for col in ("playDirection", "x", "y"):
        if col not in tracking.columns:
            raise ValueError(f"Columna requerida ausente: '{col}'")

    df = tracking.copy()

    izq = df["playDirection"] == "left"

    # ── Posición ─────────────────────────────────────────────────────────────
    x_orig_dtype = df["x"].dtype
    y_orig_dtype = df["y"].dtype

    df.loc[izq, "x"] = (LARGO - df.loc[izq, "x"]).astype(x_orig_dtype)
    df.loc[izq, "y"] = (ANCHO - df.loc[izq, "y"]).astype(y_orig_dtype)

    # ── Ángulos (solo si existen) ─────────────────────────────────────────────
    for col in ("o", "dir"):
        if col in df.columns:
            orig_dtype = df[col].dtype
            df.loc[izq, col] = ((df.loc[izq, col] + 180) % 360).astype(orig_dtype)

    df[COL_NORMALIZADO] = True
    return df


# ── Constantes para línea de golpeo ──────────────────────────────────────────

FRAMES_PRESNAP: int = 5          # últimos N frames antes del snap para C'
UMBRAL_DISCREPANCIA: float = 1.5  # yardas: si |C' - D| > umbral, usar D


def calcular_linea_golpeo(
    tracking: pd.DataFrame,
    plays: pd.DataFrame,
) -> pd.DataFrame:
    """Calcula la línea de golpeo por jugada a partir del tracking normalizado.

    Jugadas incluidas: las que tienen el evento ball_snap en el tracking.
    Jugadas excluidas: las que no tienen ball_snap (quien llama debe manejarlas).

    Lógica (orden de prioridad):
      C' = mediana de x del balón en los últimos FRAMES_PRESNAP frames antes
           del frame ball_snap (frames con rel ∈ {-5, -4, -3, -2, -1}).
      D  = absoluteYardlineNumber si playDirection original era "right",
           o (LARGO - absoluteYardlineNumber) si era "left".
      - Si la jugada no tiene frames pre-snap → usar D  (fuente: "absolute_yardline").
      - Si |C' - D| > UMBRAL_DISCREPANCIA  → usar D y marcar la jugada.
      - En el resto → usar C'              (fuente: "balon_presnap").

    Supuestos
    ---------
    - El tracking ya está normalizado (columna 'normalizado' == True).
    - El balón se identifica por nflId NaN.
    - La columna playDirection en el tracking conserva el valor original
      (no cambia con la normalización).
    - plays debe contener gameId, playId y absoluteYardlineNumber.

    Parámetros
    ----------
    tracking : pd.DataFrame
        Tracking normalizado. Columnas mínimas:
        gameId, playId, nflId, frameId, x, playDirection, event, normalizado.
    plays : pd.DataFrame
        Al menos: gameId, playId, absoluteYardlineNumber.

    Retorna
    -------
    pd.DataFrame con columnas:
        gameId, playId,
        linea_golpeo   : float  — x de la línea de golpeo (yardas, normalizado)
        fuente_linea   : str    — "balon_presnap" | "absolute_yardline"
        marcada        : bool   — True si |C' - D| > UMBRAL_DISCREPANCIA
        diff_cprime_D  : float  — |C' - D| en yardas (NaN si C' no pudo calcularse)
    """
    if COL_NORMALIZADO not in tracking.columns or not tracking[COL_NORMALIZADO].any():
        raise ValueError(
            "El tracking debe estar normalizado antes de calcular la línea de golpeo. "
            "Llama primero a normalizar_direccion()."
        )

    # ── Frame del snap por jugada ─────────────────────────────────────────────
    snap_frames = (
        tracking[tracking["event"].astype(str) == "ball_snap"]
        .drop_duplicates(["gameId", "playId"])
        [["gameId", "playId", "frameId"]]
        .rename(columns={"frameId": "frame_snap"})
    )

    # ── Balón solamente ───────────────────────────────────────────────────────
    balon = tracking[tracking["nflId"].isna()][
        ["gameId", "playId", "frameId", "x", "playDirection"]
    ].copy()
    balon = balon.merge(snap_frames, on=["gameId", "playId"],
                        how="inner", validate="many_to_one")
    balon["rel"] = balon["frameId"] - balon["frame_snap"]

    # ── C': mediana de los últimos FRAMES_PRESNAP frames antes del snap ───────
    presnap = balon[
        (balon["rel"] >= -FRAMES_PRESNAP) & (balon["rel"] < 0)
    ]
    cprime = (
        presnap.groupby(["gameId", "playId"])["x"]
        .median()
        .rename("cprime")
        .reset_index()
    )

    # ── D: absoluteYardlineNumber ajustado por dirección ─────────────────────
    # playDirection viene del tracking normalizado (valor original conservado)
    dir_por_jugada = (
        tracking[["gameId", "playId", "playDirection"]]
        .drop_duplicates(["gameId", "playId"])
    )
    plays_sel = plays[["gameId", "playId", "absoluteYardlineNumber"]].copy()
    plays_sel = plays_sel.merge(dir_por_jugada, on=["gameId", "playId"],
                                how="left", validate="one_to_one")
    plays_sel["D"] = np.where(
        plays_sel["playDirection"].astype(str) == "right",
        plays_sel["absoluteYardlineNumber"],
        LARGO - plays_sel["absoluteYardlineNumber"],
    )
    cD = plays_sel[["gameId", "playId", "D"]]

    # ── Unir C' y D para todas las jugadas con snap ───────────────────────────
    result = snap_frames[["gameId", "playId"]].merge(
        cprime, on=["gameId", "playId"], how="left"
    ).merge(
        cD, on=["gameId", "playId"], how="left", validate="many_to_one"
    )

    # ── Diferencia y lógica de selección ─────────────────────────────────────
    result["diff_cprime_D"] = (result["cprime"] - result["D"]).abs()

    sin_presnap  = result["cprime"].isna()
    discrepancia = (~sin_presnap) & (result["diff_cprime_D"] > UMBRAL_DISCREPANCIA)
    usar_D       = sin_presnap | discrepancia

    result["linea_golpeo"] = np.where(usar_D, result["D"], result["cprime"])
    result["fuente_linea"] = np.where(usar_D, "absolute_yardline", "balon_presnap")
    result["marcada"]      = discrepancia

    # diff_cprime_D queda NaN donde no había C' (sin_presnap); eso es correcto
    return result[["gameId", "playId", "linea_golpeo",
                   "fuente_linea", "marcada", "diff_cprime_D"]]
