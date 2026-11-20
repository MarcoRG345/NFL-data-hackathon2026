"""
P3 revisado: Ventaja al lanzar
El tracking se corta 0.5s después de pass_forward, así que analizamos
la separación del objetivo EN el lanzamiento y su tendencia previa
"""
import pandas as pd
import numpy as np
import random

print("="*80)
print("P3 REVISADO: VENTAJA AL LANZAR")
print("="*80)

# Cargar datos
plays = pd.read_csv('data/plays.csv')
players = pd.read_csv('data/players.csv')
pff = pd.read_csv('data/pffScoutingData.csv')

# Semana 1
juegos_semana1 = sorted(plays['gameId'].unique())[:16]
plays_semana1 = plays[plays['gameId'].isin(juegos_semana1)].copy()

# Cargar tracking
tracking_list = []
for juego_id in juegos_semana1:
    tracking_juego = pd.read_csv(f'data/tracking/tracking_{juego_id}.csv')
    tracking_list.append(tracking_juego)

tracking = pd.concat(tracking_list, ignore_index=True)

# Merge con PFF y players
tracking = tracking.merge(
    pff[['gameId', 'playId', 'nflId', 'pff_role']],
    on=['gameId', 'playId', 'nflId'],
    how='left'
)

tracking = tracking.merge(
    players[['nflId', 'displayName']],
    on='nflId',
    how='left'
)

print(f"Total cuadros: {len(tracking)}")

# 1. IDENTIFICAR OBJETIVO POR playDescription
print("\n1. IDENTIFICAR OBJETIVO POR playDescription")

def extraer_objetivo_de_descripcion(descripcion):
    """Extrae apellido del receptor objetivo de playDescription"""
    if pd.isna(descripcion) or ' to ' not in descripcion:
        return None
    
    texto_despues_to = descripcion.split(' to ', 1)[1]
    palabras = texto_despues_to.split()
    if not palabras:
        return None
    
    nombre = palabras[0]
    if '.' in nombre:
        apellido = nombre.split('.')[-1]
        return apellido
    return nombre

# Aplicar a plays
plays_semana1['apellido_objetivo'] = plays_semana1['playDescription'].apply(extraer_objetivo_de_descripcion)

con_objetivo = plays_semana1['apellido_objetivo'].notna().sum()
print(f"Jugadas con objetivo identificable: {con_objetivo}/{len(plays_semana1)} ({con_objetivo/len(plays_semana1)*100:.1f}%)")

# 2. CALCULAR SEPARACIÓN Y TENDENCIA POR PASE
print("\n2. CALCULAR SEPARACIÓN Y TENDENCIA EN pass_forward")

# Jugadas con pass_forward y objetivo
jugadas_forward = tracking[tracking['event'] == 'pass_forward'][['gameId', 'playId', 'frameId']].copy()
jugadas_forward.columns = ['gameId', 'playId', 'forward_frame']

jugadas_forward = jugadas_forward.merge(
    plays_semana1[['gameId', 'playId', 'apellido_objetivo', 'passResult', 'playDescription']],
    on=['gameId', 'playId'],
    how='left'
)

# Solo jugadas con objetivo identificable
jugadas_con_objetivo = jugadas_forward[jugadas_forward['apellido_objetivo'].notna()].copy()
print(f"Jugadas con forward y objetivo: {len(jugadas_con_objetivo)}")

# Para cada jugada, calcular separación en forward y tendencia
resultados = []

for _, jugada in jugadas_con_objetivo.iterrows():
    game_id = jugada['gameId']
    play_id = jugada['playId']
    forward_frame = jugada['forward_frame']
    apellido_objetivo = jugada['apellido_objetivo']
    pass_result = jugada['passResult']
    
    # Encontrar nflId del objetivo comparando apellidos
    tracking_jugada = tracking[
        (tracking['gameId'] == game_id) &
        (tracking['playId'] == play_id)
    ]
    
    receptores = tracking_jugada[
        (tracking_jugada['pff_role'] == 'Pass Route') &
        (tracking_jugada['displayName'].notna())
    ].copy()
    
    if len(receptores) == 0:
        continue
    
    # Buscar receptor por apellido
    receptores['apellido'] = receptores['displayName'].apply(
        lambda x: x.split()[-1] if pd.notna(x) and ' ' in x else x
    )
    
    objetivo_matches = receptores[
        receptores['apellido'].str.lower() == apellido_objetivo.lower()
    ]
    
    if len(objetivo_matches) == 0:
        continue
    
    objetivo_id = objetivo_matches['nflId'].iloc[0]
    
    # Separación en forward_frame
    # Defensores en forward_frame
    defensores_forward = tracking_jugada[
        (tracking_jugada['frameId'] == forward_frame) &
        (tracking_jugada['pff_role'] == 'Coverage')
    ]
    
    objetivo_forward = tracking_jugada[
        (tracking_jugada['frameId'] == forward_frame) &
        (tracking_jugada['nflId'] == objetivo_id)
    ]
    
    if len(objetivo_forward) == 0 or len(defensores_forward) == 0:
        continue
    
    obj_x, obj_y = objetivo_forward.iloc[0]['x'], objetivo_forward.iloc[0]['y']
    
    # Distancia al defensor más cercano
    defensores_forward['dist'] = np.sqrt(
        (defensores_forward['x'] - obj_x)**2 +
        (defensores_forward['y'] - obj_y)**2
    )
    
    sep_forward = defensores_forward['dist'].min()
    
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
        
        defensores_antes['dist'] = np.sqrt(
            (defensores_antes['x'] - obj_x_antes)**2 +
            (defensores_antes['y'] - obj_y_antes)**2
        )
        
        sep_antes = defensores_antes['dist'].min()
        cambio_sep = sep_forward - sep_antes
        
        # Tendencia
        if cambio_sep > 0.5:
            tendencia = 'abriendose'
        elif cambio_sep < -0.5:
            tendencia = 'cerrandose'
        else:
            tendencia = 'estable'
    
    # Línea de golpeo para profundidad
    qb_snap = tracking_jugada[
        (tracking_jugada['event'] == 'ball_snap') &
        (tracking_jugada['pff_role'] == 'Pass')
    ]
    
    if len(qb_snap) > 0:
        linea_golpeo = qb_snap['x'].iloc[0]
        profundidad = obj_x - linea_golpeo
    else:
        profundidad = None
    
    resultados.append({
        'gameId': game_id,
        'playId': play_id,
        'objetivo_id': objetivo_id,
        'apellido_objetivo': apellido_objetivo,
        'sep_forward': sep_forward,
        'cambio_sep': cambio_sep,
        'tendencia': tendencia,
        'passResult': pass_result,
        'profundidad': profundidad
    })

