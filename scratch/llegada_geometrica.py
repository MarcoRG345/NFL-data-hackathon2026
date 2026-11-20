"""
Implementación y validación de llegada geométrica del pase
"""
import pandas as pd
import numpy as np
import random

print("="*80)
print("LLEGADA GEOMÉTRICA DEL PASE - IMPLEMENTACIÓN Y VALIDACIÓN")
print("="*80)

# Cargar datos
print("\n0. CARGANDO DATOS...")
plays = pd.read_csv('data/plays.csv')
players = pd.read_csv('data/players.csv')
pff = pd.read_csv('data/pffScoutingData.csv')

# Semana 1
juegos_semana1 = sorted(plays['gameId'].unique())[:16]
plays_semana1 = plays[plays['gameId'].isin(juegos_semana1)].copy()

print(f"  Jugadas semana 1: {len(plays_semana1)}")

# Cargar tracking
tracking_list = []
for juego_id in juegos_semana1:
    tracking_juego = pd.read_csv(f'data/tracking/tracking_{juego_id}.csv')
    tracking_list.append(tracking_juego)

tracking = pd.concat(tracking_list, ignore_index=True)
print(f"  Total cuadros: {len(tracking)}")

# Merge con PFF para roles
tracking = tracking.merge(
    pff[['gameId', 'playId', 'nflId', 'pff_role']],
    on=['gameId', 'playId', 'nflId'],
    how='left'
)
print(f"  Merge con PFF completado")

# 1. VERIFICAR QUE EL BALÓN TIENE CUADROS DESPUÉS DE pass_forward
print("\n1. VERIFICAR BALÓN DESPUÉS DE pass_forward")

# Jugadas con pass_forward
jugadas_con_forward = tracking[tracking['event'] == 'pass_forward'][['gameId', 'playId']].drop_duplicates()
print(f"  Jugadas con pass_forward: {len(jugadas_con_forward)}")

# Para cada jugada, verificar si hay balón después de pass_forward
verificaciones = []

for _, jugada in jugadas_con_forward.head(20).iterrows():  # Muestra de 20
    game_id = jugada['gameId']
    play_id = jugada['playId']
    
    # Cuadro de pass_forward
    forward_frame = tracking[
        (tracking['gameId'] == game_id) &
        (tracking['playId'] == play_id) &
        (tracking['event'] == 'pass_forward')
    ]['frameId'].min()
    
    # Balón después de forward
    balon_despues = tracking[
        (tracking['gameId'] == game_id) &
        (tracking['playId'] == play_id) &
        (tracking['team'] == 'football') &
        (tracking['frameId'] > forward_frame)
    ]
    
    verificaciones.append({
        'gameId': game_id,
        'playId': play_id,
        'forward_frame': forward_frame,
        'cuadros_balon_despues': len(balon_despues),
        'tiene_balon': len(balon_despues) > 0
    })

df_verif = pd.DataFrame(verificaciones)
print(f"\n  Muestra de 20 jugadas con pass_forward:")
print(f"    Con balón después: {df_verif['tiene_balon'].sum()}")
print(f"    Sin balón después: {(~df_verif['tiene_balon']).sum()}")
print(f"    Promedio cuadros balón: {df_verif['cuadros_balon_despues'].mean():.1f}")

if df_verif['tiene_balon'].sum() == 0:
    print("\n  ERROR: El balon NO tiene cuadros despues de pass_forward")
    print("  DETENIENDO EJECUCION")
    exit(1)

print("\n  OK: El balon SI tiene cuadros despues de pass_forward")

# 2. IMPLEMENTAR LLEGADA GEOMÉTRICA
print("\n2. IMPLEMENTAR LLEGADA GEOMÉTRICA")

