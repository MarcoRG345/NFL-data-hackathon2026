"""
Verificar si el tracking se corta poco después de pass_forward
"""
import pandas as pd
import numpy as np

print("="*80)
print("VERIFICACIÓN: CUADROS DISPONIBLES DESPUÉS DE pass_forward")
print("="*80)

# Cargar datos
plays = pd.read_csv('data/plays.csv')
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

# Merge con PFF
tracking = tracking.merge(
    pff[['gameId', 'playId', 'nflId', 'pff_role']],
    on=['gameId', 'playId', 'nflId'],
    how='left'
)

print(f"Total cuadros: {len(tracking)}")

# 1. CUADROS DISPONIBLES DESPUÉS DE pass_forward
print("\n1. CUADROS DISPONIBLES DESPUÉS DE pass_forward")

# Jugadas con pass_forward
jugadas_forward = tracking[tracking['event'] == 'pass_forward'][['gameId', 'playId', 'frameId']].copy()
jugadas_forward.columns = ['gameId', 'playId', 'forward_frame']

# Merge con plays para obtener passResult
jugadas_forward = jugadas_forward.merge(
    plays_semana1[['gameId', 'playId', 'passResult']],
    on=['gameId', 'playId'],
    how='left'
)

print(f"Jugadas con pass_forward: {len(jugadas_forward)}")

# Para cada jugada, contar cuadros después de forward
resultados = []

for _, jugada in jugadas_forward.iterrows():
    game_id = jugada['gameId']
    play_id = jugada['playId']
    forward_frame = jugada['forward_frame']
    pass_result = jugada['passResult']
    
    # Cuadros de la jugada después de forward
    cuadros_despues = tracking[
        (tracking['gameId'] == game_id) &
        (tracking['playId'] == play_id) &
        (tracking['frameId'] > forward_frame)
    ]['frameId'].nunique()
    
    # Cuadro máximo de la jugada
    max_frame = tracking[
        (tracking['gameId'] == game_id) &
        (tracking['playId'] == play_id)
    ]['frameId'].max()
    
    resultados.append({
        'gameId': game_id,
        'playId': play_id,
        'forward_frame': forward_frame,
        'max_frame': max_frame,
        'cuadros_despues': cuadros_despues,
        'passResult': pass_result
    })

df_cuadros = pd.DataFrame(resultados)

print("\nDistribución de cuadros disponibles después de pass_forward:")
print(f"  Mediana: {df_cuadros['cuadros_despues'].median():.0f}")
print(f"  P10: {df_cuadros['cuadros_despues'].quantile(0.1):.0f}")
print(f"  P90: {df_cuadros['cuadros_despues'].quantile(0.9):.0f}")
print(f"  Media: {df_cuadros['cuadros_despues'].mean():.1f}")
print(f"  Max: {df_cuadros['cuadros_despues'].max():.0f}")

# Por passResult
print("\nPor passResult:")
for result in ['C', 'I', 'S', 'R', 'IN']:
    subset = df_cuadros[df_cuadros['passResult'] == result]
    if len(subset) > 0:
        print(f"  {result} (n={len(subset)}): mediana {subset['cuadros_despues'].median():.0f}, "
              f"P90 {subset['cuadros_despues'].quantile(0.9):.0f}")

# Jugadas con ≤6 cuadros
con_pocos = (df_cuadros['cuadros_despues'] <= 6).sum()
print(f"\nJugadas con ≤6 cuadros después de forward: {con_pocos}/{len(df_cuadros)} ({con_pocos/len(df_cuadros)*100:.1f}%)")

# 2. PROFUNDIDAD DE LAS 50 JUGADAS CON pass_arrived
print("\n2. PROFUNDIDAD DE LAS 50 JUGADAS CON pass_arrived")

# Jugadas con pass_arrived
jugadas_arrived = tracking[tracking['event'] == 'pass_arrived'][['gameId', 'playId']].drop_duplicates()
print(f"Jugadas con pass_arrived: {len(jugadas_arrived)}")

