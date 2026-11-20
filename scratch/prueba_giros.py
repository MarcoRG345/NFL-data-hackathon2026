"""
Prototipo: Giro principal por ruta (Tarea 3 de logica-giro-aire) - CORREGIDO
Semana 1, sin escribir en backend/
Ventana correcta: dir(t + 0.25s) - dir(t - 0.25s)
"""
import pandas as pd
import numpy as np

print("="*80)
print("PROTOTIPO: GIRO PRINCIPAL POR RUTA (CORREGIDO)")
print("="*80)

# Constantes
VEL_MIN_GIRO = 2.0
GIRO_SUAVE = 30
GIRO_BRUSCO = 60
ABIERTO_YD = 3.0

# Cargar datos semana 1
print("\nCargando datos semana 1...")
plays = pd.read_csv('data/plays.csv')
pff = pd.read_csv('data/pffScoutingData.csv')

juegos_semana1 = sorted(plays['gameId'].unique())[:16]
plays_semana1 = plays[plays['gameId'].isin(juegos_semana1)]

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

# PASO 1: CALCULAR GIRO POR CUADRO CON VENTANA CORRECTA
print("\n1. CALCULANDO GIRO POR CUADRO (ventana +/- 0.25s)...")

# Solo receptores
receptores = tracking[tracking['pff_role'] == 'Pass Route'].copy()
print(f"Cuadros de receptores: {len(receptores)}")

# Ordenar por jugador y cuadro
receptores = receptores.sort_values(['gameId', 'playId', 'nflId', 'frameId'])

# dir y velocidad en t - 0.25s (2.5 cuadros antes, redondeamos a 3)
receptores['dir_antes'] = receptores.groupby(['gameId', 'playId', 'nflId'])['dir'].shift(3)
receptores['s_antes'] = receptores.groupby(['gameId', 'playId', 'nflId'])['s'].shift(3)

# dir y velocidad en t + 0.25s (2.5 cuadros después, redondeamos a 3)
receptores['dir_despues'] = receptores.groupby(['gameId', 'playId', 'nflId'])['dir'].shift(-3)
receptores['s_despues'] = receptores.groupby(['gameId', 'playId', 'nflId'])['s'].shift(-3)

# delta = dir(t + 0.25) - dir(t - 0.25), envuelto en [-180, 180]
receptores['delta_raw'] = receptores['dir_despues'] - receptores['dir_antes']
receptores['delta'] = ((receptores['delta_raw'] + 180) % 360) - 180

# Válido si ambas velocidades >= VEL_MIN_GIRO
receptores['valido'] = (
    (receptores['s_antes'] >= VEL_MIN_GIRO) & 
    (receptores['s_despues'] >= VEL_MIN_GIRO) &
    receptores['delta'].notna()
)

# giro_grados
receptores['giro_grados'] = np.where(receptores['valido'], receptores['delta'], 0)

# girando
receptores['girando'] = receptores['valido'] & (receptores['delta'].abs() >= GIRO_SUAVE)

print(f"Cuadros con giro válido: {receptores['valido'].sum()}")

# PASO 2: GIRO PRINCIPAL POR RUTA
print("\n2. IDENTIFICANDO GIRO PRINCIPAL POR RUTA...")

# Obtener frames de ball_snap y pass_forward
ball_snap_frames = tracking[tracking['event'] == 'ball_snap'][['gameId', 'playId', 'frameId']].drop_duplicates()
ball_snap_frames.columns = ['gameId', 'playId', 'snap_frame']

pass_forward_frames = tracking[tracking['event'] == 'pass_forward'][['gameId', 'playId', 'frameId']].drop_duplicates()
pass_forward_frames.columns = ['gameId', 'playId', 'forward_frame']

print(f"  Jugadas con ball_snap: {len(ball_snap_frames)}")
print(f"  Jugadas con pass_forward: {len(pass_forward_frames)}")

# Merge receptores SOLO con gameId/playId de eventos (más eficiente)
# Primero reducir receptores a solo lo necesario
receptores_keys = receptores[['gameId', 'playId', 'nflId', 'frameId', 'delta', 'valido']].copy()

# Merge con snap
receptores_con_snap = receptores_keys.merge(
    ball_snap_frames,
    on=['gameId', 'playId'],
    how='inner'
)

print(f"  Receptores con snap: {len(receptores_con_snap)}")

# Merge con forward
receptores_con_eventos = receptores_con_snap.merge(
    pass_forward_frames,
    on=['gameId', 'playId'],
    how='inner'
)

print(f"  Receptores con ambos eventos: {len(receptores_con_eventos)}")

# Filtrar cuadros: entre 0.5s después del snap (snap_frame + 5) y pass_forward
receptores_ventana = receptores_con_eventos[
    (receptores_con_eventos['frameId'] >= receptores_con_eventos['snap_frame'] + 5) &
    (receptores_con_eventos['frameId'] <= receptores_con_eventos['forward_frame']) &
    (receptores_con_eventos['valido'])  # SOLO cuadros válidos
].copy()

