"""
Módulo de vuelo (ventaja al lanzar) - backend/calculos/vuelo.py
P3 revisado: Analiza separación del objetivo EN el lanzamiento
"""
import pandas as pd
import numpy as np

# Constantes - mover a config.py al hacer merge
ABIERTO_YD = 3.0
SEP_CERRADA_YD = 1.5  # definición actualizada en pregunta.md
TENDENCIA_UMBRAL_YD = 0.5
BOOTSTRAP_REPS = 1000
SEMILLA = 42
IC_NIVEL = 0.90  # 90% de confianza (pregunta.md)
MIN_N_IC = 20


def normalizar_apellido(apellido):
    """
    Normaliza apellido: quita sufijos (Jr., Sr., II, III, IV) y guiones
    """
    if pd.isna(apellido):
        return None
    
    apellido = str(apellido).strip()
    
    # Quitar sufijos comunes
    sufijos = ['Jr.', 'Sr.', 'II', 'III', 'IV', 'V']
    for sufijo in sufijos:
        if apellido.endswith(' ' + sufijo):
            apellido = apellido[:-len(sufijo)-1].strip()
    
    # Quitar guiones
    apellido = apellido.replace('-', '')
    
    return apellido.lower()


def extraer_objetivo_de_descripcion(descripcion):
    """
    Extrae apellido del receptor objetivo de playDescription
    Busca " to " (pase) o "intended for " (intercepción)
    
    Returns:
        (apellido_normalizado, inicial_o_None)
    """
    if pd.isna(descripcion):
        return None, None
    
    texto_buscar = None
    
    # Buscar " to "
    if ' to ' in descripcion:
        texto_buscar = descripcion.split(' to ', 1)[1]
    # Buscar "intended for "
    elif 'intended for ' in descripcion:
        texto_buscar = descripcion.split('intended for ', 1)[1]
    
    if texto_buscar is None:
        return None, None
    
    palabras = texto_buscar.split()
    if not palabras:
        return None, None
    
    nombre_completo = palabras[0]
    
    # Separar inicial y apellido
    if '.' in nombre_completo:
        partes = nombre_completo.split('.')
        if len(partes) >= 2:
            inicial = partes[0]
            apellido = '.'.join(partes[1:])
            return normalizar_apellido(apellido), inicial
    
    return normalizar_apellido(nombre_completo), None