def calcular_llegada_geometrica(tracking_jugada, forward_frame, game_id, play_id):
    """
    Calcula llegada geométrica según reglas:
    1. Primer cuadro ≥ 3 frames (0.3s) después de forward donde balón está a ≤1.5 yd de no-QB
    2. Si no existe, el cuadro con distancia mínima dentro de 40 frames (4s)
    """
    # Balón después de forward
    balon = tracking_jugada[
        (tracking_jugada['team'] == 'football') &
        (tracking_jugada['frameId'] > forward_frame)
    ].copy()
    
    if len(balon) == 0:
        return None, None, 'sin_balon'
    
    # QB de la jugada
    qb = tracking_jugada[
        (tracking_jugada['pff_role'] == 'Pass') &
        (tracking_jugada['frameId'] == forward_frame)
    ]['nflId'].values
    
    qb_id = qb[0] if len(qb) > 0 else None
    
    # Filtrar balón >= 3 frames (0.3s) después
    balon_min = balon[balon['frameId'] >= forward_frame + 3]
    
    if len(balon_min) == 0:
        return None, None, 'sin_balon_min'
    
    # Para cada cuadro del balón, calcular distancia a jugadores no-QB
    resultados = []
    
    for _, cuadro_balon in balon_min.iterrows():
        frame_id = cuadro_balon['frameId']
        balon_x, balon_y = cuadro_balon['x'], cuadro_balon['y']
        frames_desde_forward = frame_id - forward_frame
        
        # Jugadores en ese cuadro (excluir QB y balón)
        jugadores = tracking_jugada[
            (tracking_jugada['frameId'] == frame_id) &
            (tracking_jugada['team'] != 'football')
        ].copy()
        
        if qb_id is not None:
            jugadores = jugadores[jugadores['nflId'] != qb_id]
        
        if len(jugadores) == 0:
            continue
        
        # Distancia mínima
        jugadores['dist_balon'] = np.sqrt(
            (jugadores['x'] - balon_x)**2 + 
            (jugadores['y'] - balon_y)**2
        )
        
        dist_min = jugadores['dist_balon'].min()
        jugador_cercano = jugadores.loc[jugadores['dist_balon'].idxmin(), 'nflId']
        
        resultados.append({
            'frameId': frame_id,
            'frames_desde_forward': frames_desde_forward,
            'dist_min': dist_min,
            'jugador_cercano': jugador_cercano
        })
    
    if len(resultados) == 0:
        return None, None, 'sin_jugadores'
    
    df_res = pd.DataFrame(resultados)
    
    # Regla 1: primer cuadro con dist ≤ 1.5 yd
    regla1 = df_res[df_res['dist_min'] <= 1.5]
    if len(regla1) > 0:
        llegada = regla1.iloc[0]
        return int(llegada['frameId']), llegada['jugador_cercano'], 'regla1_distancia'
    
    # Regla 2: distancia mínima dentro de 40 frames (4s)
    df_4s = df_res[df_res['frames_desde_forward'] <= 40]
    if len(df_4s) > 0:
        llegada = df_4s.loc[df_4s['dist_min'].idxmin()]
        return int(llegada['frameId']), llegada['jugador_cercano'], 'regla2_minima'
    
    return None, None, 'timeout'

# Aplicar a todas las jugadas con pass_forward
print("  Calculando llegada para jugadas con pass_forward...")

llegadas = []
for _, jugada_info in jugadas_con_forward.iterrows():
    game_id = jugada_info['gameId']
    play_id = jugada_info['playId']
    
    tracking_jugada = tracking[
        (tracking['gameId'] == game_id) &
        (tracking['playId'] == play_id)
    ]
    
    # Frame de forward
    forward_frame = tracking_jugada[
        tracking_jugada['event'] == 'pass_forward'
    ]['frameId'].min()
    
    if pd.isna(forward_frame):
        continue
    
    llegada_frame, jugador_id, regla = calcular_llegada_geometrica(
        tracking_jugada, forward_frame, game_id, play_id
    )
    
    llegadas.append({
        'gameId': game_id,
        'playId': play_id,
        'forward_frame': int(forward_frame),
        'llegada_frame': llegada_frame,
        'jugador_llegada': jugador_id,
        'regla_usada': regla
    })

df_llegadas = pd.DataFrame(llegadas)
print(f"\n  Total jugadas procesadas: {len(df_llegadas)}")
print(f"\n  Distribución de reglas:")
print(df_llegadas['regla_usada'].value_counts())

exitosas = df_llegadas[df_llegadas['llegada_frame'].notna()]
print(f"\n  Llegadas exitosas: {len(exitosas)} ({len(exitosas)/len(df_llegadas)*100:.1f}%)")

# 3. VALIDAR CONTRA LAS 50 JUGADAS CON pass_arrived
print("\n3. VALIDACIÓN CONTRA pass_arrived")

