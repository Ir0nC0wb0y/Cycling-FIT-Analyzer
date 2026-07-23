from collections import defaultdict
from datetime import timedelta


def build_distribution(records, field, bins, moving_only=True):
    """
    Build a time-weighted distribution for a field.

    Returns:
        {
            "120-129": timedelta(...),
            "130-139": timedelta(...),
            ...
        }
    """

    histogram = defaultdict(timedelta)

    for current, next_record in zip(records, records[1:]):

        # Skip stationary records if requested
        if moving_only and current.get("enhanced_speed", 0) <= 0:
            continue

        value = current.get(field)

        if value is None:
            continue

        dt = next_record["timestamp"] - current["timestamp"]

        for bin in bins:

            minimum = bin.get("min")
            maximum = bin.get("max")

            if minimum is None and value <= maximum:
                histogram[bin["label"]] += dt
                break

            elif maximum is None and value >= minimum:
                histogram[bin["label"]] += dt
                break

            elif minimum <= value <= maximum:
                histogram[bin["label"]] += dt
                break

    return dict(histogram)