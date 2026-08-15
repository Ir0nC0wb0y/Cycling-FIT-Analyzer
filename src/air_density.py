

P0 = 101325.0
T0 = 288.15
LAPSE_RATE = 0.0065
GRAVITY = 9.80665
MOLAR_MASS_AIR = 0.0289644
GAS_CONSTANT = 8.31447
R_AIR = 287.05

R_AIR = 287.05      # J/(kg·K)

def air_density(temperature, altitude):
    """
    Calculate air density from temperature and altitude.

    Args:
        temperature: Air temperature in °C.
        altitude: Altitude in meters.

    Returns:
        Air density in kg/m³.
    """



    temperature_kelvin = temperature + 273.15

    pressure = (
        P0 * (1 - LAPSE_RATE * altitude / T0) ** (GRAVITY * MOLAR_MASS_AIR / (GAS_CONSTANT * LAPSE_RATE))
    )

    return pressure / (R_AIR * temperature_kelvin)