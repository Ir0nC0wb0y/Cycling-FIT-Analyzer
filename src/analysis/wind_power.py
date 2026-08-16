import config
import src.power_calc as power_calc
from src.types.velocity import Velocity
from src.types.quantity import Quantity
from src.environment.wind import create_wind


def calculate_wind_power(ride, wind):
    """
    Calculate average aero power for a ride under
    a specified hypothetical wind.
    """

    aero_power_sum = 0.0
    total_time = 0.0

    for current, next_record in zip(
        ride.records,
        ride.records[1:],
    ):

        speed = current.get("speed")
        direction = current.get("direction")

        if (
            speed is None
            or direction is None
        ):
            continue

        if speed <= config.THRESHOLD_MOVING_SPEED:
            continue

        density = current.get("air_density")

        if density is None:
            continue

        #
        # Create the rider's velocity vector.
        #
        rider = rider_velocity(
            ride,
            current,
        )

        #
        # Calculate velocity of the rider relative
        # to the air.
        #
        air = rider.relative_to(wind)

        #
        # Calculate aero power using the magnitude
        # of the relative air velocity.
        #
        cd_a = power_calc.get_cd_a(
            config.AERO_POSITION
        )

        aero_power = power_calc.power_aero(
            air_speed=air.speed.value,
            cd_a=cd_a,
            density=density,
        )

        #
        # Time represented by this record.
        #
        dt = (
            next_record["time"]
            - current["time"]
        ).total_seconds()

        if dt <= 0:
            continue

        aero_power_sum += aero_power * dt
        total_time += dt

    if total_time <= 0:
        return None

    return aero_power_sum / total_time


def rider_velocity(ride, record):
    return Velocity(
        speed=Quantity(
            record["speed"],
            ride.units["speed"],
        ),
        direction=Quantity(
            record["direction"],
            ride.units["direction"],
        ),
    )

def wind_power_sweep(ride, wind_speeds, wind_directions):
    """
    Calculate average aero power for a range of
    hypothetical wind speeds and directions.

    Parameters
    ----------
    ride : Ride
        Ride being analyzed.

    wind_speeds : iterable
        Wind speeds. Values are interpreted using the
        unit supplied to create_wind().

    wind_directions : iterable
        Wind directions in degrees.

    Returns
    -------
    list[dict]
        One result for each speed/direction combination.
    """

    results = []

    for speed in wind_speeds:

        for direction in wind_directions:

            wind = create_wind(
                speed=speed,
                direction=direction,
                speed_unit="mph",
                direction_unit="deg",
            )

            aero_power = calculate_wind_power(
                ride,
                wind,
            )

            results.append(
                {
                    "wind": wind,
                    "aero_power": aero_power,
                }
            )

    return results