df_ventaja = pd.DataFrame(resultados)
print(f"Pases analizados: {len(df_ventaja)}")

# 3. % COMPLETO POR FRANJA DE SEPARACIÓN
print("\n3. % COMPLETO POR FRANJA DE SEPARACIÓN AL LANZAR")

# Solo C e I
df_ci = df_ventaja[df_ventaja['passResult'].isin(['C', 'I'])].copy()
df_ci['completo'] = df_ci['passResult'] == 'C'

# Franja de separación
df_ci['franja_sep'] = pd.cut(
    df_ci['sep_forward'],
    bins=[0, 1, 2, 3, 5, 100],
    labels=['0-1', '1-2', '2-3', '3-5', '5+'],
    include_lowest=True
)

print("\nPor franja de separación al lanzar:")
for franja in ['0-1', '1-2', '2-3', '3-5', '5+']:
    subset = df_ci[df_ci['franja_sep'] == franja]
    if len(subset) > 0:
        pct_completo = (subset['completo'].sum() / len(subset) * 100)
        print(f"  {franja} yd: {pct_completo:.1f}% completo (n={len(subset)})")

# 4. % COMPLETO POR TENDENCIA
print("\nPor tendencia (0.5s antes del lanzamiento):")
for tendencia in ['abriendose', 'estable', 'cerrandose']:
    subset = df_ci[df_ci['tendencia'] == tendencia]
    if len(subset) > 0:
        pct_completo = (subset['completo'].sum() / len(subset) * 100)
        cambio_medio = subset['cambio_sep'].mean() if 'cambio_sep' in subset.columns else 0
        print(f"  {tendencia}: {pct_completo:.1f}% completo (n={len(subset)}, cambio medio: {cambio_medio:+.2f} yd)")

# 5. sigue_libre_por_jugada (ahora = ventaja al lanzar)
print("\n4. sigue_libre_por_jugada() - AHORA: VENTAJA AL LANZAR")

ABIERTO_YD = 3.0

df_ventaja['sigue_libre'] = df_ventaja['sep_forward'] >= ABIERTO_YD
df_ventaja['valido'] = df_ventaja['sep_forward'].notna()

sigue_libre_data = df_ventaja[['gameId', 'playId', 'valido', 'sigue_libre']].copy()

print(f"\nJugadas con ventaja al lanzar (>= {ABIERTO_YD} yd): {df_ventaja['sigue_libre'].sum()}/{len(df_ventaja)} ({df_ventaja['sigue_libre'].sum()/len(df_ventaja)*100:.1f}%)")

# Cruzar con passResult
df_libre_result = df_ventaja[df_ventaja['passResult'].isin(['C', 'I'])].copy()
df_libre_result['completo'] = df_libre_result['passResult'] == 'C'

con_ventaja = df_libre_result[df_libre_result['sigue_libre']]
sin_ventaja = df_libre_result[~df_libre_result['sigue_libre']]

if len(con_ventaja) > 0:
    pct_con = (con_ventaja['completo'].sum() / len(con_ventaja) * 100)
    print(f"  Con ventaja (>={ABIERTO_YD} yd): {pct_con:.1f}% completo (n={len(con_ventaja)})")

if len(sin_ventaja) > 0:
    pct_sin = (sin_ventaja['completo'].sum() / len(sin_ventaja) * 100)
    print(f"  Sin ventaja (<{ABIERTO_YD} yd): {pct_sin:.1f}% completo (n={len(sin_ventaja)})")

print("\n" + "="*80)
print("ANÁLISIS COMPLETADO")
print("="*80)

# Guardar resultados para reportar
print("\nRESUMEN PARA resultados-giro-aire.md:")
print(f"- Pases analizados: {len(df_ventaja)}")
print(f"- Identificación de objetivo: {con_objetivo} jugadas ({con_objetivo/len(plays_semana1)*100:.1f}%)")
print(f"- Ventaja al lanzar (>={ABIERTO_YD} yd): {df_ventaja['sigue_libre'].sum()}/{len(df_ventaja)} ({df_ventaja['sigue_libre'].sum()/len(df_ventaja)*100:.1f}%)")