print(f"  Cuadros válidos en ventana (0.5s post-snap a forward): {len(receptores_ventana)}")

# Contar rutas (combinaciones únicas de gameId, playId, nflId)
rutas_en_ventana = receptores_con_eventos[['gameId', 'playId', 'nflId']].drop_duplicates()
print(f"  Rutas totales: {len(rutas_en_ventana)}")

# Giro principal = cuadro válido con mayor |delta| por ruta
giro_principal_indices = []
for (game_id, play_id, nfl_id), group in receptores_ventana.groupby(['gameId', 'playId', 'nflId']):
    if len(group) > 0:
        idx_max = group['delta'].abs().idxmax()
        giro_principal_indices.append(idx_max)

# Recuperar info completa desde receptores_ventana
giros_principales = receptores_ventana.loc[giro_principal_indices].copy()

print(f"  Rutas CON giro válido: {len(giros_principales)}")

# Rutas SIN giro válido = todas - las que tienen giro
rutas_con_giro = giros_principales[['gameId', 'playId', 'nflId']].drop_duplicates()
rutas_sin_giro = rutas_en_ventana.merge(
    rutas_con_giro,
    on=['gameId', 'playId', 'nflId'],
    how='left',
    indicator=True
)
rutas_sin_giro = rutas_sin_giro[rutas_sin_giro['_merge'] == 'left_only'][['gameId', 'playId', 'nflId']]

print(f"  Rutas SIN giro válido: {len(rutas_sin_giro)}")

# PASO 3: CLASIFICAR TIPO DE GIRO
# Para rutas CON giro válido
giros_principales['tipo'] = pd.cut(
    giros_principales['delta'].abs(),
    bins=[0, GIRO_SUAVE, GIRO_BRUSCO, 180],
    labels=['sin_giro', 'suave', 'brusco'],
    include_lowest=True
)

print("\n3. CLASIFICANDO TIPOS DE GIRO...")
print("\nDistribución de tipos (rutas CON giro válido):")
print(giros_principales['tipo'].value_counts())

# Añadir rutas sin giro al análisis
rutas_sin_giro['tipo'] = 'sin_giro'
rutas_sin_giro['frameId'] = None  # No hay frame específico

# PASO 4: SEPARACIÓN GANADA Y LIBRE AL FINAL
print("\n4. CALCULANDO SEPARACIÓN GANADA...")

# Calcular separación por cuadro
def calcular_separacion_cuadro(tracking_subset):
    """Calcula separación para un conjunto de cuadros"""
    receptores_data = tracking_subset[tracking_subset['pff_role'] == 'Pass Route']
    defensores_data = tracking_subset[tracking_subset['pff_role'] == 'Coverage']
    
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

print("  Calculando separación por cuadro (puede tardar)...")
separaciones = calcular_separacion_cuadro(tracking)
print(f"  Separaciones calculadas: {len(separaciones)}")

# Para rutas CON giro: separación en t (frameId del giro) y en t + 0.5s
resultados_con_giro = []

for idx, giro in giros_principales.iterrows():
    game_id = giro['gameId']
    play_id = giro['playId']
    nfl_id = giro['nflId']
    frame_giro = giro['frameId']
    tipo = giro['tipo']
    
    # Buscar forward_frame para esta jugada
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
    
    # Separación en t + 0.5s (5 frames después)
    sep_t_plus = separaciones[
        (separaciones['gameId'] == game_id) &
        (separaciones['playId'] == play_id) &
        (separaciones['nflId'] == nfl_id) &
        (separaciones['frameId'] == frame_giro + 5)
    ]
    
    # Separación en pass_forward (libre al final)
    sep_forward = separaciones[
        (separaciones['gameId'] == game_id) &
        (separaciones['playId'] == play_id) &
        (separaciones['nflId'] == nfl_id) &
        (separaciones['frameId'] == forward_frame)
    ]
    
    if len(sep_t) == 0 or len(sep_t_plus) == 0:
        continue
    
    sep_ganada = sep_t_plus.iloc[0]['separacion'] - sep_t.iloc[0]['separacion']
    
    # Libre = ≥ 3 yd en pass_forward
    if len(sep_forward) > 0:
        libre_final = sep_forward.iloc[0]['separacion'] >= ABIERTO_YD
    else:
        libre_final = None
    
    resultados_con_giro.append({
        'gameId': game_id,
        'playId': play_id,
        'nflId': nfl_id,
        'tipo': tipo,
        'sep_ganada': sep_ganada,
        'libre_final': libre_final
    })

# Para rutas SIN giro: solo verificar si están libres en pass_forward
resultados_sin_giro = []

