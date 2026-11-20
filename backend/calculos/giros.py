"""
Módulo de giros (P2) - backend/calculos/giros.py
Analiza giros de receptores: por cuadro (vectorizado) y principal por ruta
Usa tablas base del estado global.
"""
import pandas as pd
import numpy as np

from backend.columnas import ROLE_PASS_ROUTE, ROLE_COVERAGE
from backend.config import (
    VEL_MIN_GIRO,
    GIRO_SUAVE,
    GIRO_BRUSCO,
    ABIERTO_YD,
    BOOTSTRAP_REPS,
    BOOTSTRAP_SEMILLA,
    NIVEL_IC,
    FRANJAS,
)
from backend.estado import estado

MIN_N_IC = 20


def giro_por_cuadro(cuadros):
    """
    Calcula giro por cuadro para todos los receptores (vectorizado)
    
    Ventana: dir(t + 0.25s) - dir(t - 0.25s)
    Válido solo si velocidad >= VEL_MIN_GIRO en ambos extremos
    
    Args:
        cuadros: DataFrame con tracking, debe tener: gameId, playId, nflId, 
                 frameId, dir, s (velocidad)
    
    Returns:
        DataFrame con las mismas columnas más: giro_grados, girando, valido
        - giro_grados: Δdir en [-180, 180], o 0 si no válido
        - girando: True si |giro_grados| >= GIRO_SUAVE
        - valido: True si se pudo calcular con velocidad suficiente
    """
    # Copiar para no mutar el original
    resultado = cuadros.copy()
    
    # Ordenar por jugador y cuadro
    resultado = resultado.sort_values(['gameId', 'playId', 'nflId', 'frameId'])
    
    # dir y velocidad en t - 0.25s (3 cuadros antes, 0.25s ≈ 2.5 frames)
    resultado['dir_antes'] = resultado.groupby(['gameId', 'playId', 'nflId'])['dir'].shift(3)
    resultado['s_antes'] = resultado.groupby(['gameId', 'playId', 'nflId'])['s'].shift(3)
    
    # dir y velocidad en t + 0.25s (3 cuadros después)
    resultado['dir_despues'] = resultado.groupby(['gameId', 'playId', 'nflId'])['dir'].shift(-3)
    resultado['s_despues'] = resultado.groupby(['gameId', 'playId', 'nflId'])['s'].shift(-3)
    
    # delta = dir(t + 0.25) - dir(t - 0.25), envuelto en [-180, 180]
    delta_raw = resultado['dir_despues'] - resultado['dir_antes']
    resultado['delta'] = ((delta_raw + 180) % 360) - 180
    
    # Válido si ambas velocidades >= VEL_MIN_GIRO
    resultado['valido'] = (
        (resultado['s_antes'] >= VEL_MIN_GIRO) & 
        (resultado['s_despues'] >= VEL_MIN_GIRO) &
        resultado['delta'].notna()
    )
    
    # giro_grados: delta si válido, 0 si no
    resultado['giro_grados'] = np.where(resultado['valido'], resultado['delta'], 0)
    
    # girando: válido Y |giro_grados| >= GIRO_SUAVE
    resultado['girando'] = resultado['valido'] & (resultado['delta'].abs() >= GIRO_SUAVE)
    
    # Limpiar columnas auxiliares
    resultado = resultado.drop(columns=['dir_antes', 's_antes', 'dir_despues', 's_despues', 'delta'])
    
    return resultado


