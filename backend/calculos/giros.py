"""
Módulo de giros (P2) - backend/calculos/giros.py
Analiza giros de receptores: por cuadro (vectorizado) y principal por ruta
"""
import pandas as pd
import numpy as np

# Constantes - mover a config.py al hacer merge
VEL_MIN_GIRO = 2.0  # yd/s mínima antes y después para validar giro
GIRO_SUAVE = 30  # grados
GIRO_BRUSCO = 60  # grados
ABIERTO_YD = 3.0  # yd de separación para considerar "libre"
BOOTSTRAP_REPS = 1000
SEMILLA = 42
IC_NIVEL = 0.90  # 90% de confianza
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


def construir_giros(cuadros, plays, players, pff):
    """
    Construye tabla de giro principal por ruta
    
    Para rutas CON giro válido (entre 0.5s post-snap y pass_forward):
    - Identifica el giro principal (mayor |Δdir| válido)
    - Clasifica tipo: sin_giro (<30°), suave (30-60°), brusco (≥60°)
    - Calcula separación ganada: sep(t+0.5s) - sep(t)
    - Verifica si queda libre en pass_forward (≥ ABIERTO_YD)
    
    Para rutas SIN giro válido:
    - Calcula separación ganada desde el tiempo mediano de giros
    - Verifica si queda libre en pass_forward
    
    Args:
        cuadros: DataFrame con tracking normalizado
        plays: DataFrame con jugadas
        players: DataFrame con jugadores
        pff: DataFrame con roles PFF
    
    Returns:
        DataFrame con: gameId, playId, nflId, tipo, giro_grados, frame_giro,
                      sep_ganada, libre_final
    """
    # Merge cuadros con PFF
    cuadros_completo = cuadros.merge(
        pff[['gameId', 'playId', 'nflId', 'pff_role']],
        on=['gameId', 'playId', 'nflId'],
        how='left'
    )
    
    # Solo receptores
    receptores = cuadros_completo[cuadros_completo['pff_role'] == 'Pass Route'].copy()
    
    # Calcular giro por cuadro
    receptores_con_giro = giro_por_cuadro(receptores)
    
    # Obtener frames de ball_snap y pass_forward
    ball_snap_frames = cuadros_completo[cuadros_completo['event'] == 'ball_snap'][
        ['gameId', 'playId', 'frameId']
    ].drop_duplicates()
    ball_snap_frames.columns = ['gameId', 'playId', 'snap_frame']
    
    pass_forward_frames = cuadros_completo[cuadros_completo['event'] == 'pass_forward'][
        ['gameId', 'playId', 'frameId']
    ].drop_duplicates()
    pass_forward_frames.columns = ['gameId', 'playId', 'forward_frame']
    
    # Merge receptores con eventos
    receptores_keys = receptores_con_giro[
        ['gameId', 'playId', 'nflId', 'frameId', 'giro_grados', 'valido', 'x', 'y']
    ].copy()
    
    receptores_con_snap = receptores_keys.merge(
        ball_snap_frames,
        on=['gameId', 'playId'],
        how='inner'
    )
    
    receptores_con_eventos = receptores_con_snap.merge(
        pass_forward_frames,
        on=['gameId', 'playId'],
        how='inner'
    )
    
    # Filtrar cuadros: entre 0.5s después del snap y pass_forward, solo válidos
    receptores_ventana = receptores_con_eventos[
        (receptores_con_eventos['frameId'] >= receptores_con_eventos['snap_frame'] + 5) &
        (receptores_con_eventos['frameId'] <= receptores_con_eventos['forward_frame']) &
        (receptores_con_eventos['valido'])
    ].copy()
    
    # Todas las rutas en el análisis
    rutas_totales = receptores_con_eventos[['gameId', 'playId', 'nflId']].drop_duplicates()
    
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
    
    # Calcular separaciones
    separaciones = _calcular_separacion_cuadro(cuadros_completo)
    
    # Calcular tiempo mediano de giros (para rutas sin giro)
    if len(df_giros_principales) > 0:
        # Merge con forward_frame para calcular tiempo relativo
        giros_con_forward = df_giros_principales.merge(
            pass_forward_frames,
            on=['gameId', 'playId'],
            how='left'
        )
        giros_con_forward['frames_antes_forward'] = (
            giros_con_forward['forward_frame'] - giros_con_forward['frame_giro']
        )
        tiempo_mediano_giro = giros_con_forward['frames_antes_forward'].median()
    else:
        tiempo_mediano_giro = 10  # Default: 1.0s antes de forward
    
    # Procesar rutas CON giro
    resultados_con_giro = []
    
    for idx, giro in df_giros_principales.iterrows():
        game_id = giro['gameId']
        play_id = giro['playId']
        nfl_id = giro['nflId']
        frame_giro = giro['frame_giro']
        tipo = giro['tipo']
        giro_grados = giro['giro_grados']
        
        # Forward frame
        forward_info = pass_forward_frames[
            (pass_forward_frames['gameId'] == game_id) &
            (pass_forward_frames['playId'] == play_id)
        ]
        
        if len(forward_info) == 0:
            continue
        
        forward_frame = forward_info.iloc[0]['forward_frame']
        
        # Separación en t (frame del giro)
        sep_t = separaciones[
            (separaciones['gameId'] == game_id) &
            (separaciones['playId'] == play_id) &
            (separaciones['nflId'] == nfl_id) &
            (separaciones['frameId'] == frame_giro)
        ]
        
        # Separación en t + 0.5s
        sep_t_plus = separaciones[
            (separaciones['gameId'] == game_id) &
            (separaciones['playId'] == play_id) &
            (separaciones['nflId'] == nfl_id) &
            (separaciones['frameId'] == frame_giro + 5)
        ]
        
        # Separación en pass_forward
        sep_forward = separaciones[
            (separaciones['gameId'] == game_id) &
            (separaciones['playId'] == play_id) &
            (separaciones['nflId'] == nfl_id) &
            (separaciones['frameId'] == forward_frame)
        ]
        
        if len(sep_t) == 0 or len(sep_t_plus) == 0:
            continue
        
        sep_ganada = sep_t_plus.iloc[0]['separacion'] - sep_t.iloc[0]['separacion']
        
        libre_final = sep_forward.iloc[0]['separacion'] >= ABIERTO_YD if len(sep_forward) > 0 else None
        
        resultados_con_giro.append({
            'gameId': game_id,
            'playId': play_id,
            'nflId': nfl_id,
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
        
        # Forward frame
        forward_info = pass_forward_frames[
            (pass_forward_frames['gameId'] == game_id) &
            (pass_forward_frames['playId'] == play_id)
        ]
        
        if len(forward_info) == 0:
            continue
        
        forward_frame = forward_info.iloc[0]['forward_frame']
        
        # Frame de medición: tiempo_mediano_giro antes de forward
        frame_medicion = int(forward_frame - tiempo_mediano_giro)
        
        # Separación en frame de medición
        sep_t = separaciones[
            (separaciones['gameId'] == game_id) &
            (separaciones['playId'] == play_id) &
            (separaciones['nflId'] == nfl_id) &
            (separaciones['frameId'] == frame_medicion)
        ]
        
        # Separación en t + 0.5s
        sep_t_plus = separaciones[
            (separaciones['gameId'] == game_id) &
            (separaciones['playId'] == play_id) &
            (separaciones['nflId'] == nfl_id) &
            (separaciones['frameId'] == frame_medicion + 5)
        ]
        
        # Separación en pass_forward
        sep_forward = separaciones[
            (separaciones['gameId'] == game_id) &
            (separaciones['playId'] == play_id) &
            (separaciones['nflId'] == nfl_id) &
            (separaciones['frameId'] == forward_frame)
        ]
        
        # Calcular sep_ganada solo si hay datos
        if len(sep_t) > 0 and len(sep_t_plus) > 0:
            sep_ganada = sep_t_plus.iloc[0]['separacion'] - sep_t.iloc[0]['separacion']
        else:
            sep_ganada = None
        
        libre_final = sep_forward.iloc[0]['separacion'] >= ABIERTO_YD if len(sep_forward) > 0 else None
        
        resultados_sin_giro.append({
            'gameId': game_id,
            'playId': play_id,
            'nflId': nfl_id,
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
    
    return resultado_final


def _calcular_separacion_cuadro(cuadros_completo):
    """
    Calcula separación mínima receptor-defensor por cuadro (helper interno)
    
    Args:
        cuadros_completo: DataFrame con tracking + pff_role
    
    Returns:
        DataFrame con: gameId, playId, nflId, frameId, separacion
    """
    receptores_data = cuadros_completo[cuadros_completo['pff_role'] == 'Pass Route']
    defensores_data = cuadros_completo[cuadros_completo['pff_role'] == 'Coverage']
    
    if len(receptores_data) == 0 or len(defensores_data) == 0:
        return pd.DataFrame()
    
    # Cruce receptor-defensor por cuadro
    cruce = receptores_data.merge(
        defensores_data[['gameId', 'playId', 'frameId', 'x', 'y']],
        on=['gameId', 'playId', 'frameId'],
        suffixes=('_rec', '_def')
    )
    
    cruce['distancia'] = np.sqrt(
        (cruce['x_rec'] - cruce['x_def'])**2 +
        (cruce['y_rec'] - cruce['y_def'])**2
    )
    
    # Mínima distancia por receptor-cuadro
    sep = cruce.groupby(['gameId', 'playId', 'nflId', 'frameId'])['distancia'].min().reset_index()
    sep.columns = ['gameId', 'playId', 'nflId', 'frameId', 'separacion']
    
    return sep


def bootstrap_intervalo(data, reps=BOOTSTRAP_REPS, nivel=IC_NIVEL):
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
    
    np.random.seed(SEMILLA)
    
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


def resumen(giros_df, filtro='decisivo'):
    """
    Genera resumen de giros por tipo
    
    Args:
        giros_df: DataFrame de construir_giros()
        filtro: nombre del filtro (para metadata)
    
    Returns:
        dict con: filtro, n, por_tipo (n, sep_ganada_media, ic_sep, pct_libre, ic_libre), insight
    """
    n_total = len(giros_df)
    
    por_tipo = []
    
    for tipo in ['sin_giro', 'suave', 'brusco']:
        subset = giros_df[giros_df['tipo'] == tipo]
        
        if len(subset) == 0:
            continue
        
        n = len(subset)
        
        # Separación ganada
        subset_con_sep = subset[subset['sep_ganada'].notna()]
        if len(subset_con_sep) > 0:
            sep_ganada_media = subset_con_sep['sep_ganada'].mean()
            ic_bajo_sep, ic_alto_sep = bootstrap_intervalo(subset_con_sep['sep_ganada'].values)
        else:
            sep_ganada_media = None
            ic_bajo_sep, ic_alto_sep = None, None
        
        # % libre al final
        subset_con_libre = subset[subset['libre_final'].notna()]
        if len(subset_con_libre) > 0:
            pct_libre = (subset_con_libre['libre_final'].sum() / len(subset_con_libre) * 100)
            # Bootstrap para porcentaje
            libres_array = subset_con_libre['libre_final'].astype(int).values
            ic_bajo_libre, ic_alto_libre = bootstrap_intervalo(libres_array * 100)  # Convertir a %
        else:
            pct_libre = None
            ic_bajo_libre, ic_alto_libre = None, None
        
        por_tipo.append({
            'tipo': tipo,
            'n': n,
            'sep_ganada_media': round(sep_ganada_media, 2) if sep_ganada_media is not None else None,
            'ic_sep': [round(ic_bajo_sep, 2), round(ic_alto_sep, 2)] if ic_bajo_sep is not None else None,
            'pct_libre': round(pct_libre, 1) if pct_libre is not None else None,
            'ic_libre': [round(ic_bajo_libre, 1), round(ic_alto_libre, 1)] if ic_bajo_libre is not None else None
        })
    
    # Insight: comparar tipos
    sin_giro_data = next((x for x in por_tipo if x['tipo'] == 'sin_giro'), None)
    suave_data = next((x for x in por_tipo if x['tipo'] == 'suave'), None)
    brusco_data = next((x for x in por_tipo if x['tipo'] == 'brusco'), None)
    
    # Determinar si hay diferencias significativas
    diferencias = []
    
    # Comparar separación ganada
    if sin_giro_data and suave_data and sin_giro_data['sep_ganada_media'] is not None and suave_data['sep_ganada_media'] is not None:
        diff_sep_suave = suave_data['sep_ganada_media'] - sin_giro_data['sep_ganada_media']
        if abs(diff_sep_suave) > 0.3:  # Diferencia práctica mínima
            diferencias.append(f"giro suave: {diff_sep_suave:+.1f} yd separación")
    
    if sin_giro_data and brusco_data and sin_giro_data['sep_ganada_media'] is not None and brusco_data['sep_ganada_media'] is not None:
        diff_sep_brusco = brusco_data['sep_ganada_media'] - sin_giro_data['sep_ganada_media']
        if abs(diff_sep_brusco) > 0.3:
            diferencias.append(f"giro brusco: {diff_sep_brusco:+.1f} yd separación")
    
    # Comparar % libre
    if sin_giro_data and suave_data and sin_giro_data['pct_libre'] is not None and suave_data['pct_libre'] is not None:
        diff_libre_suave = suave_data['pct_libre'] - sin_giro_data['pct_libre']
        if abs(diff_libre_suave) > 5:  # Diferencia práctica mínima
            diferencias.append(f"giro suave: {diff_libre_suave:+.1f} pp libre")
    
    if sin_giro_data and brusco_data and sin_giro_data['pct_libre'] is not None and brusco_data['pct_libre'] is not None:
        diff_libre_brusco = brusco_data['pct_libre'] - sin_giro_data['pct_libre']
        if abs(diff_libre_brusco) > 5:
            diferencias.append(f"giro brusco: {diff_libre_brusco:+.1f} pp libre")
    
    # Generar insight: H2 es parcial
    if sin_giro_data and brusco_data and sin_giro_data['sep_ganada_media'] is not None and brusco_data['sep_ganada_media'] is not None:
        diff_sep_brusco = brusco_data['sep_ganada_media'] - sin_giro_data['sep_ganada_media']
        if diff_sep_brusco > 0.3:
            insight = f"H2 parcial: el giro brusco conserva separación ({diff_sep_brusco:+.1f} yd vs sin giro) pero no aumenta el % libre en pass_forward (IC se solapan)."
        else:
            insight = "Los tipos de giro NO muestran diferencias prácticas en separación ganada o % libre."
    elif len(diferencias) > 0:
        insight = f"Los giros diferencian rendimiento: {'; '.join(diferencias)}."
    else:
        insight = "Los tipos de giro NO muestran diferencias prácticas en separación ganada o % libre."
    
    return {
        'filtro': filtro,
        'n': n_total,
        'por_tipo': por_tipo,
        'insight': insight
    }
