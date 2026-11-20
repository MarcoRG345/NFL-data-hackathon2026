"""
Prueba de vida del receptor - Tarea 1 del spec logica-giro-aire
Lee 1 semana directo de los CSV con normalización inline.
"""
import pandas as pd
import numpy as np
from pathlib import Path
import random

# Constantes de pregunta.md
ABIERTO_YD = 3.0
INICIO_LIBRE_SEG = 1.0
VEL_MIN_GIRO = 2.0
GIRO_SUAVE = 30
GIRO_BRUSCO = 60

def normalizar_tracking(df, plays_df):
    """Normaliza el tracking para que el ataque vaya hacia la derecha"""
    # Merge con plays para obtener possessionTeam
    df = df.merge(
        plays_df[['gameId', 'playId', 'possessionTeam']],
        on=['gameId', 'playId'],
        how='left'
    )
    
    # Determinar dirección del juego
    # playDirection es la dirección a la que va el balón
    # Si possessionTeam != playDirection, necesitamos normalizar
    df['necesita_giro'] = df['playDirection'] == 'left'
    
    # Normalizar coordenadas
    df.loc[df['necesita_giro'], 'x'] = 120 - df.loc[df['necesita_giro'], 'x']
    df.loc[df['necesita_giro'], 'y'] = 53.3 - df.loc[df['necesita_giro'], 'y']
    
    # Normalizar ángulos (dir y o)
    df.loc[df['necesita_giro'], 'dir'] = (df.loc[df['necesita_giro'], 'dir'] + 180) % 360
    df.loc[df['necesita_giro'], 'o'] = (df.loc[df['necesita_giro'], 'o'] + 180) % 360
    
    return df.drop(['playDirection', 'possessionTeam', 'necesita_giro'], axis=1)

def cargar_semana_1():
    """Carga datos de la semana 1 (todos los juegos de la primera semana)"""
    print("Cargando datos de la semana 1...")
    
    # Cargar archivos base
    plays = pd.read_csv('data/plays.csv')
    pff = pd.read_csv('data/pffScoutingData.csv')
    players = pd.read_csv('data/players.csv')
    
    # Obtener IDs únicos de juegos y tomar los primeros 16 (1 semana)
    juegos_semana1 = sorted(plays['gameId'].unique())[:16]
    print(f"  Juegos de semana 1: {len(juegos_semana1)}")
    
    # Filtrar jugadas válidas de la semana 1
    plays_validas = plays[
        (plays['gameId'].isin(juegos_semana1)) &
        (~plays['playDescription'].str.contains('No Play', na=False))
    ].copy()
    
    print(f"  Jugadas válidas: {len(plays_validas)}")
    
    # Cargar tracking de todos los juegos de la semana 1 (SIN FILTROS)
    tracking_list = []
    for juego_id in juegos_semana1:
        tracking_file = f'data/tracking/tracking_{juego_id}.csv'
        print(f"    Cargando juego {juego_id}...", end='')
        tracking_juego = pd.read_csv(tracking_file)  # SIN nrows, SIN chunks
        print(f" {len(tracking_juego)} cuadros")
        tracking_list.append(tracking_juego)
    
    tracking_completo = pd.concat(tracking_list, ignore_index=True)
    print(f"  Total cuadros tracking COMPLETO: {len(tracking_completo)}")
    
    # Normalizar tracking
    tracking = normalizar_tracking(tracking_completo, plays_validas)
    
    # Merge con PFF para obtener roles
    tracking = tracking.merge(
        pff[['gameId', 'playId', 'nflId', 'pff_role']],
        on=['gameId', 'playId', 'nflId'],
        how='left'
    )
    
    # Merge con players para obtener displayName
    tracking = tracking.merge(
        players[['nflId', 'displayName']],
        on='nflId',
        how='left'
    )
    
    # Para el balón (team='football'), asignar displayName manualmente
    tracking.loc[tracking['team'] == 'football', 'displayName'] = 'football'
    
    return tracking, tracking_completo, plays_validas, pff