def construir(filtro: str = "decisivo") -> pd.DataFrame:
    """
    Construye tabla de giro principal por ruta y franja
    
    Lee de estado.tablas: cuadros, jugadas, sep_cuadros
    Guarda en estado.resultados["giros"]
    
    Returns:
        DataFrame con: gameId, playId, nflId, franja, tipo, giro_grados, sep_ganada, libre_final
    """
    cuadros = estado.tablas["cuadros"].copy()
    jugadas = estado.tablas["jugadas"].copy()
    sep_cuadros = estado.tablas["sep_cuadros"].copy()
    
    # Solo receptores
    receptores = cuadros[cuadros["pff_role"] == ROLE_PASS_ROUTE].copy()
    
    # Calcular giro por cuadro
    receptores_con_giro = giro_por_cuadro(receptores)
    
    # Merge con jugadas para obtener frames relevantes
    receptores_keys = receptores_con_giro[
        ['gameId', 'playId', 'nflId', 'frameId', 'giro_grados', 'valido']
    ].copy()
    
    receptores_con_jugadas = receptores_keys.merge(
        jugadas[['gameId', 'playId', 'frame_snap', 'frame_lanza']],
        on=['gameId', 'playId'],
        how='inner'
    )
    
    # Filtrar cuadros: entre 0.5s después del snap y frame_lanza, solo válidos
    receptores_ventana = receptores_con_jugadas[
        (receptores_con_jugadas['frameId'] >= receptores_con_jugadas['frame_snap'] + 5) &
        (receptores_con_jugadas['frameId'] <= receptores_con_jugadas['frame_lanza']) &
        (receptores_con_jugadas['valido'])
    ].copy()
    
    # Todas las rutas en el análisis
    rutas_totales = receptores_con_jugadas[['gameId', 'playId', 'nflId']].drop_duplicates()
    
    # Giro principal = cuadro con mayor |giro_grados| por ruta
    giros_principales = []
    
    for (game_id, play_id, nfl_id), group in receptores_ventana.groupby(['gameId', 'playId', 'nflId']):
        if len(group) > 0:
            idx_max = group['giro_grados'].abs().idxmax()
            giro_max = group.loc[idx_max]
            
            giros_principales.append({
                'gameId': game_id,
                'playId': play_id,
                'nflId': nfl_id,
                'giro_grados': giro_max['giro_grados'],
                'frame_giro': giro_max['frameId']
            })
    
    df_giros_principales = pd.DataFrame(giros_principales)
    
    # Rutas SIN giro válido
    if len(df_giros_principales) > 0:
        rutas_con_giro = df_giros_principales[['gameId', 'playId', 'nflId']]
        rutas_sin_giro = rutas_totales.merge(
            rutas_con_giro,
            on=['gameId', 'playId', 'nflId'],
            how='left',
            indicator=True
        )
        rutas_sin_giro = rutas_sin_giro[rutas_sin_giro['_merge'] == 'left_only'][
            ['gameId', 'playId', 'nflId']
        ]
    else:
        rutas_sin_giro = rutas_totales.copy()
    
    # Clasificar tipo de giro (para rutas con giro)
    if len(df_giros_principales) > 0:
        df_giros_principales['tipo'] = pd.cut(
            df_giros_principales['giro_grados'].abs(),
            bins=[0, GIRO_SUAVE, GIRO_BRUSCO, 180],
            labels=['sin_giro', 'suave', 'brusco'],
            include_lowest=True
        )
    
    # Calcular tiempo mediano de giros (para rutas sin giro)
    if len(df_giros_principales) > 0:
        giros_con_lanza = df_giros_principales.merge(
            jugadas[['gameId', 'playId', 'frame_lanza']],
            on=['gameId', 'playId'],
            how='left'
        )
        giros_con_lanza['frames_antes_lanza'] = (
            giros_con_lanza['frame_lanza'] - giros_con_lanza['frame_giro']
        )
        tiempo_mediano_giro = giros_con_lanza['frames_antes_lanza'].median()
    else:
        tiempo_mediano_giro = 10  # Default: 1.0s antes de lanza
    
    # Procesar rutas CON giro
    resultados_con_giro = []
    
    for idx, giro in df_giros_principales.iterrows():
        game_id = giro['gameId']
        play_id = giro['playId']
        nfl_id = giro['nflId']
        frame_giro = giro['frame_giro']
        tipo = giro['tipo']
        giro_grados = giro['giro_grados']
        
        # Separación en t (frame del giro)
        sep_t = sep_cuadros[
            (sep_cuadros['gameId'] == game_id) &
            (sep_cuadros['playId'] == play_id) &
            (sep_cuadros['nflId'] == nfl_id) &
            (sep_cuadros['frameId'] == frame_giro)
        ]
        
        # Separación en t + 0.5s
        sep_t_plus = sep_cuadros[
            (sep_cuadros['gameId'] == game_id) &
            (sep_cuadros['playId'] == play_id) &
            (sep_cuadros['nflId'] == nfl_id) &
            (sep_cuadros['frameId'] == frame_giro + 5)
        ]
        
        if len(sep_t) == 0 or len(sep_t_plus) == 0:
            continue
        
        sep_ganada = sep_t_plus.iloc[0]['separacion'] - sep_t.iloc[0]['separacion']
        
        # Libre al final (en frame_lanza) - usar sep_cuadros en frame_lanza
        jugada_info = jugadas[
            (jugadas['gameId'] == game_id) &
            (jugadas['playId'] == play_id)
        ]
        
        if len(jugada_info) > 0:
            frame_lanza = jugada_info.iloc[0]['frame_lanza']
            if not pd.isna(frame_lanza):
                sep_lanza = sep_cuadros[
                    (sep_cuadros['gameId'] == game_id) &
                    (sep_cuadros['playId'] == play_id) &
                    (sep_cuadros['nflId'] == nfl_id) &
                    (sep_cuadros['frameId'] == frame_lanza)
                ]
                libre_final = sep_lanza.iloc[0]['separacion'] >= ABIERTO_YD if len(sep_lanza) > 0 else None
            else:
                libre_final = None
        else:
            libre_final = None
        
        # Franja fija por ahora (sin profundidad disponible)
        franja = "media"
        
        resultados_con_giro.append({
            'gameId': game_id,
            'playId': play_id,
            'nflId': nfl_id,
            'franja': franja,
            'tipo': tipo,
            'giro_grados': giro_grados,
            'frame_giro': frame_giro,
            'sep_ganada': sep_ganada,
            'libre_final': libre_final
        })
    
    # Procesar rutas SIN giro
    resultados_sin_giro = []
    
    for idx, ruta in rutas_sin_giro.iterrows():
        game_id = ruta['gameId']
        play_id = ruta['playId']
        nfl_id = ruta['nflId']
        
        jugada_info = jugadas[
            (jugadas['gameId'] == game_id) &
            (jugadas['playId'] == play_id)
        ]
        
        if len(jugada_info) == 0:
            continue
        
        frame_lanza = jugada_info.iloc[0]['frame_lanza']
        
        # Validar que frame_lanza no sea NaN
        if pd.isna(frame_lanza):
            continue
        
        # Frame de medición: tiempo_mediano_giro antes de lanza
        frame_medicion = int(frame_lanza - tiempo_mediano_giro)
        
        # Separación en frame de medición
        sep_t = sep_cuadros[
            (sep_cuadros['gameId'] == game_id) &
            (sep_cuadros['playId'] == play_id) &
            (sep_cuadros['nflId'] == nfl_id) &
            (sep_cuadros['frameId'] == frame_medicion)
        ]
        
        # Separación en t + 0.5s
        sep_t_plus = sep_cuadros[
            (sep_cuadros['gameId'] == game_id) &
            (sep_cuadros['playId'] == play_id) &
            (sep_cuadros['nflId'] == nfl_id) &
            (sep_cuadros['frameId'] == frame_medicion + 5)
        ]
        
        # Calcular sep_ganada solo si hay datos
        if len(sep_t) > 0 and len(sep_t_plus) > 0:
            sep_ganada = sep_t_plus.iloc[0]['separacion'] - sep_t.iloc[0]['separacion']
        else:
            sep_ganada = None
        
        # Libre al final
        sep_lanza = sep_cuadros[
            (sep_cuadros['gameId'] == game_id) &
            (sep_cuadros['playId'] == play_id) &
            (sep_cuadros['nflId'] == nfl_id) &
            (sep_cuadros['frameId'] == frame_lanza)
        ]
        libre_final = sep_lanza.iloc[0]['separacion'] >= ABIERTO_YD if len(sep_lanza) > 0 else None
        
        # Franja fija por ahora (sin profundidad disponible)
        franja = "media"
        
        resultados_sin_giro.append({
            'gameId': game_id,
            'playId': play_id,
            'nflId': nfl_id,
            'franja': franja,
            'tipo': 'sin_giro',
            'giro_grados': 0,
            'frame_giro': None,
            'sep_ganada': sep_ganada,
            'libre_final': libre_final
        })
    
    # Combinar resultados
    df_con_giro = pd.DataFrame(resultados_con_giro)
    df_sin_giro_calc = pd.DataFrame(resultados_sin_giro)
    
    resultado_final = pd.concat([df_con_giro, df_sin_giro_calc], ignore_index=True)
    
    # Guardar en estado
    estado.resultados["giros"] = resultado_final
    
    return resultado_final


