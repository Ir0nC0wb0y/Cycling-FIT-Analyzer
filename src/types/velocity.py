from dataclasses import dataclass
from src.types.quantity import Quantity
import src.units as unit_converter
import math

@dataclass(frozen=True)
class Velocity:
    speed: Quantity
    direction: Quantity
    # Convention for direction angles:
    #    0 - N
    #   90 - E
    #  180 - S
    #  270 - W

    def __str__(self):
        return f"{self.speed} @ {self.direction}"


    def __format__(self, format_spec):
        return (
            f"{self.speed:{format_spec}u}"
            f" @ "
            f"{self.direction:{format_spec}u}"
        )

    def relative_to(self, other):
        """
        Calculate this velocity relative to another velocity.

        The result is:

            self - other

        The result is expressed in the units of `self`.
        """

        self_speed = unit_converter.convert(
            self.speed.value,
            self.speed.unit,
            "m/s",
        )

        other_speed = unit_converter.convert(
            other.speed.value,
            other.speed.unit,
            "m/s",
        )

        self_direction = math.radians(
            unit_converter.convert(
                self.direction.value,
                self.direction.unit,
                "deg",
            )
        )

        other_direction = math.radians(
            unit_converter.convert(
                other.direction.value,
                other.direction.unit,
                "deg",
            )
        )

        self_x = self_speed * math.sin(self_direction)
        self_y = self_speed * math.cos(self_direction)

        other_x = other_speed * math.sin(other_direction)
        other_y = other_speed * math.cos(other_direction)

        result_x = self_x - other_x
        result_y = self_y - other_y

        result_speed = math.sqrt(
            result_x ** 2
            + result_y ** 2
        )

        result_direction = math.degrees(
            math.atan2(result_x, result_y)
        ) % 360

        return Velocity(
            speed=Quantity(
                unit_converter.convert(
                    result_speed,
                    "m/s",
                    self.speed.unit,
                ),
                self.speed.unit,
            ),
            direction=Quantity(
                unit_converter.convert(
                    result_direction,
                    "deg",
                    self.direction.unit,
                ),
                self.direction.unit,
            ),
        )