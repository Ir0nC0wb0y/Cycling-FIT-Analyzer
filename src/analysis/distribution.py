from collections import defaultdict
from datetime import timedelta
import config


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
        if moving_only and current.get("enhanced_speed", config.MISSING_DATA_VALUE) <= 0:
            continue

        value = current.get(field)

        if value is None:
            continue

        dt = next_record["timestamp"] - current["timestamp"]

        for bin in bins:

            label = bin["label"]

            minimum = (
                float("-inf")
                if bin["min"] is None
                else bin["min"]
            )

            maximum = (
                float("inf")
                if bin["max"] is None
                else bin["max"]
            )

            if minimum <= value <= maximum:
                histogram[label] += dt
                break

    return dict(histogram)

def print_distribution(distribution, title="Distribution"):
    """
    Print a time distribution returned by build_distribution().
    """

    if not distribution:
        print()
        print(title)
        print("------------------------------")
        print("No data.")
        return

    total_time = sum(distribution.values(), timedelta())
    largest = max(distribution.values())

    print()
    print(title)
    print("-" * 60)

    for label, duration in distribution.items():

        percent = (
            duration / total_time
            if total_time.total_seconds() > 0
            else 0
        )

        bar_length = (
            int(duration / largest * config.REPORT_BAR_WIDTH)
            if largest.total_seconds() > 0
            else 0
        )

        bar = config.REPORT_BAR_CHARACTER * bar_length

        print(
            f"{label:<12}"
            f"{duration.total_seconds()/60:6.1f} min  "
            f"{percent:6.1%}  "
            f"{bar}"
        )

    print("-" * 60)
    print(
        f"{'Total':<12}"
        f"{total_time.total_seconds()/60:6.1f} min  "
        f"{'100.0%':>6}"
    )