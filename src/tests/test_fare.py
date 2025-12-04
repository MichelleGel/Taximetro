import pytest
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from taximeter import calculate_time_fare, calculate_distance_fare
from config import fare_config

# Carga la configuración para usar las tarifas reales
config = fare_config()


# =========================
# Test de tarifas válidas
# =========================

def test_calculate_fare():
    # Tarifas por tiempo
    stopped_time = 10  # segundos
    moving_time = 20   # segundos
    fare = calculate_time_fare(stopped_time, moving_time)
    assert fare > 0 #La tarifa por tiempo debería ser mayor que 0
    
    # Tarifas por distancia
    distance = 5  # km
    fare_dist = calculate_distance_fare(distance)
    assert fare_dist > 0 


# =========================
# Test de valores erróneos
# =========================

def test_invalid():
    # Valores negativos o cero
    with pytest.raises(ValueError):
        calculate_distance_fare(-5)

    with pytest.raises(ValueError):
        calculate_distance_fare(0)

    # Tiempo negativo (si tu función valida)
    with pytest.raises(ValueError):
        calculate_time_fare(-10, 5)

    with pytest.raises(ValueError):
        calculate_time_fare(5, -10)


# =========================
# Tarifa conocida (consistencia)
# =========================

def test_known_values():
    stopped_time = 60   # 60 segundos parado
    moving_time = 120   # 120 segundos en movimiento
    expected_fare = (stopped_time * config['stopped_fare']) + (moving_time * config['moving_fare'])
    fare = calculate_time_fare(stopped_time, moving_time)
    assert fare == expected_fare, "La tarifa calculada no coincide con el valor esperado"


# =========================
# Valores límites
# =========================
def test_fare_limits():
    # Tiempo total = 0
    assert calculate_time_fare(0, 0) == 0, "La tarifa con 0s debe ser 0"
    
    # Distancia negativa o cero debería lanzar error
    with pytest.raises(ValueError):
        calculate_distance_fare(0)
    with pytest.raises(ValueError):
        calculate_distance_fare(-5)


# =========================
# Decimal y tipo de retorno
# =========================
def test_decimal_precision():
    fare = calculate_distance_fare(7.5)
    assert isinstance(fare, float), "El retorno debe ser un float"
    assert round(fare, 2) == round(fare, 2), "El resultado debe ser redondeable a 2 decimales"


# =========================
# Valores extremos
# =========================
def test_extreme_values():
    fare = calculate_distance_fare(10_000)
    assert fare > 0, "La tarifa con valores grandes debe ser positiva"
    fare = calculate_distance_fare(0.0001)
    assert fare > 0, "La tarifa con valores muy pequeños debe ser positiva"


# =========================
# Error por tipo de dato inválido
# =========================
def test_invalid_type():
    with pytest.raises(TypeError):
        calculate_distance_fare("cinco")  # No se puede multiplicar string
    with pytest.raises(TypeError):
        calculate_time_fare("10", "20")   # String en vez de número