# Jugadas con pass_arrived real
jugadas_arrived = tracking[tracking['event'] == 'pass_arrived'][['gameId', 'playId', 'frameId']].copy()
jugadas_arrived.columns = ['gameId', 'playId', 'arrived_frame']

# Merge con llegadas geométricas
validacion = df_llegadas.merge(
    jugadas_arrived,
    on=['gameId', 'playId'],
    how='inner'
)

print(f"  Jugadas para validar: {len(validacion)}")

if len(validacion) > 0:
    validacion['diff_frames'] = abs(validacion['llegada_frame'] - validacion['arrived_frame'])
    
    print(f"\n  Diferencia en cuadros (geométrica vs pass_arrived):")
    print(f"    Mediana: {validacion['diff_frames'].median():.1f}")
    print(f"    P90: {validacion['diff_frames'].quantile(0.9):.1f}")
    print(f"    Media: {validacion['diff_frames'].mean():.1f}")
    print(f"    Max: {validacion['diff_frames'].max():.0f}")
    
    # Casos dentro de ±2 cuadros
    dentro_2 = (validacion['diff_frames'] <= 2).sum()
    print(f"\n  Dentro de ±2 cuadros: {dentro_2}/{len(validacion)} ({dentro_2/len(validacion)*100:.1f}%)")

# 4. TIEMPO DE VUELO Y % CON LLEGADA
print("\n4. TIEMPO DE VUELO Y COBERTURA")

# Calcular tiempo de vuelo en jugadas exitosas
exitosas_con_tiempo = exitosas.copy()
exitosas_con_tiempo['cuadros_vuelo'] = exitosas_con_tiempo['llegada_frame'] - exitosas_con_tiempo['forward_frame']
exitosas_con_tiempo['tiempo_vuelo_seg'] = exitosas_con_tiempo['cuadros_vuelo'] / 10.0

print(f"  Tiempo de vuelo (segundos):")
print(f"    Mediana: {exitosas_con_tiempo['tiempo_vuelo_seg'].median():.2f} s")
print(f"    P10: {exitosas_con_tiempo['tiempo_vuelo_seg'].quantile(0.1):.2f} s")
print(f"    P90: {exitosas_con_tiempo['tiempo_vuelo_seg'].quantile(0.9):.2f} s")
print(f"    Media: {exitosas_con_tiempo['tiempo_vuelo_seg'].mean():.2f} s")

# % de jugadas con pase que obtienen llegada
jugadas_pase = plays_semana1[plays_semana1['passResult'].notna()]
pct_cobertura = (len(exitosas) / len(jugadas_pase) * 100)
print(f"\n  Cobertura:")
print(f"    Jugadas con passResult válido: {len(jugadas_pase)}")
print(f"    Llegadas geométricas calculadas: {len(exitosas)}")
print(f"    Porcentaje: {pct_cobertura:.1f}%")

# 5. OBJETIVO VS playDescription CON LLEGADA GEOMÉTRICA
print("\n5. OBJETIVO VS playDescription (CON LLEGADA GEOMÉTRICA)")

# El tracking ya tiene PFF mergeado, solo falta players
tracking_completo = tracking.merge(
    players[['nflId', 'displayName']],
    on='nflId',
    how='left'
)
tracking_completo.loc[tracking_completo['team'] == 'football', 'displayName'] = 'football'

# Merge llegadas con plays
llegadas_validas = df_llegadas[df_llegadas['llegada_frame'].notna()].merge(
    plays_semana1[['gameId', 'playId', 'passResult', 'playDescription']],
    on=['gameId', 'playId'],
    how='inner'
)

# Filtrar C o I
llegadas_ci = llegadas_validas[llegadas_validas['passResult'].isin(['C', 'I'])]
print(f"  Llegadas geométricas con passResult C o I: {len(llegadas_ci)}")

# Muestra aleatoria de 20
random.seed(42)
if len(llegadas_ci) >= 20:
    muestra = llegadas_ci.sample(n=20)
else:
    muestra = llegadas_ci

coincidencias = 0
casos_procesados = 0
ejemplos = []