def calcular_separacion(tracking, plays):
    """Calcula separación por cuadro para cada receptor"""
    # Filtrar solo jugadas de pase
    pase_ids = plays[plays['passResult'].notna()][['gameId', 'playId']]
    tracking_pases = tracking.merge(pase_ids, on=['gameId', 'playId'])
    
    # Receptores y defensores
    receptores = tracking_pases[tracking_pases['pff_role'] == 'Pass Route'].copy()
    defensores = tracking_pases[tracking_pases['pff_role'] == 'Coverage'].copy()
    
    if len(receptores) == 0 or len(defensores) == 0:
        return pd.DataFrame()
    
    # Cruce para calcular distancias
    cruce = receptores.merge(
        defensores[['gameId', 'playId', 'frameId', 'nflId', 'x', 'y']],
        on=['gameId', 'playId', 'frameId'],
        suffixes=('_rec', '_def')
    )
    
    # Distancia euclidiana
    cruce['distancia'] = np.sqrt(
        (cruce['x_rec'] - cruce['x_def'])**2 + 
        (cruce['y_rec'] - cruce['y_def'])**2
    )
    
    # Separación = distancia mínima por receptor y cuadro
    sep = cruce.groupby(['gameId', 'playId', 'nflId_rec', 'frameId', 'time'])['distancia'].min().reset_index()
    sep.columns = ['gameId', 'playId', 'nflId', 'frameId', 't', 'separacion']
    
    return sep

def calcular_giros(tracking):
    """Calcula giros por cuadro según skill logica-giro-aire"""
    # Solo receptores
    receptores = tracking[tracking['pff_role'] == 'Pass Route'].copy()
    
    if len(receptores) == 0:
        return pd.DataFrame()
    
    # Ordenar por jugador y cuadro
    receptores = receptores.sort_values(['gameId', 'playId', 'nflId', 'frameId'])
    
    # dir_antes y s_antes (5 cuadros = 0.5s atrás)
    receptores['dir_antes'] = receptores.groupby(['gameId', 'playId', 'nflId'])['dir'].shift(5)
    receptores['s_antes'] = receptores.groupby(['gameId', 'playId', 'nflId'])['s'].shift(5)
    
    # delta envuelto en [-180, 180]
    receptores['delta_raw'] = receptores['dir'] - receptores['dir_antes']
    receptores['delta'] = ((receptores['delta_raw'] + 180) % 360) - 180
    
    # Válido si ambas velocidades >= VEL_MIN_GIRO
    receptores['valido'] = (receptores['s'] >= VEL_MIN_GIRO) & (receptores['s_antes'] >= VEL_MIN_GIRO)
    
    # giro_grados
    receptores['giro_grados'] = np.where(receptores['valido'], receptores['delta'], 0)
    
    # girando
    receptores['girando'] = receptores['valido'] & (receptores['delta'].abs() >= GIRO_SUAVE)
    
    return receptores[['gameId', 'playId', 'nflId', 'frameId', 'time', 'giro_grados', 'girando', 's', 'dir']]

def analizar_pass_arrived_completo(tracking_completo):
    """Analiza eventos en TODO el tracking sin filtros"""
    print("\n  Analizando tracking COMPLETO (sin filtros)...")
    
    # Contar eventos por jugada única
    eventos_por_jugada = tracking_completo[tracking_completo['event'].notna()].groupby(
        ['gameId', 'playId', 'event']
    ).size().reset_index(name='count')
    
    # Pivot para ver qué jugadas tienen cada evento
    jugadas_con_evento = eventos_por_jugada.groupby('event')['playId'].nunique().sort_values(ascending=False)
    
    print("  Eventos por jugada única:")
    for evento, count in jugadas_con_evento.items():
        print(f"    {evento}: {count} jugadas")
    
    # Calcular jugadas únicas con pass_arrived o pass_outcome
    jugadas_unicas = tracking_completo[['gameId', 'playId']].drop_duplicates()
    total_jugadas = len(jugadas_unicas)
    
    jugadas_con_arrived = tracking_completo[
        tracking_completo['event'] == 'pass_arrived'
    ][['gameId', 'playId']].drop_duplicates()
    
    jugadas_con_outcome = tracking_completo[
        tracking_completo['event'].isin(['pass_outcome_caught', 'pass_outcome_incomplete'])
    ][['gameId', 'playId']].drop_duplicates()
    
    # Union: arrived O outcome
    jugadas_con_llegada = pd.concat([
        jugadas_con_arrived,
        jugadas_con_outcome
    ]).drop_duplicates()
    
    n_arrived = len(jugadas_con_arrived)
    n_outcome = len(jugadas_con_outcome)
    n_llegada_total = len(jugadas_con_llegada)
    
    pct_arrived = (n_arrived / total_jugadas * 100) if total_jugadas > 0 else 0
    pct_outcome = (n_outcome / total_jugadas * 100) if total_jugadas > 0 else 0
    pct_llegada = (n_llegada_total / total_jugadas * 100) if total_jugadas > 0 else 0
    
    return {
        'total_jugadas': total_jugadas,
        'n_arrived': n_arrived,
        'pct_arrived': pct_arrived,
        'n_outcome': n_outcome,
        'pct_outcome': pct_outcome,
        'n_llegada_total': n_llegada_total,
        'pct_llegada': pct_llegada,
        'eventos_por_jugada': jugadas_con_evento
    }