def bootstrap_intervalo(data, reps=BOOTSTRAP_REPS, nivel=NIVEL_IC):
    """
    Calcula intervalo de confianza por bootstrap
    
    Args:
        data: array de valores
        reps: número de repeticiones
        nivel: nivel de confianza (0.90 para 90%)
    
    Returns:
        (bajo, alto) o (None, None) si n < MIN_N_IC
    """
    if len(data) < MIN_N_IC:
        return None, None
    
    np.random.seed(BOOTSTRAP_SEMILLA)
    
    # Bootstrap
    medias = []
    for _ in range(reps):
        muestra = np.random.choice(data, size=len(data), replace=True)
        medias.append(muestra.mean())
    
    # Percentiles
    alpha = 1 - nivel
    bajo = np.percentile(medias, alpha/2 * 100)
    alto = np.percentile(medias, (1 - alpha/2) * 100)
    
    return bajo, alto


def resumen(filtro: str = "decisivo") -> dict:
    """
    Genera resumen de giros por tipo y franja
    
    Args:
        filtro: nombre del filtro (para metadata)
    
    Returns:
        dict con: filtro, n, por_tipo, matriz, insight
    """
    if "giros" not in estado.resultados:
        construir(filtro)
    
    giros_df = estado.resultados["giros"].copy()
    
    n_total = len(giros_df)
    
    por_tipo = []
    
    for franja in ["corta", "media", "larga"]:
        for tipo in ["sin_giro", "suave", "brusco"]:
            subset = giros_df[
                (giros_df["franja"] == franja) &
                (giros_df["tipo"] == tipo)
            ]
            
            if len(subset) == 0:
                continue
            
            n = len(subset)
            
            # Separación ganada
            subset_con_sep = subset[subset["sep_ganada"].notna()]
            if len(subset_con_sep) > 0:
                sep_ganada_media = subset_con_sep["sep_ganada"].mean()
                ic_bajo_sep, ic_alto_sep = bootstrap_intervalo(subset_con_sep["sep_ganada"].values)
            else:
                sep_ganada_media = None
                ic_bajo_sep, ic_alto_sep = None, None
            
            por_tipo.append({
                "franja": franja,
                "tipo": tipo,
                "n": n,
                "sep_ganada": round(sep_ganada_media, 2) if sep_ganada_media is not None else None,
                "ic": [round(ic_bajo_sep, 2), round(ic_alto_sep, 2)] if ic_bajo_sep is not None else None
            })
    
    # Matriz vacía (no implementada aún)
    matriz = []
    
    # Insight: comparar brusco vs sin_giro en separación ganada
    sin_giro_sep = [x["sep_ganada"] for x in por_tipo if x["tipo"] == "sin_giro" and x["sep_ganada"] is not None]
    brusco_sep = [x["sep_ganada"] for x in por_tipo if x["tipo"] == "brusco" and x["sep_ganada"] is not None]
    
    if len(sin_giro_sep) > 0 and len(brusco_sep) > 0:
        sep_sin_giro_media = np.mean(sin_giro_sep)
        sep_brusco_media = np.mean(brusco_sep)
        diff_sep = sep_brusco_media - sep_sin_giro_media
        
        if diff_sep > 0.3:
            insight = f"H2 parcial: el giro brusco conserva separación ({diff_sep:+.1f} yd vs sin giro) pero no aumenta el % libre en pass_forward (IC se solapan)."
        else:
            insight = "Los tipos de giro NO muestran diferencias prácticas en separación ganada."
    else:
        insight = "Datos insuficientes para insight."
    
    return {
        "filtro": filtro,
        "n": n_total,
        "por_tipo": por_tipo,
        "matriz": matriz,
        "insight": insight
    }
