from src.types.velocity import Velocity
from src.types.quantity import Quantity
from src.environment.wind import create_wind

rider = Velocity(
    Quantity(15, "mph"),
    Quantity(0,"deg"),
)

#wind = Velocity(
#    Quantity(5, "m/s"),
#    Quantity(90, "deg"),
#)
wind = create_wind(5, 90, speed_unit="m/s")

print("Starting unit test:")

air = rider.relative_to(wind)
print(air)

print("Complete")