def analizar_colchon_snap(tracking, plays):
    """Analiza separación en el snap (colchón)"""
    # Eventos de ball_snap
    snaps = tracking[tracking['event'] == 'ball_snap']
    
    if len(snaps) == 0:
        return None, 0
    
    # Calcular separación en el snap
    sep_snap = calcular_separacion(tracking[tracking['event'] == 'ball_snap'], plays)
    
    if len(sep_snap) == 0:
        return None, 0
    
    stats = sep_snap['separacion'].describe(percentiles=[0.1, 0.5, 0.9])
    return stats, len(sep_snap)

def analizar_giros_rutas(giros_df):
    """Analiza % de rutas con giro suave y brusco"""
    if len(giros_df) == 0:
        return 0, 0, 0, 0, 0, 0
    
    # Giro principal por ruta (máximo |delta|)
    giro_principal = giros_df.loc[
        giros_df.groupby(['gameId', 'playId', 'nflId'])['giro_grados'].apply(lambda x: x.abs().idxmax())
    ]
    
    total_rutas = len(giro_principal)
    
    # Clasificar por tipo
    sin_giro = (giro_principal['giro_grados'].abs() < GIRO_SUAVE).sum()
    suave = ((giro_principal['giro_grados'].abs() >= GIRO_SUAVE) & 
             (giro_principal['giro_grados'].abs() < GIRO_BRUSCO)).sum()
    brusco = (giro_principal['giro_grados'].abs() >= GIRO_BRUSCO).sum()
    
    return (total_rutas, sin_giro, suave, brusco,
            (suave / total_rutas * 100) if total_rutas > 0 else 0,
            (brusco / total_rutas * 100) if total_rutas > 0 else 0)

def analizar_ruido_baja_velocidad(giros_df):
    """Analiza ruido de dir solo con velocidad >= 2 yd/s antes y después"""
    if len(giros_df) == 0:
        return 0, 0, 0
    
    # SOLO cuadros con velocidad >= VEL_MIN_GIRO antes y después
    # Es decir, los que tienen valido=True en el cálculo de giros
    alta_vel = giros_df[
        (giros_df['s'] >= VEL_MIN_GIRO) &
        (giros_df['s'].notna())
    ].copy()
    
    if len(alta_vel) == 0:
        return 0, 0, 0
    
    # Calcular dir_antes para estos cuadros
    alta_vel = alta_vel.sort_values(['gameId', 'playId', 'nflId', 'frameId'])
    alta_vel['dir_antes'] = alta_vel.groupby(['gameId', 'playId', 'nflId'])['dir'].shift(5)
    alta_vel['s_antes'] = alta_vel.groupby(['gameId', 'playId', 'nflId'])['s'].shift(5)
    
    # Filtrar solo los que TAMBIÉN tenían alta velocidad antes
    alta_vel_ambos = alta_vel[alta_vel['s_antes'] >= VEL_MIN_GIRO].copy()
    
    if len(alta_vel_ambos) == 0:
        return 0, 0, 0
    
    # Calcular delta
    alta_vel_ambos['delta_raw'] = alta_vel_ambos['dir'] - alta_vel_ambos['dir_antes']
    alta_vel_ambos['delta'] = ((alta_vel_ambos['delta_raw'] + 180) % 360) - 180
    
    # Contar cambios grandes
    cambios_grandes = (alta_vel_ambos['delta'].abs() > 45).sum()
    total_cuadros = len(alta_vel_ambos)
    
    porcentaje = (cambios_grandes / total_cuadros * 100) if total_cuadros > 0 else 0
    
    return total_cuadros, cambios_grandes, porcentaje