def construir(cuadros, plays, players, pff, usar_respaldo=False):
    """
    Construye tabla de ventaja al lanzar (una fila por jugada con pase)
    
    Args:
        cuadros: DataFrame con tracking normalizado
        plays: DataFrame con jugadas
        players: DataFrame con jugadores
        pff: DataFrame con roles PFF
        usar_respaldo: Si True, usa receptor más cercano cuando no se encuentra por nombre
    
    Returns:
        DataFrame con: gameId, playId, objetivo_id, objetivo_nombre, aproximado,
                      sep_forward, franja_sep, tendencia, cambio_sep, completo
    """
    # Merge cuadros con PFF y players
    cuadros_completo = cuadros.merge(
        pff[['gameId', 'playId', 'nflId', 'pff_role']],
        on=['gameId', 'playId', 'nflId'],
        how='left'
    ).merge(
        players[['nflId', 'displayName']],
        on='nflId',
        how='left'
    )
    
    # Jugadas con pase (C, I, IN)
    jugadas_pase = plays[plays['passResult'].isin(['C', 'I', 'IN'])].copy()
    
    # Extraer objetivo de playDescription
    objetivo_info = jugadas_pase['playDescription'].apply(
        extraer_objetivo_de_descripcion
    )
    jugadas_pase['apellido_objetivo'] = objetivo_info.apply(lambda x: x[0] if x else None)
    jugadas_pase['inicial_objetivo'] = objetivo_info.apply(lambda x: x[1] if x else None)
    
    # Frames de pass_forward
    pass_forward_frames = cuadros_completo[
        cuadros_completo['event'] == 'pass_forward'
    ][['gameId', 'playId', 'frameId']].drop_duplicates()
    pass_forward_frames.columns = ['gameId', 'playId', 'forward_frame']
    
    resultados = []
    
    for _, jugada in jugadas_pase.iterrows():
        game_id = jugada['gameId']
        play_id = jugada['playId']
        apellido_objetivo = jugada['apellido_objetivo']
        inicial_objetivo = jugada['inicial_objetivo']
        pass_result = jugada['passResult']
        
        # Frame de pass_forward
        forward_info = pass_forward_frames[
            (pass_forward_frames['gameId'] == game_id) &
            (pass_forward_frames['playId'] == play_id)
        ]
        
        if len(forward_info) == 0:
            continue
        
        forward_frame = forward_info.iloc[0]['forward_frame']
        
        # Tracking de esta jugada
        tracking_jugada = cuadros_completo[
            (cuadros_completo['gameId'] == game_id) &
            (cuadros_completo['playId'] == play_id)
        ]
        
        objetivo_id = None
        objetivo_nombre = None
        aproximado = False
        valido = True  # Por defecto es válido
        
        # Si no hay apellido_objetivo (spike, throaway), marcar como NO VÁLIDO
        if pd.isna(apellido_objetivo):
            valido = False
            continue  # No procesar esta jugada
        
        # Intentar encontrar objetivo por apellido
        receptores = tracking_jugada[
            (tracking_jugada['pff_role'] == 'Pass Route') &
            (tracking_jugada['displayName'].notna())
        ].copy()
        
        if len(receptores) > 0:
            # Normalizar apellidos de receptores
            receptores['apellido_normalizado'] = receptores['displayName'].apply(
                lambda x: normalizar_apellido(x.split()[-1] if pd.notna(x) and ' ' in x else x)
            )
            
            # Filtrar por apellido
            objetivo_matches = receptores[
                receptores['apellido_normalizado'] == apellido_objetivo
            ]
            
            # Si hay múltiples con el mismo apellido, usar inicial
            if len(objetivo_matches) > 1 and inicial_objetivo is not None:
                objetivo_matches['inicial'] = objetivo_matches['displayName'].apply(
                    lambda x: x.split()[0][0] if pd.notna(x) and ' ' in x else None
                )
                objetivo_matches = objetivo_matches[
                    objetivo_matches['inicial'] == inicial_objetivo
                ]
            
            if len(objetivo_matches) > 0:
                objetivo_id = objetivo_matches['nflId'].iloc[0]
                objetivo_nombre = objetivo_matches['displayName'].iloc[0]
                aproximado = False
        
        # Si no se encontró por nombre: NO usar respaldo, saltar jugada
        if objetivo_id is None:
            # RESPALDO (solo si usar_respaldo=True): usar receptor más cercano al balón para C o I
            if usar_respaldo and pass_result in ['C', 'I']:
                # Último cuadro disponible (tracking se corta 0.5s después de forward)
                max_frame = tracking_jugada['frameId'].max()
                
                receptores_ultimo = tracking_jugada[
                    (tracking_jugada['frameId'] == max_frame) &
                    (tracking_jugada['pff_role'] == 'Pass Route')
                ]
                
                balon_ultimo = tracking_jugada[
                    (tracking_jugada['frameId'] == max_frame) &
                    (tracking_jugada['team'] == 'football')
                ]
                
                if len(receptores_ultimo) > 0 and len(balon_ultimo) > 0:
                    balon_x, balon_y = balon_ultimo.iloc[0]['x'], balon_ultimo.iloc[0]['y']
                    
                    receptores_ultimo_copy = receptores_ultimo.copy()
                    receptores_ultimo_copy['dist_balon'] = np.sqrt(
                        (receptores_ultimo_copy['x'] - balon_x)**2 +
                        (receptores_ultimo_copy['y'] - balon_y)**2
                    )
                    
                    objetivo_match = receptores_ultimo_copy.loc[receptores_ultimo_copy['dist_balon'].idxmin()]
                    objetivo_id = objetivo_match['nflId']
                    objetivo_nombre = objetivo_match['displayName']
                    aproximado = True  # Objetivo aproximado por distancia al balón
            
            # Si aún no hay objetivo, saltar esta jugada
            if objetivo_id is None:
                continue
        
        # Separación en forward_frame
        objetivo_forward = tracking_jugada[
            (tracking_jugada['frameId'] == forward_frame) &
            (tracking_jugada['nflId'] == objetivo_id)
        ]
        
        defensores_forward = tracking_jugada[
            (tracking_jugada['frameId'] == forward_frame) &
            (tracking_jugada['pff_role'] == 'Coverage')
        ]
        
        if len(objetivo_forward) == 0 or len(defensores_forward) == 0:
            continue
        
        obj_x, obj_y = objetivo_forward.iloc[0]['x'], objetivo_forward.iloc[0]['y']
        
        defensores_forward_copy = defensores_forward.copy()
        defensores_forward_copy['dist'] = np.sqrt(
            (defensores_forward_copy['x'] - obj_x)**2 +
            (defensores_forward_copy['y'] - obj_y)**2
        )
        
        sep_forward = defensores_forward_copy['dist'].min()
        
        # Separación 5 cuadros antes (0.5s)
        frame_antes = forward_frame - 5
        
        objetivo_antes = tracking_jugada[
            (tracking_jugada['frameId'] == frame_antes) &
            (tracking_jugada['nflId'] == objetivo_id)
        ]
        
        defensores_antes = tracking_jugada[
            (tracking_jugada['frameId'] == frame_antes) &
            (tracking_jugada['pff_role'] == 'Coverage')
        ]
        
        if len(objetivo_antes) == 0 or len(defensores_antes) == 0:
            tendencia = 'desconocida'
            cambio_sep = None
        else:
            obj_x_antes, obj_y_antes = objetivo_antes.iloc[0]['x'], objetivo_antes.iloc[0]['y']
            
            defensores_antes_copy = defensores_antes.copy()
            defensores_antes_copy['dist'] = np.sqrt(
                (defensores_antes_copy['x'] - obj_x_antes)**2 +
                (defensores_antes_copy['y'] - obj_y_antes)**2
            )
            
            sep_antes = defensores_antes_copy['dist'].min()
            cambio_sep = sep_forward - sep_antes
            
            if cambio_sep > TENDENCIA_UMBRAL_YD:
                tendencia = 'abriendose'
            elif cambio_sep < -TENDENCIA_UMBRAL_YD:
                tendencia = 'cerrandose'
            else:
                tendencia = 'estable'
        
        # Franja de separación
        if sep_forward < SEP_CERRADA_YD:
            franja_sep = 'cerrado'
        elif sep_forward >= ABIERTO_YD:
            franja_sep = 'abierto'
        else:
            franja_sep = 'disputado'
        
        # Completo
        completo = (pass_result == 'C')
        
        resultados.append({
            'gameId': game_id,
            'playId': play_id,
            'objetivo_id': objetivo_id,
            'objetivo_nombre': objetivo_nombre,
            'aproximado': aproximado,
            'sep_forward': sep_forward,
            'franja_sep': franja_sep,
            'tendencia': tendencia,
            'cambio_sep': cambio_sep,
            'completo': completo
        })
    
    return pd.DataFrame(resultados)