for idx, ruta in rutas_sin_giro.iterrows():
    game_id = ruta['gameId']
    play_id = ruta['playId']
    nfl_id = ruta['nflId']
    
    # Obtener forward_frame
    forward_info = pass_forward_frames[
        (pass_forward_frames['gameId'] == game_id) &
        (pass_forward_frames['playId'] == play_id)
    ]
    
    if len(forward_info) == 0:
        continue
    
    forward_frame = forward_info.iloc[0]['forward_frame']
    
    # Separación en pass_forward
    sep_forward = separaciones[
        (separaciones['gameId'] == game_id) &
        (separaciones['playId'] == play_id) &
        (separaciones['nflId'] == nfl_id) &
        (separaciones['frameId'] == forward_frame)
    ]
    
    if len(sep_forward) > 0:
        libre_final = sep_forward.iloc[0]['separacion'] >= ABIERTO_YD
    else:
        libre_final = None
    
    resultados_sin_giro.append({
        'gameId': game_id,
        'playId': play_id,
        'nflId': nfl_id,
        'tipo': 'sin_giro',
        'sep_ganada': None,  # No hay giro, no se calcula
        'libre_final': libre_final
    })

# Combinar resultados
df_con_giro = pd.DataFrame(resultados_con_giro)
df_sin_giro_calc = pd.DataFrame(resultados_sin_giro)

df_giros_analisis = pd.concat([df_con_giro, df_sin_giro_calc], ignore_index=True)

print(f"\nRutas analizadas: {len(df_giros_analisis)}")
print(f"  Con giro y sep_ganada: {len(df_con_giro)}")
print(f"  Sin giro (solo libre_final): {len(df_sin_giro_calc)}")

# PASO 5: RESULTADOS POR TIPO
print("\n" + "="*80)
print("RESULTADOS POR TIPO DE GIRO")
print("="*80)

# Primero mostrar distribución total
print(f"\nDistribución de tipos (todas las rutas, n={len(df_giros_analisis)}):")
conteo_tipos = df_giros_analisis['tipo'].value_counts()
for tipo in conteo_tipos.index:
    n = conteo_tipos[tipo]
    pct = (n / len(df_giros_analisis) * 100)
    print(f"  {tipo}: {n} ({pct:.1f}%)")

print("\n" + "-"*80)

for tipo in ['sin_giro', 'suave', 'brusco']:
    subset = df_giros_analisis[df_giros_analisis['tipo'] == tipo]
    
    if len(subset) == 0:
        continue
    
    # Separación ganada (solo para rutas con giro válido)
    subset_con_sep = subset[subset['sep_ganada'].notna()]
    
    if len(subset_con_sep) > 0:
        sep_ganada_media = subset_con_sep['sep_ganada'].mean()
        sep_ganada_mediana = subset_con_sep['sep_ganada'].median()
    else:
        sep_ganada_media = None
        sep_ganada_mediana = None
    
    # % libre al final (en pass_forward)
    subset_con_libre = subset[subset['libre_final'].notna()]
    if len(subset_con_libre) > 0:
        pct_libre = (subset_con_libre['libre_final'].sum() / len(subset_con_libre) * 100)
    else:
        pct_libre = None
    
    print(f"\n{tipo.upper()} (n={len(subset)}):")
    if sep_ganada_media is not None:
        print(f"  Separación ganada (media): {sep_ganada_media:+.2f} yd (n={len(subset_con_sep)})")
        print(f"  Separación ganada (mediana): {sep_ganada_mediana:+.2f} yd")
    else:
        print(f"  Separación ganada: N/A (sin giro válido)")
    
    if pct_libre is not None:
        print(f"  % libres en pass_forward (>={ABIERTO_YD} yd): {pct_libre:.1f}% (n={len(subset_con_libre)})")
    else:
        print(f"  % libres en pass_forward: N/A")

print("\n" + "="*80)
print("VERIFICACIÓN: % brusco vs prueba de vida")
print("="*80)

n_brusco = len(df_giros_analisis[df_giros_analisis['tipo'] == 'brusco'])
total_rutas = len(df_giros_analisis)
pct_brusco = (n_brusco / total_rutas * 100) if total_rutas > 0 else 0

print(f"\n% de rutas con giro brusco: {pct_brusco:.1f}%")
print(f"Prueba de vida reportó: 4.3%")

if pct_brusco > 30:
    print(f"\nADVERTENCIA: {pct_brusco:.1f}% es alto (esperado ~4-5%)")
    print("\nPosibles causas:")
    print("  1. Ventana incorrecta: Se esta usando +/- 0.25s correctamente?")
    print("  2. Validacion de velocidad: Se verifica en t-0.25 Y t+0.25?")
    print("  3. Filtro de tiempo: Solo entre 0.5s post-snap y pass_forward?")
    print("  4. Delta mal calculado: Envolvimiento [-180, 180] correcto?")
else:
    print(f"\nOK: El % brusco ({pct_brusco:.1f}%) es coherente con la prueba de vida (4.3%)")

print("\n" + "="*80)
print("PROTOTIPO COMPLETADO")
print("="*80)
