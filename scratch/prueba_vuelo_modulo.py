"""
Prueba del módulo vuelo.py cargando 1 semana directo
"""
import pandas as pd
import sys
sys.path.insert(0, '.')

from backend.calculos import vuelo

# Usar constantes del módulo
ABIERTO_YD = vuelo.ABIERTO_YD

print("="*80)
print("PRUEBA DEL MÓDULO vuelo.py")
print("="*80)

# Cargar datos semana 1
print("\nCargando datos semana 1...")
plays = pd.read_csv('data/plays.csv')
players = pd.read_csv('data/players.csv')
pff = pd.read_csv('data/pffScoutingData.csv')

juegos_semana1 = sorted(plays['gameId'].unique())[:16]
plays_semana1 = plays[plays['gameId'].isin(juegos_semana1)]

tracking_list = []
for juego_id in juegos_semana1:
    tracking_juego = pd.read_csv(f'data/tracking/tracking_{juego_id}.csv')
    tracking_list.append(tracking_juego)

cuadros = pd.concat(tracking_list, ignore_index=True)

print(f"  Jugadas: {len(plays_semana1)}")
print(f"  Cuadros: {len(cuadros)}")

# Normalización básica (ya hecha en el prototipo)
# Por simplicidad, asumimos que el tracking ya está normalizado
# En producción, se haría en backend/base/normalizacion.py

# 1. Construir ventaja
print("\n1. CONSTRUIR VENTAJA AL LANZAR")
ventaja_df = vuelo.construir(cuadros, plays_semana1, players, pff)
print(f"  Pases analizados: {len(ventaja_df)}")
print(f"  Aproximados: {ventaja_df['aproximado'].sum()}")

# 2. sigue_libre_por_jugada
print("\n2. sigue_libre_por_jugada()")
sigue_libre_df = vuelo.sigue_libre_por_jugada(cuadros, plays_semana1, players, pff)
print(f"  Jugadas: {len(sigue_libre_df)}")
print(f"  Con ventaja (>={ABIERTO_YD} yd): {sigue_libre_df['sigue_libre'].sum()}")

# 3. Resumen
print("\n3. RESUMEN")
resumen_data = vuelo.resumen(ventaja_df, filtro='decisivo')

print(f"\nFiltro: {resumen_data['filtro']}")
print(f"n: {resumen_data['n']}")
print(f"n_aproximado: {resumen_data['n_aproximado']}")

print("\nPor separación:")
for item in resumen_data['por_separacion']:
    ic_str = f"IC: {item['ic']}" if item['ic'] else "IC: N/A"
    print(f"  {item['franja']}: {item['pct_completo']}% (n={item['n']}, {ic_str})")

print("\nPor tendencia:")
for item in resumen_data['por_tendencia']:
    ic_str = f"IC: {item['ic']}" if item['ic'] else "IC: N/A"
    print(f"  {item['tendencia']}: {item['pct_completo']}% (n={item['n']}, {ic_str})")

print(f"\nInsight: {resumen_data['insight']}")

print("\n" + "="*80)
print("PRUEBA COMPLETADA")
print("="*80)
