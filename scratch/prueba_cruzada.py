"""
Prueba cruzada para verificar eventos faltantes
"""
import pandas as pd
import os
from pathlib import Path

print("="*80)
print("PRUEBA CRUZADA - VERIFICACIÓN DE EVENTOS")
print("="*80)

# 1. Listar archivos de data/ con tamaño
print("\n1. ARCHIVOS DE data/ CON TAMAÑO")
data_path = Path('data')
for item in sorted(data_path.iterdir()):
    if item.is_file():
        size_mb = item.stat().st_size / (1024 * 1024)
        print(f"  {item.name}: {size_mb:.2f} MB")

# Columnas de tracking (un archivo ejemplo)
print("\n  Columnas de tracking (ejemplo):")
tracking_sample = pd.read_csv('data/tracking/tracking_2021090900.csv', nrows=1)
print(f"  {tracking_sample.columns.tolist()}")

# 2. passResult: conteo por valor en semana 1
print("\n2. passResult EN PLAYS DE SEMANA 1")
plays = pd.read_csv('data/plays.csv')
juegos_semana1 = sorted(plays['gameId'].unique())[:16]
plays_semana1 = plays[plays['gameId'].isin(juegos_semana1)]

print(f"  Total jugadas en semana 1: {len(plays_semana1)}")
print(f"\n  Conteo por passResult:")
print(plays_semana1['passResult'].value_counts(dropna=False))

# 3. Eventos por jugada en tracking completo
print("\n3. EVENTOS POR JUGADA EN TRACKING COMPLETO (semana 1)")
print("  Cargando tracking de semana 1...")

tracking_list = []
for juego_id in juegos_semana1:
    tracking_file = f'data/tracking/tracking_{juego_id}.csv'
    tracking_juego = pd.read_csv(tracking_file)
    tracking_list.append(tracking_juego)

tracking_completo = pd.concat(tracking_list, ignore_index=True)
print(f"  Total cuadros: {len(tracking_completo)}")
print(f"  Cuadros con evento no-null: {tracking_completo['event'].notna().sum()}")

# Contar jugadas únicas por evento
eventos_por_jugada = tracking_completo[tracking_completo['event'].notna()].copy()
jugadas_por_evento = eventos_por_jugada.groupby('event')[['gameId', 'playId']].apply(
    lambda x: x.drop_duplicates().shape[0]
).sort_values(ascending=False)

print(f"\n  Top 15 eventos (jugadas únicas que tienen el evento):")
for i, (evento, count) in enumerate(jugadas_por_evento.head(15).items(), 1):
    print(f"    {i:2}. {evento:30} {count:4} jugadas")

# 4. Comparación passResult vs eventos
print("\n4. COMPARACIÓN passResult VS EVENTOS")

# Jugadas con passResult = C
jugadas_completados = plays_semana1[plays_semana1['passResult'] == 'C'][['gameId', 'playId']].copy()
print(f"  Jugadas con passResult = 'C': {len(jugadas_completados)}")

# Jugadas con pass_outcome_caught
jugadas_con_caught = tracking_completo[
    tracking_completo['event'] == 'pass_outcome_caught'
][['gameId', 'playId']].drop_duplicates()
print(f"  Jugadas con pass_outcome_caught: {len(jugadas_con_caught)}")

# Comparar
merge_caught = jugadas_completados.merge(
    jugadas_con_caught,
    on=['gameId', 'playId'],
    how='outer',
    indicator=True
)
print(f"\n  En ambos (C y caught): {(merge_caught['_merge'] == 'both').sum()}")
print(f"  Solo en passResult=C: {(merge_caught['_merge'] == 'left_only').sum()}")
print(f"  Solo en pass_outcome_caught: {(merge_caught['_merge'] == 'right_only').sum()}")

# Jugadas con passResult = I
jugadas_incompletos = plays_semana1[plays_semana1['passResult'] == 'I'][['gameId', 'playId']].copy()
print(f"\n  Jugadas con passResult = 'I': {len(jugadas_incompletos)}")

# Jugadas con pass_outcome_incomplete
jugadas_con_incomplete = tracking_completo[
    tracking_completo['event'] == 'pass_outcome_incomplete'
][['gameId', 'playId']].drop_duplicates()
print(f"  Jugadas con pass_outcome_incomplete: {len(jugadas_con_incomplete)}")

# Comparar
merge_incomplete = jugadas_incompletos.merge(
    jugadas_con_incomplete,
    on=['gameId', 'playId'],
    how='outer',
    indicator=True
)
print(f"\n  En ambos (I y incomplete): {(merge_incomplete['_merge'] == 'both').sum()}")
print(f"  Solo en passResult=I: {(merge_incomplete['_merge'] == 'left_only').sum()}")
print(f"  Solo en pass_outcome_incomplete: {(merge_incomplete['_merge'] == 'right_only').sum()}")

# Jugadas con pass_arrived
jugadas_con_arrived = tracking_completo[
    tracking_completo['event'] == 'pass_arrived'
][['gameId', 'playId']].drop_duplicates()
print(f"\n  Jugadas con pass_arrived: {len(jugadas_con_arrived)}")

