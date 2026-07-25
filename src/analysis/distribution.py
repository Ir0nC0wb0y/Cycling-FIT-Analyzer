from collections import defaultdict
from datetime import timedelta
import config


def generate_bins(records, field, width):
    """
    Generate numeric bins from the data range.
    """

    values = [
        record.get(field)
        for record in records
        if record.get(field) is not None
        and record.get(field) >= 0
    ]

    if not values:
        return []

    minimum = int(min(values) // width * width)
    maximum = int(max(values) // width * width + width)

    bins = []

    current = minimum

    while current < maximum:
        bins.append(
            {
                "label": f"{current}-{current + width - 1}",
                "min": current,
                "max": current + width - 1,
            }
        )

        current += width

    return bins

def build_stddev_bins(mean, stddev, bin_config):
    """
    Convert standard deviation bin definitions into value bins.

    Input:
        min/max are standard deviation multipliers.

    Example:
        -1.0 means mean - 1σ
         2.0 means mean + 2σ
    """

    bins = []

    for bin in bin_config:

        minimum = (
            None
            if bin["min"] is None
            else mean + (bin["min"] * stddev)
        )

        maximum = (
            None
            if bin["max"] is None
            else mean + (bin["max"] * stddev)
        )

        bins.append(
            {
                "label": bin["label"],
                "min": minimum,
                "max": maximum,
            }
        )

    return bins

def build_distribution(records, field, bins, moving_only=True):
    """
    Build a time-weighted distribution for a field.

    Parameters
    ----------
    bins : list[dict]
        List of bin definitions.

    Returns
    -------
    dict
        label -> timedelta
    """

    histogram = {
        bin["label"]: timedelta()
        for bin in bins
    }

    for current, next_record in zip(records, records[1:]):

        if (
            moving_only
            and current.get(
                "speed",
                config.MISSING_DATA_VALUE,
            ) <= 0
        ):
            continue

        value = current.get(field)

        if value is None:
            continue

        dt = (
            next_record["time"]
            - current["time"]
        )

        for bin in bins:

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
                histogram[bin["label"]] += dt
                break

    return histogram

def print_distribution(distribution, bins, title="Distribution"):
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

    label_width = max(len(bin["label"]) for bin in bins)
    bounds_width = max(
        len(format_bounds(bin["min"], bin["max"]))
        for bin in bins
)

    print()
    print(title)
    print("-" * 80)

    for bin in bins:

        label = bin["label"]
        bounds = format_bounds(
            bin["min"],
            bin["max"]
        )

        duration = distribution[label]

        percent = (
            duration / total_time
            if total_time.total_seconds() > 0
            else 0
        )

        if (
            not config.REPORT_SHOW_EMPTY_BINS
            and percent < config.REPORT_MIN_BIN_PERCENT
        ):
            continue

        bar_length = (
            int(duration / largest * config.REPORT_BAR_WIDTH)
            if largest.total_seconds() > 0
            else 0
        )

        bar = config.REPORT_BAR_CHARACTER * bar_length

        print(
            f"{label:<{label_width}}  "
            f"{bounds:<{bounds_width}}  "
            f"{duration.total_seconds()/60:6.1f} min  "
            f"{percent:6.1%}  "
            f"{bar}"
        )

    print("-" * 80)

    print(
        f"{'Total':<{label_width}}  "
        f"{'':<{bounds_width}}  "
        f"{total_time.total_seconds()/60:6.1f} min  "
        f"{'100.0%':>6}"
    )

def format_bounds(minimum, maximum):
    """
    Format bounds for display.
    """

    if minimum is None:
        return f"< {maximum:.1f}"

    if maximum is None:
        return f"> {minimum:.1f}"

    return f"{minimum:.1f}-{maximum:.1f}"