def verificar_objetivo_vs_descripcion(plays, tracking, n=20):
    """Verifica coincidencia del objetivo con playDescription usando apellidos"""
    # Filtrar jugadas con pase completo o incompleto
    jugadas_pase = plays[plays['passResult'].isin(['C', 'I'])].copy()
    
    if len(jugadas_pase) < n:
        n = len(jugadas_pase)
    
    # Seleccionar n al azar
    random.seed(42)
    muestra = jugadas_pase.sample(n=n)
    
    coincidencias = 0
    ejemplos = []
    
    print("\n  Verificando objetivo vs playDescription (muestra aleatoria):")
    
    for idx, jugada in muestra.iterrows():
        # Buscar pass_arrived o pass_outcome
        eventos = tracking[
            (tracking['gameId'] == jugada['gameId']) &
            (tracking['playId'] == jugada['playId']) &
            (tracking['event'].isin(['pass_arrived', 'pass_outcome_caught', 'pass_outcome_incomplete']))
        ]
        
        if len(eventos) == 0:
            continue
        
        # Tomar el primer evento
        evento = eventos.iloc[0]
        frame_id = evento['frameId']
        
        # Receptores en ese frame
        receptores_frame = tracking[
            (tracking['gameId'] == jugada['gameId']) &
            (tracking['playId'] == jugada['playId']) &
            (tracking['frameId'] == frame_id) &
            (tracking['pff_role'] == 'Pass Route')
        ].copy()
        
        # Balón en ese frame
        balon = tracking[
            (tracking['gameId'] == jugada['gameId']) &
            (tracking['playId'] == jugada['playId']) &
            (tracking['frameId'] == frame_id) &
            (tracking['displayName'] == 'football')
        ]
        
        if len(balon) == 0 or len(receptores_frame) == 0:
            continue
        
        # Distancias al balón
        balon_x, balon_y = balon.iloc[0]['x'], balon.iloc[0]['y']
        receptores_frame.loc[:, 'dist_balon'] = np.sqrt(
            (receptores_frame['x'] - balon_x)**2 +
            (receptores_frame['y'] - balon_y)**2
        )
        
        # Objetivo = más cercano
        objetivo = receptores_frame.loc[receptores_frame['dist_balon'].idxmin()]
        objetivo_nombre = objetivo['displayName']
        
        # Extraer apellido del objetivo (última palabra)
        if pd.notna(objetivo_nombre):
            apellido_objetivo = objetivo_nombre.split()[-1] if ' ' in objetivo_nombre else objetivo_nombre
        else:
            apellido_objetivo = None
        
        # Extraer nombre después de " to " en playDescription
        descripcion = jugada['playDescription']
        nombre_en_desc = None
        coincide = False
        
        if pd.notna(descripcion) and ' to ' in descripcion:
            # Texto después de " to "
            texto_despues_to = descripcion.split(' to ', 1)[1]
            # Tomar primera palabra (puede ser "S.Diggs" o similar)
            palabras = texto_despues_to.split()
            if len(palabras) > 0:
                nombre_en_desc = palabras[0]
                # Extraer apellido (después del punto si existe)
                if '.' in nombre_en_desc:
                    apellido_desc = nombre_en_desc.split('.')[-1]
                else:
                    apellido_desc = nombre_en_desc
                
                # Comparar apellidos
                if apellido_objetivo and apellido_desc.lower() == apellido_objetivo.lower():
                    coincide = True
                    coincidencias += 1
        
        # Guardar primeros 5 ejemplos
        if len(ejemplos) < 5:
            ejemplos.append({
                'objetivo_calculado': objetivo_nombre,
                'apellido_objetivo': apellido_objetivo,
                'nombre_en_desc': nombre_en_desc,
                'descripcion': descripcion,
                'coincide': coincide
            })
    
    porcentaje = (coincidencias / n * 100) if n > 0 else 0
    return n, coincidencias, porcentaje, ejemplos