# Para cada una, calcular profundidad (posición x del receptor objetivo en pass_arrived)
profundidades = []

for _, jugada in jugadas_arrived.iterrows():
    game_id = jugada['gameId']
    play_id = jugada['playId']
    
    # Frame de pass_arrived
    arrived_frame = tracking[
        (tracking['gameId'] == game_id) &
        (tracking['playId'] == play_id) &
        (tracking['event'] == 'pass_arrived')
    ]['frameId'].min()
    
    # Línea de golpeo (aprox: línea de scrimmage)
    # Usar la posición x del QB en ball_snap como referencia
    snap_qb = tracking[
        (tracking['gameId'] == game_id) &
        (tracking['playId'] == play_id) &
        (tracking['event'] == 'ball_snap') &
        (tracking['pff_role'] == 'Pass')
    ]
    
    if len(snap_qb) == 0:
        continue
    
    linea_golpeo = snap_qb['x'].iloc[0]
    
    # Balón en arrived
    balon = tracking[
        (tracking['gameId'] == game_id) &
        (tracking['playId'] == play_id) &
        (tracking['frameId'] == arrived_frame) &
        (tracking['team'] == 'football')
    ]
    
    if len(balon) == 0:
        continue
    
    balon_x = balon['x'].iloc[0]
    profundidad = balon_x - linea_golpeo
    
    profundidades.append({
        'gameId': game_id,
        'playId': play_id,
        'profundidad': profundidad
    })

df_prof = pd.DataFrame(profundidades)

if len(df_prof) > 0:
    print(f"\nProfundidad de pases con pass_arrived (n={len(df_prof)}):")
    print(f"  Mediana: {df_prof['profundidad'].median():.1f} yd")
    print(f"  P10: {df_prof['profundidad'].quantile(0.1):.1f} yd")
    print(f"  P90: {df_prof['profundidad'].quantile(0.9):.1f} yd")
    print(f"  Media: {df_prof['profundidad'].mean():.1f} yd")
    
    # Distribución por franja
    df_prof['franja'] = pd.cut(
        df_prof['profundidad'],
        bins=[-100, 5, 15, 100],
        labels=['corta (<5)', 'media (5-15)', 'larga (>15)']
    )
    print("\n  Por franja:")
    print(df_prof['franja'].value_counts())

print("\n" + "="*80)
print("ANÁLISIS COMPLETADO")
print("="*80)

# 3. BUSCAR COLUMNA DE RECEPTOR OBJETIVO
print("\n3. BUSCAR COLUMNA DE RECEPTOR OBJETIVO EN CSV")

print("\nColumnas en plays.csv:")
plays_cols = pd.read_csv('data/plays.csv', nrows=1).columns.tolist()
objetivo_cols = [c for c in plays_cols if 'target' in c.lower() or 'receiver' in c.lower()]
if objetivo_cols:
    print(f"  Columnas relacionadas con objetivo: {objetivo_cols}")
else:
    print("  No hay columnas con 'target' o 'receiver'")

print("\nColumnas en pffScoutingData.csv:")
pff_cols = pd.read_csv('data/pffScoutingData.csv', nrows=1).columns.tolist()
objetivo_cols = [c for c in pff_cols if 'target' in c.lower() or 'receiver' in c.lower()]
if objetivo_cols:
    print(f"  Columnas relacionadas con objetivo: {objetivo_cols}")
else:
    print("  No hay columnas con 'target' o 'receiver'")

print("\nColumnas en tracking (muestra):")
track_cols = tracking.columns.tolist()
objetivo_cols = [c for c in track_cols if 'target' in c.lower() or 'receiver' in c.lower()]
if objetivo_cols:
    print(f"  Columnas relacionadas con objetivo: {objetivo_cols}")
else:
    print("  No hay columnas con 'target' o 'receiver'")
