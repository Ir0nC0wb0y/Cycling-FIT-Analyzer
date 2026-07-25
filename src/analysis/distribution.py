from collections import defaultdict
from datetime import timedelta
import config
import src.units as unit_converter


def generate_bins(ride, field, width):
    """
    Generate numeric bins from the data range.
    """

    #print(f"converting {field} from {ride.units[field]} to {config.FIT_FIELDS[field]["display_unit"]}")
    values = []

    for record in ride.records:

        value = record.get(field)

        if value is None or value < 0:
            continue

        value = unit_converter.convert(
            value,
            ride.units[field],
            config.FIT_FIELDS[field]["display_unit"]
        )

        values.append(value)

    if not values:
        return []

    minimum = int(min(values) // width * width)
    maximum = int(max(values) // width * width + width)

    bins = []

    current = minimum

    while current < maximum:
        bins.append(
            {
                "label": f"{current}-{current + width}",
                "min": current,
                "max": current + width,
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

def build_distribution(ride, field, bins, moving_only=True):
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

    for current, next_record in zip(ride.records, ride.records[1:]):

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

        value = unit_converter.convert(
            value,
            ride.units[field],
            config.FIT_FIELDS[field]["display_unit"]
        )

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

def print_distribution(distribution, bins, title="Distribution", show_bounds=True):
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

    if show_bounds:
        bounds_width = max(
            len(format_bounds(bin["min"], bin["max"]))
            for bin in bins
        )
    else:
        bounds_width = 0

    label_width = max(len(bin["label"]) for bin in bins)
    line_width = (
        label_width
        + 2
        + bounds_width
        + 2
        + len("000.0 min")
        + 2
        + len("100.0%")
        + 2
        + config.REPORT_BAR_WIDTH
    )

    print()
    print(title)
    print("-" * line_width)

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

        if show_bounds:
            print(
                f"{label:<{label_width}}  "
                f"{bounds:<{bounds_width}}  "
                f"{duration.total_seconds()/60:6.1f} min  "
                f"{percent:6.1%}  "
                f"{bar}"
            )
        else:
            print(
                f"{label:<{label_width}}  "
                f"{duration.total_seconds()/60:6.1f} min  "
                f"{percent:6.1%}  "
                f"{bar}"
            )


    print("-" * line_width)

    if show_bounds:
        print(
            f"{'Total':<{label_width}}  "
            f"{'':<{bounds_width}}  "
            f"{total_time.total_seconds()/60:6.1f} min  "
            f"{'100.0%':>6}"
        )
    else:
        print(
            f"{'Total':<{label_width}}  "
            f"{total_time.total_seconds()/60:6.1f} min  "
            f"{'100.0%':>6}"
        )

    #print(f"Distribution total: {total_time}")
    

def format_bounds(minimum, maximum):
    """
    Format bounds for display.
    """

    if minimum is None:
        return f"< {maximum:.1f}"

    if maximum is None:
        return f"> {minimum:.1f}"

    return f"{minimum:.1f}-{maximum:.1f}"