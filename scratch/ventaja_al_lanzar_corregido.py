"""
P3 revisado: Ventaja al lanzar - CORREGIDO
UNA fila por jugada con pase (C, I o IN)
"""
import pandas as pd
import numpy as np

print("="*80)
print("P3 REVISADO: VENTAJA AL LANZAR (UNA FILA POR JUGADA)")
print("="*80)

# Cargar datos
plays = pd.read_csv('data/plays.csv')
players = pd.read_csv('data/players.csv')
pff = pd.read_csv('data/pffScoutingData.csv')

# SEMANA 1 SOLAMENTE (como especifica la tarea)
juegos_semana1 = sorted(plays['gameId'].unique())[:16]
plays_semana1 = plays[plays['gameId'].isin(juegos_semana1)].copy()

print(f"Juegos de semana 1: {len(juegos_semana1)}")

# Cargar tracking semana 1
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

print(f"Total cuadros semana 1: {len(tracking)}")

# Función para extraer objetivo
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

# Jugadas con pase (C, I, IN) de semana 1
jugadas_pase = plays_semana1[plays_semana1['passResult'].isin(['C', 'I', 'IN'])].copy()
print(f"\nJugadas con pase (C, I, IN) en semana 1: {len(jugadas_pase)}")

# Extraer objetivo
jugadas_pase['apellido_objetivo'] = jugadas_pase['playDescription'].apply(extraer_objetivo_de_descripcion)
con_objetivo = jugadas_pase['apellido_objetivo'].notna().sum()
print(f"Jugadas con objetivo identificable: {con_objetivo} ({con_objetivo/len(jugadas_pase)*100:.1f}%)")

# Solo jugadas con objetivo identificable
jugadas_pase = jugadas_pase[jugadas_pase['apellido_objetivo'].notna()].copy()

# Calcular separación y tendencia POR JUGADA
resultados = []

for _, jugada in jugadas_pase.iterrows():
    game_id = jugada['gameId']
    play_id = jugada['playId']
    apellido_objetivo = jugada['apellido_objetivo']
    pass_result = jugada['passResult']
    
    # Frame de pass_forward
    forward_frames = tracking[
        (tracking['gameId'] == game_id) &
        (tracking['playId'] == play_id) &
        (tracking['event'] == 'pass_forward')
    ]['frameId']
    
    if len(forward_frames) == 0:
        continue
    
    forward_frame = forward_frames.min()
    
    # Tracking de esta jugada
    tracking_jugada = tracking[
        (tracking['gameId'] == game_id) &
        (tracking['playId'] == play_id)
    ]
    
    # Encontrar nflId del objetivo
    receptores = tracking_jugada[
        (tracking_jugada['pff_role'] == 'Pass Route') &
        (tracking_jugada['displayName'].notna())
    ].copy()
    
    if len(receptores) == 0:
        continue
    
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
        
        if cambio_sep > 0.5:
            tendencia = 'abriendose'
        elif cambio_sep < -0.5:
            tendencia = 'cerrandose'
        else:
            tendencia = 'estable'
    
    resultados.append({
        'gameId': game_id,
        'playId': play_id,
        'objetivo_id': objetivo_id,
        'apellido_objetivo': apellido_objetivo,
        'sep_forward': sep_forward,
        'cambio_sep': cambio_sep,
        'tendencia': tendencia,
        'passResult': pass_result
    })

df_ventaja = pd.DataFrame(resultados)
print(f"\nPases analizados (UNA fila por jugada): {len(df_ventaja)}")

# Calcular % completo
df_ventaja['completo'] = df_ventaja['passResult'] == 'C'

# Franjas de separación
df_ventaja['franja_sep'] = pd.cut(
    df_ventaja['sep_forward'],
    bins=[0, 1, 2, 3, 5, 100],
    labels=['0-1', '1-2', '2-3', '3-5', '5+'],
    include_lowest=True
)

print("\n% COMPLETO POR FRANJA DE SEPARACIÓN AL LANZAR:")
for franja in ['0-1', '1-2', '2-3', '3-5', '5+']:
    subset = df_ventaja[df_ventaja['franja_sep'] == franja]
    if len(subset) > 0:
        pct_completo = (subset['completo'].sum() / len(subset) * 100)
        print(f"  {franja} yd: {pct_completo:.1f}% completo (n={len(subset)})")

print("\n% COMPLETO POR TENDENCIA (0.5s antes del lanzamiento):")
for tendencia in ['abriendose', 'estable', 'cerrandose']:
    subset = df_ventaja[df_ventaja['tendencia'] == tendencia]
    if len(subset) > 0:
        pct_completo = (subset['completo'].sum() / len(subset) * 100)
        cambio_medio = subset['cambio_sep'].mean() if subset['cambio_sep'].notna().any() else 0
        print(f"  {tendencia}: {pct_completo:.1f}% completo (n={len(subset)}, cambio medio: {cambio_medio:+.2f} yd)")

# Ventaja al lanzar
ABIERTO_YD = 3.0
df_ventaja['sigue_libre'] = df_ventaja['sep_forward'] >= ABIERTO_YD

con_ventaja = df_ventaja[df_ventaja['sigue_libre']]
sin_ventaja = df_ventaja[~df_ventaja['sigue_libre']]

print("\nVENTAJA AL LANZAR (>= 3.0 yd):")
if len(con_ventaja) > 0:
    pct_con = (con_ventaja['completo'].sum() / len(con_ventaja) * 100)
    print(f"  Con ventaja: {pct_con:.1f}% completo (n={len(con_ventaja)})")

if len(sin_ventaja) > 0:
    pct_sin = (sin_ventaja['completo'].sum() / len(sin_ventaja) * 100)
    print(f"  Sin ventaja: {pct_sin:.1f}% completo (n={len(sin_ventaja)})")

print("\n" + "="*80)
print("ANÁLISIS COMPLETADO")
print("="*80)
