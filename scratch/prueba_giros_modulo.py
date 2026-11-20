"""
Prueba del módulo giros.py cargando 1 semana directo
Genera resumen por tipo de giro para H2
"""
import pandas as pd
import sys
sys.path.insert(0, '.')

from backend.calculos import giros

# Usar constantes del módulo
VEL_MIN_GIRO = giros.VEL_MIN_GIRO
GIRO_SUAVE = giros.GIRO_SUAVE
GIRO_BRUSCO = giros.GIRO_BRUSCO
ABIERTO_YD = giros.ABIERTO_YD

print("="*80)
print("PRUEBA DEL MÓDULO giros.py")
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

# 1. Construir giros principales por ruta
print("\n1. CONSTRUIR GIROS PRINCIPALES POR RUTA")
print("  (Esto puede tardar ~30-60s por el cálculo de separaciones...)")
giros_df = giros.construir_giros(cuadros, plays_semana1, players, pff)
print(f"  Rutas analizadas: {len(giros_df)}")

# Distribución de tipos
print("\n  Distribución de tipos:")
conteo = giros_df['tipo'].value_counts()
for tipo in conteo.index:
    n = conteo[tipo]
    pct = (n / len(giros_df) * 100)
    print(f"    {tipo}: {n} ({pct:.1f}%)")

# 2. Resumen
print("\n2. RESUMEN")
resumen_data = giros.resumen(giros_df, filtro='decisivo')

print(f"\nFiltro: {resumen_data['filtro']}")
print(f"n total: {resumen_data['n']}")

print("\n" + "="*60)
print("POR TIPO DE GIRO")
print("="*60)

for item in resumen_data['por_tipo']:
    tipo = item['tipo']
    n = item['n']
    sep_ganada = item['sep_ganada_media']
    ic_sep = item['ic_sep']
    pct_libre = item['pct_libre']
    ic_libre = item['ic_libre']
    
    print(f"\n{tipo.upper()} (n={n}):")
    
    if sep_ganada is not None:
        ic_str = f"IC 90%: [{ic_sep[0]:.2f}, {ic_sep[1]:.2f}]" if ic_sep else "IC: N/A"
        print(f"  Separación ganada: {sep_ganada:+.2f} yd ({ic_str})")
    else:
        print(f"  Separación ganada: N/A")
    
    if pct_libre is not None:
        ic_str = f"IC 90%: [{ic_libre[0]:.1f}, {ic_libre[1]:.1f}]" if ic_libre else "IC: N/A"
        print(f"  % libre en pass_forward (>={ABIERTO_YD} yd): {pct_libre:.1f}% ({ic_str})")
    else:
        print(f"  % libre en pass_forward: N/A")

print(f"\n" + "="*60)
print(f"Insight: {resumen_data['insight']}")

print("\n" + "="*80)
print("VERIFICACIÓN: % brusco vs prueba de vida")
print("="*80)

n_brusco = conteo.get('brusco', 0)
total = len(giros_df)
pct_brusco = (n_brusco / total * 100) if total > 0 else 0

print(f"\n% de rutas con giro brusco: {pct_brusco:.1f}%")
print(f"Prueba de vida reportó: 4.3%")
print(f"Prototipo corregido reportó: 6.9%")

if 5 <= pct_brusco <= 10:
    print(f"\nOK: El % brusco ({pct_brusco:.1f}%) es coherente")
else:
    print(f"\nADVERTENCIA: El % brusco ({pct_brusco:.1f}%) está fuera del rango esperado (5-10%)")

print("\n" + "="*80)
print("PRUEBA COMPLETADA")
print("="*80)