def main():
    print("="*60)
    print("PRUEBA DE VIDA DEL RECEPTOR - TAREA 1")
    print("="*60)
    
    # Cargar datos
    tracking, tracking_completo, plays, pff = cargar_semana_1()
    
    # 1. % de pases con pass_arrived EN TRACKING COMPLETO
    print("\n1. ANÁLISIS DE pass_arrived (TRACKING COMPLETO)")
    resultado_arrived = analizar_pass_arrived_completo(tracking_completo)
    print(f"  Total jugadas en tracking: {resultado_arrived['total_jugadas']}")
    print(f"  Con pass_arrived: {resultado_arrived['n_arrived']} ({resultado_arrived['pct_arrived']:.1f}%)")
    print(f"  Con pass_outcome_*: {resultado_arrived['n_outcome']} ({resultado_arrived['pct_outcome']:.1f}%)")
    print(f"  Con llegada (arrived O outcome): {resultado_arrived['n_llegada_total']} ({resultado_arrived['pct_llegada']:.1f}%)")
    
    # 2. Separación en el snap (colchón)
    print("\n2. SEPARACIÓN EN EL SNAP (colchón)")
    stats_sep, n_sep = analizar_colchon_snap(tracking, plays)
    if stats_sep is not None:
        print(f"  n = {n_sep}")
        print(f"  Mediana: {stats_sep['50%']:.2f} yd")
        print(f"  P10: {stats_sep['10%']:.2f} yd")
        print(f"  P90: {stats_sep['90%']:.2f} yd")
    else:
        print("  No hay datos de snap suficientes")
    
    # 3. Calcular giros
    print("\n3. GIROS POR RUTA")
    giros = calcular_giros(tracking)
    total_rutas, sin_giro, suave, brusco, pct_suave, pct_brusco = analizar_giros_rutas(giros)
    print(f"  Rutas analizadas: {total_rutas}")
    print(f"  Sin giro (< {GIRO_SUAVE}°): {sin_giro} ({(sin_giro/total_rutas*100):.1f}%)")
    print(f"  Giro suave ({GIRO_SUAVE}-{GIRO_BRUSCO}°): {suave} ({pct_suave:.1f}%)")
    print(f"  Giro brusco (≥ {GIRO_BRUSCO}°): {brusco} ({pct_brusco:.1f}%)")
    
    # 4. Ruido de dir SOLO con alta velocidad antes y después
    print("\n4. RUIDO DE dir CON VELOCIDAD ALTA (≥ 2 yd/s antes y después)")
    cuadros_alta_vel, cambios_grandes, pct_ruido = analizar_ruido_baja_velocidad(giros)
    print(f"  Cuadros con s ≥ {VEL_MIN_GIRO} yd/s antes y después: {cuadros_alta_vel}")
    print(f"  Cambios de dir > 45°: {cambios_grandes}")
    print(f"  Porcentaje: {pct_ruido:.1f}%")
    
    # 5. Verificar objetivo vs playDescription CON APELLIDOS
    print("\n5. COINCIDENCIA OBJETIVO vs playDescription (por apellido)")
    n_muestra, coincide, pct_coincide, ejemplos = verificar_objetivo_vs_descripcion(plays, tracking, n=20)
    print(f"  Muestra: {n_muestra} jugadas")
    print(f"  Coincidencias: {coincide}")
    print(f"  Porcentaje: {pct_coincide:.1f}%")
    print("\n  EJEMPLOS (primeros 5):")
    for i, ej in enumerate(ejemplos, 1):
        print(f"    {i}. Objetivo: {ej['objetivo_calculado']} (apellido: {ej['apellido_objetivo']})")
        print(f"       En descripción: {ej['nombre_en_desc']}")
        print(f"       Coincide: {'✓' if ej['coincide'] else '✗'}")
        print(f"       Texto: {ej['descripcion'][:80]}...")
    
    print("\n" + "="*60)
    print("ANÁLISIS COMPLETADO")
    print("="*60)
    
    # Retornar resultados para escribir en MD
    return {
        'pass_arrived': resultado_arrived,
        'colchon': (n_sep, stats_sep),
        'giros': (total_rutas, sin_giro, suave, brusco, pct_suave, pct_brusco),
        'ruido': (cuadros_alta_vel, cambios_grandes, pct_ruido),
        'objetivo': (n_muestra, coincide, pct_coincide, ejemplos)
    }

if __name__ == '__main__':
    resultados = main()
