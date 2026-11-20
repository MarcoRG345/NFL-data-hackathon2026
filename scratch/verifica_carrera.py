"""
Casos sintéticos para verificar la lógica de relojes.
5 casos que cubren los resultados posibles.
"""
import pandas as pd
import numpy as np

def crear_caso_1_gana_receptor():
    """Caso 1: Receptor se libera en t=1.2s, presión llega en t=2.5s → gana_receptor"""
    # sep_cuadros: receptor libre en t=1.2
    sep = pd.DataFrame({
        "gameId": [1, 1, 1, 1],
        "playId": [1, 1, 1, 1],
        "nflId": [100, 100, 100, 100],
        "frameId": [10, 12, 15, 20],
        "t": [1.0, 1.2, 1.5, 2.0],
        "libre": [False, True, True, True],
        "separacion": [2.5, 3.2, 3.5, 4.0],
    })
    
    # presion: llega en t=2.5
    presion = pd.DataFrame({
        "gameId": [1],
        "playId": [1],
        "t_presion": [2.5],
        "por_sack": [False],
    })
    
    # jugadas
    jugadas = pd.DataFrame({
        "gameId": [1],
        "playId": [1],
        "decisivo": [True],
    })
    
    return sep, presion, jugadas, "gana_receptor", 1.3


def crear_caso_2_gana_defensa():
    """Caso 2: Presión llega en t=1.8s, receptor se libera en t=2.3s → gana_defensa"""
    sep = pd.DataFrame({
        "gameId": [2, 2, 2, 2],
        "playId": [2, 2, 2, 2],
        "nflId": [200, 200, 200, 200],
        "frameId": [10, 15, 20, 23],
        "t": [1.0, 1.5, 2.0, 2.3],
        "libre": [False, False, False, True],
        "separacion": [2.0, 2.5, 2.8, 3.1],
    })
    
    presion = pd.DataFrame({
        "gameId": [2],
        "playId": [2],
        "t_presion": [1.8],
        "por_sack": [False],
    })
    
    jugadas = pd.DataFrame({
        "gameId": [2],
        "playId": [2],
        "decisivo": [True],
    })
    
    return sep, presion, jugadas, "gana_defensa", -0.5


def crear_caso_3_sin_presion():
    """Caso 3: Receptor se libera en t=1.5s, nunca llega presión → sin_presion"""
    sep = pd.DataFrame({
        "gameId": [3, 3, 3],
        "playId": [3, 3, 3],
        "nflId": [300, 300, 300],
        "frameId": [10, 15, 20],
        "t": [1.0, 1.5, 2.0],
        "libre": [False, True, True],
        "separacion": [2.8, 3.2, 3.5],
    })
    
    presion = pd.DataFrame({
        "gameId": [3],
        "playId": [3],
        "t_presion": [np.nan],
        "por_sack": [False],
    })
    
    jugadas = pd.DataFrame({
        "gameId": [3],
        "playId": [3],
        "decisivo": [True],
    })
    
    return sep, presion, jugadas, "sin_presion", np.nan


def crear_caso_4_nunca_libre():
    """Caso 4: Presión llega en t=2.0s, receptor nunca se libera → gana_defensa"""
    sep = pd.DataFrame({
        "gameId": [4, 4, 4],
        "playId": [4, 4, 4],
        "nflId": [400, 400, 400],
        "frameId": [10, 15, 20],
        "t": [1.0, 1.5, 2.0],
        "libre": [False, False, False],
        "separacion": [2.0, 2.2, 2.5],
    })
    
    presion = pd.DataFrame({
        "gameId": [4],
        "playId": [4],
        "t_presion": [2.0],
        "por_sack": [True],
    })
    
    jugadas = pd.DataFrame({
        "gameId": [4],
        "playId": [4],
        "decisivo": [True],
    })
    
    return sep, presion, jugadas, "gana_defensa", np.nan


def crear_caso_5_sack_con_libre():
    """Caso 5: Receptor libre en t=1.1s, sack en t=2.8s → gana_receptor + sack_con_libre"""
    sep = pd.DataFrame({
        "gameId": [5, 5, 5],
        "playId": [5, 5, 5],
        "nflId": [500, 500, 500],
        "frameId": [10, 11, 15],
        "t": [1.0, 1.1, 1.5],
        "libre": [False, True, True],
        "separacion": [2.9, 3.1, 3.3],
    })
    
    presion = pd.DataFrame({
        "gameId": [5],
        "playId": [5],
        "t_presion": [2.8],
        "por_sack": [True],
    })
    
    jugadas = pd.DataFrame({
        "gameId": [5],
        "playId": [5],
        "decisivo": [True],
    })
    
    return sep, presion, jugadas, "gana_receptor", 1.7


def ejecutar_verificacion():
    """Ejecuta los 5 casos y verifica resultados."""
    from backend.estado import estado
    from backend.calculos import relojes
    
    casos = [
        ("Caso 1: Gana receptor", crear_caso_1_gana_receptor()),
        ("Caso 2: Gana defensa", crear_caso_2_gana_defensa()),
        ("Caso 3: Sin presión", crear_caso_3_sin_presion()),
        ("Caso 4: Nunca libre", crear_caso_4_nunca_libre()),
        ("Caso 5: Sack con libre", crear_caso_5_sack_con_libre()),
    ]
    
    resultados = []
    
    for nombre, (sep, presion, jugadas, esperado_resultado, esperado_margen) in casos:
        # preparar estado
        estado.tablas["sep_cuadros"] = sep
        estado.tablas["presion"] = presion
        estado.tablas["jugadas"] = jugadas
        estado.resultados.clear()
        
        # ejecutar
        res = relojes.resultado_por_jugada()
        
        # verificar
        if len(res) == 1:
            fila = res.iloc[0]
            ok_resultado = fila["resultado"] == esperado_resultado
            ok_margen = (pd.isna(fila["margen"]) and pd.isna(esperado_margen)) or \
                       (not pd.isna(fila["margen"]) and not pd.isna(esperado_margen) and 
                        abs(fila["margen"] - esperado_margen) < 0.01)
            
            resultado_str = "✓" if ok_resultado and ok_margen else "✗"
            margen_str = f"{fila['margen']:.2f}" if not pd.isna(fila["margen"]) else "NaN"
            esperado_str = f"{esperado_margen:.2f}" if not pd.isna(esperado_margen) else "NaN"
            resultados.append(f"{resultado_str} {nombre}: resultado={fila['resultado']} (esperado={esperado_resultado}), margen={margen_str} (esperado={esperado_str})")
        else:
            resultados.append(f"✗ {nombre}: ERROR - {len(res)} filas en resultado")
    
    return "\n".join(resultados)


if __name__ == "__main__":
    print(ejecutar_verificacion())