# Jugadas con cualquier passResult válido (C, I, S, IN, R)
jugadas_con_passresult = plays_semana1[
    plays_semana1['passResult'].notna()
][['gameId', 'playId']].copy()
print(f"  Jugadas con passResult válido: {len(jugadas_con_passresult)}")

merge_arrived = jugadas_con_passresult.merge(
    jugadas_con_arrived,
    on=['gameId', 'playId'],
    how='outer',
    indicator=True
)
print(f"\n  Pass_arrived que están en plays con passResult: {(merge_arrived['_merge'] == 'both').sum()}")
print(f"  PassResult sin pass_arrived: {(merge_arrived['_merge'] == 'left_only').sum()}")
print(f"  Pass_arrived sin passResult: {(merge_arrived['_merge'] == 'right_only').sum()}")

# 5. Verificar objetivo solo en jugadas C o I
print("\n5. OBJETIVO VS playDescription (SOLO passResult = C o I)")

import random
random.seed(42)

plays_ci = plays_semana1[plays_semana1['passResult'].isin(['C', 'I'])].copy()
print(f"  Total jugadas C o I: {len(plays_ci)}")

# Cargar players para displayName
players = pd.read_csv('data/players.csv')

# Merge tracking con players
tracking_con_nombres = tracking_completo.merge(
    players[['nflId', 'displayName']],
    on='nflId',
    how='left'
)
tracking_con_nombres.loc[tracking_con_nombres['team'] == 'football', 'displayName'] = 'football'

# Cargar PFF para roles
pff = pd.read_csv('data/pffScoutingData.csv')
tracking_con_nombres = tracking_con_nombres.merge(
    pff[['gameId', 'playId', 'nflId', 'pff_role']],
    on=['gameId', 'playId', 'nflId'],
    how='left'
)

muestra = plays_ci.sample(n=min(20, len(plays_ci)))
coincidencias = 0
casos_validos = 0

print(f"\n  Muestra aleatoria de 20 jugadas C o I:")

for idx, jugada in muestra.iterrows():
    game_id = jugada['gameId']
    play_id = jugada['playId']
    
    # Buscar eventos de llegada
    eventos = tracking_con_nombres[
        (tracking_con_nombres['gameId'] == game_id) &
        (tracking_con_nombres['playId'] == play_id) &
        (tracking_con_nombres['event'].isin(['pass_arrived', 'pass_outcome_caught', 'pass_outcome_incomplete']))
    ]
    
    if len(eventos) == 0:
        continue
    
    casos_validos += 1
    evento = eventos.iloc[0]
    frame_id = evento['frameId']
    
    # Receptores en ese frame
    receptores = tracking_con_nombres[
        (tracking_con_nombres['gameId'] == game_id) &
        (tracking_con_nombres['playId'] == play_id) &
        (tracking_con_nombres['frameId'] == frame_id) &
        (tracking_con_nombres['pff_role'] == 'Pass Route')
    ].copy()
    
    # Balón en ese frame
    balon = tracking_con_nombres[
        (tracking_con_nombres['gameId'] == game_id) &
        (tracking_con_nombres['playId'] == play_id) &
        (tracking_con_nombres['frameId'] == frame_id) &
        (tracking_con_nombres['displayName'] == 'football')
    ]
    
    if len(balon) == 0 or len(receptores) == 0:
        continue
    
    # Distancia al balón
    balon_x, balon_y = balon.iloc[0]['x'], balon.iloc[0]['y']
    receptores.loc[:, 'dist_balon'] = (
        (receptores['x'] - balon_x)**2 + 
        (receptores['y'] - balon_y)**2
    )**0.5
    
    objetivo = receptores.loc[receptores['dist_balon'].idxmin()]
    objetivo_nombre = objetivo['displayName']
    
    # Extraer apellido
    apellido_objetivo = objetivo_nombre.split()[-1] if pd.notna(objetivo_nombre) and ' ' in objetivo_nombre else objetivo_nombre
    
    # Extraer de playDescription
    descripcion = jugada['playDescription']
    coincide = False
    
    if pd.notna(descripcion) and ' to ' in descripcion:
        texto_despues_to = descripcion.split(' to ', 1)[1]
        nombre_en_desc = texto_despues_to.split()[0] if texto_despues_to.split() else None
        
        if nombre_en_desc and '.' in nombre_en_desc:
            apellido_desc = nombre_en_desc.split('.')[-1]
            if apellido_objetivo and apellido_desc.lower() == apellido_objetivo.lower():
                coincide = True
                coincidencias += 1

porcentaje = (coincidencias / casos_validos * 100) if casos_validos > 0 else 0
print(f"\n  Casos con evento válido: {casos_validos}")
print(f"  Coincidencias de apellido: {coincidencias}")
print(f"  Porcentaje: {porcentaje:.1f}%")

print("\n" + "="*80)
print("PRUEBA CRUZADA COMPLETADA")
print("="*80)
