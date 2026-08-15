
## Need to make conversions for incoming units of "time" and "duration" based on standard time objects

def convert(value, from_unit, to_unit):

    if from_unit == to_unit or value == None:
        return value

    # Handle lists/collections first
    if isinstance(value, list):
        return [
            convert(item, from_unit, to_unit)
            for item in value
        ]

    # Speeds
    if from_unit in ["m/s", "mph", "kph"]:
        return convert_speed(
            value,
            from_unit,
            to_unit
        )

    # Lengths
    if from_unit in ["m", "mi", "ft"]:
        return convert_length(
            value,
            from_unit,
            to_unit
        )

    # Temperature
    if from_unit in ["C", "F"]:
        return convert_temperature(
            value,
            from_unit,
            to_unit
        )

    # Time
    if from_unit in ["duration", "s", "min", "hr"]:
        return convert_time(
            value,
            from_unit,
            to_unit
        )

    if from_unit in ["lb", "kg", "g"]:
        return convert_mass(
            value,
            from_unit,
            to_unit
        )

    raise ValueError(
        f"No conversion available: {from_unit} -> {to_unit}"
    )

def convert_speed(value, from_unit, to_unit):
    """
    Convert speed between supported units.
    """

    if from_unit == to_unit:
        return value

    if from_unit == "m/s" and to_unit == "mph":
        return value * 2.23694

    if from_unit == "mph" and to_unit == "m/s":
        return value / 2.23694

    if from_unit == "m/s" and to_unit == "kph":
        return value * 3.6

    if from_unit == "kph" and to_unit == "m/s":
        return value / 3.6

    if from_unit == "mph" and to_unit == "kph":
        return value * 1.60934

    if from_unit == "kph" and to_unit == "mph":
        return value / 1.60934

    raise ValueError(
        f"Unsupported speed conversion: {from_unit} -> {to_unit}"
    )


def convert_length(value, from_unit, to_unit):
    """
    Convert distance between supported units.
    """

    if from_unit == to_unit:
        return value

    if from_unit == "m" and to_unit == "mi":
        return value / 1609.34

    if from_unit == "mi" and to_unit == "m":
        return value * 1609.34

    if from_unit == "m" and to_unit == "ft":
        return value * 3.28084

    if from_unit == "ft" and to_unit == "m":
        return value / 3.28084

    if from_unit == "mi" and to_unit == "ft":
        return value * 5280

    if from_unit == "ft" and to_unit == "mi":
        return value / 5280

    raise ValueError(
            f"Unsupported length conversion: {from_unit} -> {to_unit}"
        )

def convert_temperature(value, from_unit, to_unit):
    """
    Convert distance between supported units.
    """

    if from_unit == to_unit:
        return value

    if from_unit == "C" and to_unit == "F":
        return value * 9/5 + 32

    if from_unit == "F" and to_unit == "C":
        return (value - 32) * 5/9

    raise ValueError(
                f"Unsupported temperature conversion: {from_unit} -> {to_unit}"
            )

def convert_time(value, from_unit, to_unit):
    """
    Convert duration between supported units.
    """

    if from_unit == to_unit:
        return value

    if from_unit == "duration" and to_unit == "s":
        return value.total_seconds()

    if from_unit == "duration" and to_unit == "min":
        return value.total_seconds() / 60

    if from_unit == "duration" and to_unit == "hr":
        return value.total_seconds() / 3600

def convert_mass(value, from_unit, to_unit):
    """
    Convert mass between supported units.
    """

    if from_unit == "kg" and to_unit == "lb":
        return value * 2.20462

    if from_unit == "lb" and to_unit == "kg":
        return value / 2.20462

    if from_unit == "kg" and to_unit == "g":
        return value * 1000

    if from_unit == "g" and to_unit == "kg":
        return value / 1000

    if from_unit == "lb" and to_unit == "g":
        return value * 453.592

    if from_unit == "g" and to_unit == "lb":
        return value / 453.592

    raise ValueError(
            f"Unsupported temperature conversion: {from_unit} -> {to_unit}"
        )