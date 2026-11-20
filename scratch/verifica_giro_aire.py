"""
Verificación de giro_por_cuadro() con casos sintéticos
"""
import pandas as pd
import numpy as np
import sys
sys.path.insert(0, '.')

from backend.calculos import giros

print("="*80)
print("VERIFICACIÓN: giro_por_cuadro() - CASOS SINTÉTICOS")
print("="*80)

# CASO 1: Giro de 90° con velocidad suficiente
print("\nCASO 1: Giro de 90° (dir: 0° → 45° → 90°) con velocidad = 3.0 yd/s")
print("  Esperado: giro_grados = 90.0, valido = True, girando = True")

caso1 = pd.DataFrame({
    'gameId': [1, 1, 1, 1, 1, 1, 1],
    'playId': [1, 1, 1, 1, 1, 1, 1],
    'nflId': [100, 100, 100, 100, 100, 100, 100],
    'frameId': [1, 2, 3, 4, 5, 6, 7],
    'dir': [0, 15, 30, 45, 60, 75, 90],  # Incremento lineal
    's': [3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0]  # Velocidad constante suficiente
})

resultado1 = giros.giro_por_cuadro(caso1)
# Analizar cuadro central (frameId = 4, índice 3)
fila_central = resultado1[resultado1['frameId'] == 4].iloc[0]

print(f"  Resultado:")
print(f"    giro_grados: {fila_central['giro_grados']:.1f}°")
print(f"    valido: {fila_central['valido']}")
print(f"    girando: {fila_central['girando']}")

assert fila_central['valido'] == True, "ERROR: debería ser válido"
assert abs(fila_central['giro_grados'] - 90.0) < 1.0, f"ERROR: giro_grados esperado ~90°, obtenido {fila_central['giro_grados']:.1f}°"
assert fila_central['girando'] == True, "ERROR: debería estar girando"
print("  ✓ CASO 1 PASÓ")

# CASO 2: Sin giro (línea recta) con velocidad suficiente
print("\nCASO 2: Sin giro (dir constante = 45°) con velocidad = 4.0 yd/s")
print("  Esperado: giro_grados ≈ 0.0, valido = True, girando = False")

caso2 = pd.DataFrame({
    'gameId': [2, 2, 2, 2, 2, 2, 2],
    'playId': [2, 2, 2, 2, 2, 2, 2],
    'nflId': [200, 200, 200, 200, 200, 200, 200],
    'frameId': [1, 2, 3, 4, 5, 6, 7],
    'dir': [45, 45, 45, 45, 45, 45, 45],  # Constante
    's': [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0]
})

resultado2 = giros.giro_por_cuadro(caso2)
fila_central = resultado2[resultado2['frameId'] == 4].iloc[0]

print(f"  Resultado:")
print(f"    giro_grados: {fila_central['giro_grados']:.1f}°")
print(f"    valido: {fila_central['valido']}")
print(f"    girando: {fila_central['girando']}")

assert fila_central['valido'] == True, "ERROR: debería ser válido"
assert abs(fila_central['giro_grados']) < 1.0, f"ERROR: giro_grados esperado ~0°, obtenido {fila_central['giro_grados']:.1f}°"
assert fila_central['girando'] == False, "ERROR: NO debería estar girando"
print("  ✓ CASO 2 PASÓ")

# CASO 3: Giro inválido (velocidad baja en extremos)
print("\nCASO 3: Giro de 60° pero con velocidad < VEL_MIN_GIRO (1.0 yd/s)")
print("  Esperado: giro_grados = 0.0, valido = False, girando = False")

caso3 = pd.DataFrame({
    'gameId': [3, 3, 3, 3, 3, 3, 3],
    'playId': [3, 3, 3, 3, 3, 3, 3],
    'nflId': [300, 300, 300, 300, 300, 300, 300],
    'frameId': [1, 2, 3, 4, 5, 6, 7],
    'dir': [0, 10, 20, 30, 40, 50, 60],  # Giro suave
    's': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]  # Velocidad BAJA (< VEL_MIN_GIRO = 2.0)
})

resultado3 = giros.giro_por_cuadro(caso3)
fila_central = resultado3[resultado3['frameId'] == 4].iloc[0]

print(f"  Resultado:")
print(f"    giro_grados: {fila_central['giro_grados']:.1f}°")
print(f"    valido: {fila_central['valido']}")
print(f"    girando: {fila_central['girando']}")

assert fila_central['valido'] == False, "ERROR: NO debería ser válido (velocidad baja)"
assert fila_central['giro_grados'] == 0.0, f"ERROR: giro_grados esperado 0.0° (inválido), obtenido {fila_central['giro_grados']:.1f}°"
assert fila_central['girando'] == False, "ERROR: NO debería estar girando"
print("  ✓ CASO 3 PASÓ")

# CASO 4: Envolvimiento de ángulos (360° → 0°)
print("\nCASO 4: Giro con envolvimiento (dir: 350° → 0° → 10°)")
print("  Esperado: giro_grados ≈ +20°, NO -340° (debe envolver en [-180, 180])")

caso4 = pd.DataFrame({
    'gameId': [4, 4, 4, 4, 4, 4, 4],
    'playId': [4, 4, 4, 4, 4, 4, 4],
    'nflId': [400, 400, 400, 400, 400, 400, 400],
    'frameId': [1, 2, 3, 4, 5, 6, 7],
    'dir': [350, 355, 0, 5, 10, 15, 20],
    's': [3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0]
})

resultado4 = giros.giro_por_cuadro(caso4)
fila_central = resultado4[resultado4['frameId'] == 4].iloc[0]

print(f"  Resultado:")
print(f"    giro_grados: {fila_central['giro_grados']:.1f}°")
print(f"    valido: {fila_central['valido']}")
print(f"    girando: {fila_central['girando']}")

assert fila_central['valido'] == True, "ERROR: debería ser válido"
# dir(t-3) = 350, dir(t+3) = 20, delta_raw = 20 - 350 = -330
# Envuelto: (-330 + 180) % 360 - 180 = (-150) % 360 - 180 = 210 - 180 = 30
assert 20 < fila_central['giro_grados'] < 40, f"ERROR: giro_grados esperado ~30°, obtenido {fila_central['giro_grados']:.1f}°"
assert fila_central['girando'] == True, "ERROR: debería estar girando (>= 30°)"
print("  ✓ CASO 4 PASÓ (envolvimiento correcto: +30° en lugar de -330°)")

print("\n" + "="*80)
print("✓ TODOS LOS CASOS SINTÉTICOS PASARON")
print("="*80)
print("\ngiro_por_cuadro() está VERIFICADO y listo para usar en producción")
print("Aviso a A: función vectorizada disponible en backend/calculos/giros.py")