for _, jugada in muestra.iterrows():
    game_id = jugada['gameId']
    play_id = jugada['playId']
    llegada_frame = jugada['llegada_frame']
    descripcion = jugada['playDescription']
    
    # Receptores en frame de llegada
    receptores = tracking_completo[
        (tracking_completo['gameId'] == game_id) &
        (tracking_completo['playId'] == play_id) &
        (tracking_completo['frameId'] == llegada_frame) &
        (tracking_completo['pff_role'] == 'Pass Route')
    ].copy()
    
    # Balón en llegada
    balon = tracking_completo[
        (tracking_completo['gameId'] == game_id) &
        (tracking_completo['playId'] == play_id) &
        (tracking_completo['frameId'] == llegada_frame) &
        (tracking_completo['displayName'] == 'football')
    ]
    
    if len(balon) == 0 or len(receptores) == 0:
        continue
    
    casos_procesados += 1
    
    # Distancia al balón
    balon_x, balon_y = balon.iloc[0]['x'], balon.iloc[0]['y']
    receptores.loc[:, 'dist_balon'] = np.sqrt(
        (receptores['x'] - balon_x)**2 + 
        (receptores['y'] - balon_y)**2
    )
    
    objetivo = receptores.loc[receptores['dist_balon'].idxmin()]
    objetivo_nombre = objetivo['displayName']
    
    # Apellido
    apellido_objetivo = objetivo_nombre.split()[-1] if pd.notna(objetivo_nombre) and ' ' in objetivo_nombre else objetivo_nombre
    
    # Comparar con playDescription
    coincide = False
    nombre_en_desc = None
    
    if pd.notna(descripcion) and ' to ' in descripcion:
        texto_despues_to = descripcion.split(' to ', 1)[1]
        palabras = texto_despues_to.split()
        if palabras:
            nombre_en_desc = palabras[0]
            if '.' in nombre_en_desc:
                apellido_desc = nombre_en_desc.split('.')[-1]
                if apellido_objetivo and apellido_desc.lower() == apellido_objetivo.lower():
                    coincide = True
                    coincidencias += 1
    
    if len(ejemplos) < 5:
        ejemplos.append({
            'objetivo': objetivo_nombre,
            'apellido': apellido_objetivo,
            'nombre_desc': nombre_en_desc,
            'coincide': coincide,
            'descripcion': descripcion[:80] if pd.notna(descripcion) else ''
        })

porcentaje = (coincidencias / casos_procesados * 100) if casos_procesados > 0 else 0

print(f"\n  Casos procesados: {casos_procesados}")
print(f"  Coincidencias: {coincidencias}")
print(f"  Porcentaje: {porcentaje:.1f}%")

print(f"\n  Ejemplos (primeros 5):")
for i, ej in enumerate(ejemplos, 1):
    marca = 'OK' if ej['coincide'] else 'X'
    print(f"    {i}. {ej['objetivo']} -> {ej['nombre_desc']} {marca}")
    print(f"       {ej['descripcion']}...")

# 6. DEFINICIÓN FINAL
print("\n" + "="*80)
print("6. DEFINICIÓN FINAL PARA pregunta.md")
print("="*80)

definicion = """
Llegada del pase (geométrica):
- Después de pass_forward (o 0.5 s desde snap si falta), la llegada es el primer cuadro (≥ 0.3 s) donde el balón está a ≤ 1.5 yd de cualquier jugador no-QB.
- Si no existe, usar el cuadro con distancia mínima balón–jugador dentro de 4 s desde pass_forward.
- Cobertura: {:.1f}% de pases válidos. Validación: mediana {:.1f} cuadros vs pass_arrived (n=50).
""".format(pct_cobertura, validacion['diff_frames'].median() if len(validacion) > 0 else 0)

print(definicion)

# Guardar resultados
resultados = {
    'total_llegadas': len(exitosas),
    'cobertura_pct': pct_cobertura,
    'tiempo_vuelo_mediana': exitosas_con_tiempo['tiempo_vuelo_seg'].median(),
    'tiempo_vuelo_p10': exitosas_con_tiempo['tiempo_vuelo_seg'].quantile(0.1),
    'tiempo_vuelo_p90': exitosas_con_tiempo['tiempo_vuelo_seg'].quantile(0.9),
    'validacion_mediana': validacion['diff_frames'].median() if len(validacion) > 0 else None,
    'validacion_p90': validacion['diff_frames'].quantile(0.9) if len(validacion) > 0 else None,
    'objetivo_coincidencia': porcentaje,
    'objetivo_n': casos_procesados,
    'reglas': df_llegadas['regla_usada'].value_counts().to_dict()
}

print("\n" + "="*80)
print("ANÁLISIS COMPLETADO")
print("="*80)
