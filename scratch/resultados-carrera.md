# Resultados Carrera de Relojes - Parte A

## Filtro: decisivo (3.º y 4.º down)

### N total: 354 jugadas

## 1. Resultado de la carrera (P1)

- **Gana receptor**: 34.7% (n=123)
  - El receptor se libera antes de que llegue la presión
  
- **Gana defensa**: 0.6% (n=2)
  - La presión llega antes de que haya receptor libre
  - **n < 20**: porcentaje no confiable, se omiten métricas derivadas
  
- **Sin presión**: 64.7% (n=229)
  - La presión nunca llega al QB

- **Sack con libre**: 0.0%
  - Hubo sack aunque había receptor libre disponible

## 2. Curvas de tiempo

- **Mediana t_libre**: 1.0s
  - Tiempo en que el 50% de jugadas ya tiene receptor libre
  - **Confirmado**: t_libre nunca es < 1.0s (INICIO_LIBRE_SEG)
  
- **Mediana t_presion**: null (< 50% con presión)
  - Solo el 33.3% de jugadas tiene presión en t=4.0s
  - No se alcanza el 50% en la ventana medida
  
- **Ventaja receptor**: N/A (presión insuficiente)

### Puntos clave de las curvas:

| Tiempo | % Receptor libre | % Presión llegada |
|--------|------------------|-------------------|
| 0.5s | 0.0% | 0.3% |
| 1.0s | 96.3% | 0.3% |
| 1.5s | 97.7% | 0.3% |
| 2.0s | 98.3% | 2.3% |
| 2.5s | 98.6% | 19.2% |
| 3.0s | 98.9% | 29.4% |
| 3.5s | 98.9% | 32.2% |
| 4.0s | 99.2% | 33.3% |

## 3. Cadena completa (P2 → P1 → P3 → Conversión)

| Paso | % | n |
|------|---|---|
| Jugadas decisivas | 100.0% | 354 |
| Se libera (P2) | 99.2% | 351 |
| Gana carrera (P1) | 98.9% | 350 |
| Abierto al lanzar (P3) | 39.8% | 141 |
| Convierte | 17.8% | 63 |

## 4. KPIs clave

- **% Gana receptor**: 34.7% (n=123)
- **% Gana defensa**: 0.6% (n=2, **n < 20**)
- **Conversión cuando gana receptor**: 30.1%
- **Conversión cuando gana defensa**: null (n=2 < 20)
- **Mediana t_presion**: 2.5s

## 5. Insight

Muy pocas jugadas donde gana la defensa (n=2). El receptor se libera en 99.2% de las jugadas.

## Observaciones

- **t_libre >= 1.0s confirmado**: La mediana de 1.0s es correcta (el primer cuadro donde se puede estar "libre" según INICIO_LIBRE_SEG).
- **Muy poca presión en esta semana**: Solo 2 jugadas (0.6%) donde la defensa gana la carrera. Esto hace imposible comparar conversiones de forma confiable.
- El 64.7% sin presión es muy alto, indicando excelente protección de línea ofensiva.
- La mediana de t_libre en 1.0s muestra que los receptores se liberan inmediatamente tras pasar el umbral de tiempo.
- **Eslabón crítico P3**: La caída de 98.9% (gana carrera) a 39.8% (abierto al lanzar) sugiere que el cuello de botella está en mantener la separación hasta el momento del lanzamiento.
- Con n=123 jugadas donde gana el receptor, la conversión de 30.1% es estadísticamente confiable.

## 6. Comparación con otros filtros

| Filtro | N | Gana Receptor | Gana Defensa | Sin Presión |
|--------|---|---------------|--------------|-------------|| decisivo | 354 | 34.7% | 0.6% | 64.7% |
| pocas_yardas | 74 | 20.3% | 1.4% | 78.4% |
| normal | 743 | 24.2% | 1.6% | 74.2% |