def sigue_libre_por_jugada(cuadros, plays, players, pff):
    """
    Devuelve para cada jugada si el objetivo está abierto al lanzar
    Función pública para la síntesis de A
    
    Returns:
        DataFrame con: gameId, playId, valido, sigue_libre
    """
    ventaja = construir(cuadros, plays, players, pff)
    
    # sigue_libre = objetivo a >= ABIERTO_YD en el lanzamiento
    ventaja['sigue_libre'] = ventaja['sep_forward'] >= ABIERTO_YD
    ventaja['valido'] = True
    
    return ventaja[['gameId', 'playId', 'valido', 'sigue_libre']]


def bootstrap_intervalo(data, reps=BOOTSTRAP_REPS, nivel=IC_NIVEL):
    """
    Calcula intervalo de confianza por bootstrap
    
    Args:
        data: array de valores (0 o 1 para porcentajes)
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
        medias.append(muestra.mean() * 100)  # convertir a %
    
    # Percentiles
    alpha = 1 - nivel
    bajo = np.percentile(medias, alpha/2 * 100)
    alto = np.percentile(medias, (1 - alpha/2) * 100)
    
    return bajo, alto


def resumen(ventaja_df, ventaja_robustez_df=None, filtro='decisivo'):
    """
    Genera resumen de ventaja al lanzar
    
    Args:
        ventaja_df: DataFrame de construir() sin respaldo (solo nombres encontrados)
        ventaja_robustez_df: DataFrame con respaldo para tabla de robustez (opcional)
        filtro: nombre del filtro (para metadata)
    
    Returns:
        dict con: filtro, n_por_nombre, n_sin_objetivo, n_aproximado, 
                  tabla_principal, tabla_robustez, insight
    """
    n_por_nombre = len(ventaja_df)
    n_aproximado = 0
    
    # Si hay tabla de robustez, calcular aproximados
    if ventaja_robustez_df is not None:
        n_total_robustez = len(ventaja_robustez_df)
        n_aproximado = n_total_robustez - n_por_nombre
    
    # Tabla principal (solo objetivos por nombre)
    tabla_principal = {
        'por_separacion': [],
        'por_tendencia': []
    }
    
    # Por separación
    for franja in ['cerrado', 'disputado', 'abierto']:
        subset = ventaja_df[ventaja_df['franja_sep'] == franja]
        if len(subset) == 0:
            continue
        
        n = len(subset)
        completos = subset['completo'].astype(int)
        pct_completo = completos.mean() * 100
        
        ic_bajo, ic_alto = bootstrap_intervalo(completos.values)
        
        tabla_principal['por_separacion'].append({
            'franja': franja,
            'n': n,
            'pct_completo': round(pct_completo, 1),
            'ic': [round(ic_bajo, 1), round(ic_alto, 1)] if ic_bajo is not None else None
        })
    
    # Por tendencia
    for tend in ['abriendose', 'estable', 'cerrandose']:
        subset = ventaja_df[ventaja_df['tendencia'] == tend]
        if len(subset) == 0:
            continue
        
        n = len(subset)
        completos = subset['completo'].astype(int)
        pct_completo = completos.mean() * 100
        
        ic_bajo, ic_alto = bootstrap_intervalo(completos.values)
        
        tabla_principal['por_tendencia'].append({
            'tendencia': tend,
            'n': n,
            'pct_completo': round(pct_completo, 1),
            'ic': [round(ic_bajo, 1), round(ic_alto, 1)] if ic_bajo is not None else None
        })
    
    # Tabla de robustez (con respaldo)
    tabla_robustez = None
    if ventaja_robustez_df is not None:
        tabla_robustez = {
            'por_separacion': [],
            'por_tendencia': []
        }
        
        # Por separación
        for franja in ['cerrado', 'disputado', 'abierto']:
            subset = ventaja_robustez_df[ventaja_robustez_df['franja_sep'] == franja]
            if len(subset) == 0:
                continue
            
            n = len(subset)
            completos = subset['completo'].astype(int)
            pct_completo = completos.mean() * 100
            
            ic_bajo, ic_alto = bootstrap_intervalo(completos.values)
            
            tabla_robustez['por_separacion'].append({
                'franja': franja,
                'n': n,
                'pct_completo': round(pct_completo, 1),
                'ic': [round(ic_bajo, 1), round(ic_alto, 1)] if ic_bajo is not None else None
            })
        
        # Por tendencia
        for tend in ['abriendose', 'estable', 'cerrandose']:
            subset = ventaja_robustez_df[ventaja_robustez_df['tendencia'] == tend]
            if len(subset) == 0:
                continue
            
            n = len(subset)
            completos = subset['completo'].astype(int)
            pct_completo = completos.mean() * 100
            
            ic_bajo, ic_alto = bootstrap_intervalo(completos.values)
            
            tabla_robustez['por_tendencia'].append({
                'tendencia': tend,
                'n': n,
                'pct_completo': round(pct_completo, 1),
                'ic': [round(ic_bajo, 1), round(ic_alto, 1)] if ic_bajo is not None else None
            })
    
    # Insight (de tabla principal)
    # Comparar abierto vs cerrado
    abierto_pct = next((x['pct_completo'] for x in tabla_principal['por_separacion'] if x['franja'] == 'abierto'), None)
    cerrado_pct = next((x['pct_completo'] for x in tabla_principal['por_separacion'] if x['franja'] == 'cerrado'), None)
    
    # Comparar abriéndose vs cerrándose
    abriendose_pct = next((x['pct_completo'] for x in tabla_principal['por_tendencia'] if x['tendencia'] == 'abriendose'), None)
    cerrandose_pct = next((x['pct_completo'] for x in tabla_principal['por_tendencia'] if x['tendencia'] == 'cerrandose'), None)
    
    if abierto_pct is not None and cerrado_pct is not None:
        diff_sep = abierto_pct - cerrado_pct
    else:
        diff_sep = None
    
    if abriendose_pct is not None and cerrandose_pct is not None:
        diff_tend = abriendose_pct - cerrandose_pct
    else:
        diff_tend = None
    
    if diff_sep is not None and diff_tend is not None:
        insight = (f"La ventaja al lanzar predice conversión: +{diff_sep:.1f} puntos con objetivo abierto "
                  f"(≥{ABIERTO_YD} yd); +{diff_tend:.1f} puntos abriéndose vs cerrándose.")
    elif diff_sep is not None:
        insight = f"Objetivo abierto (≥{ABIERTO_YD} yd): +{diff_sep:.1f} puntos de conversión."
    elif diff_tend is not None:
        insight = f"Abriéndose vs cerrándose: +{diff_tend:.1f} puntos de conversión."
    else:
        insight = "Datos insuficientes para insight."
    
    return {
        'filtro': filtro,
        'n_por_nombre': n_por_nombre,
        'n_aproximado': n_aproximado,
        'tabla_principal': tabla_principal,
        'tabla_robustez': tabla_robustez,
        'insight': insight
    }
