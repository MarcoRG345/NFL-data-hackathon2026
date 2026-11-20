"""Cinta superior. DUEÑA: B. (Esqueleto: 9 elementos de mentira, marcados como ejemplo.)

Cuando sea real, B usará relojes.resultado_por_jugada() (vacío/todo sin_presion mientras A no la entregue:
entonces la cinta usa solo giro y aire)."""


def ticker(filtro: str) -> list[dict]:
    return [
        {"texto": "Ejemplo: el receptor gana la carrera en 41 % de las jugadas", "tipo": "receptor"},
        {"texto": "Ejemplo: la defensa llega primero en 34 %", "tipo": "defensa"},
        {"texto": "Ejemplo: en 25 % la presión nunca llega", "tipo": "sin_presion"},
        {"texto": "Ejemplo: un giro brusco gana 1.5 yd de separación", "tipo": "giro"},
        {"texto": "Ejemplo: abierto al lanzar, 75 % de pases completos", "tipo": "aire"},
        {"texto": "Ejemplo: mediana de la presión en 2.7 s", "tipo": "defensa"},
        {"texto": "Ejemplo: el receptor libre llega a 2.1 s", "tipo": "receptor"},
        {"texto": "Ejemplo: giros suaves ganan 0.9 yd", "tipo": "giro"},
        {"texto": "Ejemplo: cerrado al lanzar, 49 % completos", "tipo": "aire"},
    ]
