"""
Prueba del módulo vuelo.py cargando 1 semana directo
Genera tabla principal (solo por nombre) y tabla de robustez (con respaldo)
"""
import pandas as pd
import sys
sys.path.insert(0, '.')

from backend.calculos import vuelo

# Usar constantes del módulo
ABIERTO_YD = vuelo.ABIERTO_YD

print("="*80)
print("PRUEBA DEL MÓDULO vuelo.py - CORREGIDO")
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

# Total de pases
pases_totales = len(plays_semana1[plays_semana1['passResult'].isin(['C', 'I', 'IN'])])
print(f"  Pases totales (C/I/IN): {pases_totales}")

# 1. Construir ventaja SIN RESPALDO (solo por nombre)
print("\n1. CONSTRUIR VENTAJA AL LANZAR (solo por nombre)")
ventaja_principal = vuelo.construir(cuadros, plays_semana1, players, pff, usar_respaldo=False)
print(f"  Identificados por nombre: {len(ventaja_principal)}")

# 2. Construir ventaja CON RESPALDO (para robustez)
print("\n2. CONSTRUIR CON RESPALDO (para tabla de robustez)")
ventaja_robustez = vuelo.construir(cuadros, plays_semana1, players, pff, usar_respaldo=True)
print(f"  Total con respaldo: {len(ventaja_robustez)}")
print(f"  Aproximados: {ventaja_robustez['aproximado'].sum()}")

# Calcular sin objetivo
n_sin_objetivo = pases_totales - len(ventaja_robustez)
print(f"  Sin objetivo (spike, throwaway): {n_sin_objetivo}")

# 3. Resumen con ambas tablas
print("\n3. RESUMEN")
resumen_data = vuelo.resumen(ventaja_principal, ventaja_robustez, filtro='decisivo')

print(f"\nFiltro: {resumen_data['filtro']}")
print(f"n por nombre: {resumen_data['n_por_nombre']}")
print(f"n sin objetivo: {n_sin_objetivo}")
print(f"n aproximado: {resumen_data['n_aproximado']}")

print("\n" + "="*60)
print("TABLA PRINCIPAL (solo identificados por nombre)")
print("="*60)

print("\nPor separación:")
for item in resumen_data['tabla_principal']['por_separacion']:
    ic_str = f"IC 90%: [{item['ic'][0]}, {item['ic'][1]}]" if item['ic'] else "IC: N/A"
    print(f"  {item['franja']:12s}: {item['pct_completo']:5.1f}% (n={item['n']:3d}, {ic_str})")

print("\nPor tendencia:")
for item in resumen_data['tabla_principal']['por_tendencia']:
    ic_str = f"IC 90%: [{item['ic'][0]}, {item['ic'][1]}]" if item['ic'] else "IC: N/A"
    print(f"  {item['tendencia']:12s}: {item['pct_completo']:5.1f}% (n={item['n']:3d}, {ic_str})")

if resumen_data['tabla_robustez']:
    print("\n" + "="*60)
    print("TABLA DE ROBUSTEZ (con respaldo)")
    print("="*60)
    
    print("\nPor separación:")
    for item in resumen_data['tabla_robustez']['por_separacion']:
        ic_str = f"IC 90%: [{item['ic'][0]}, {item['ic'][1]}]" if item['ic'] else "IC: N/A"
        print(f"  {item['franja']:12s}: {item['pct_completo']:5.1f}% (n={item['n']:3d}, {ic_str})")
    
    print("\nPor tendencia:")
    for item in resumen_data['tabla_robustez']['por_tendencia']:
        ic_str = f"IC 90%: [{item['ic'][0]}, {item['ic'][1]}]" if item['ic'] else "IC: N/A"
        print(f"  {item['tendencia']:12s}: {item['pct_completo']:5.1f}% (n={item['n']:3d}, {ic_str})")

print(f"\n" + "="*60)
print(f"Insight (de tabla principal): {resumen_data['insight']}")

print("\n" + "="*80)
print("PRUEBA COMPLETADA")
print("="*80)
