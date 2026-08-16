from src.types.velocity import Velocity
from src.types.quantity import Quantity

def create_wind(speed, direction, speed_unit = None, direction_unit=None):
    ## Creates a velocity vector of the wind's "from" direction

    if speed_unit is None:
        speed_unit = "mph"

    if direction_unit is None:
        direction_unit = "deg"

    return Velocity(
        speed=Quantity(speed, speed_unit),
        direction=Quantity(direction, direction_unit),
    )
