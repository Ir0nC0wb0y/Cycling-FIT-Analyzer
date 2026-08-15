from datetime import timedelta

import config
import src.units as unit_converter


def build_power_profile(ride, bins):
    """
    Build a time-weighted power profile.

    Each power bin contains:
        - total time
        - average speed
        - average grade
        - average gravity power
        - average rolling power
        - average aerodynamic power
        - average acceleration power

    Returns:
        {
            "50-75": {
                "time": timedelta,
                "avg_speed": float,
                "avg_grade": float,
                "avg_gravity": float,
                "avg_rolling": float,
                "avg_aero": float,
                "avg_acceleration": float,
            },
            ...
        }
    """

    profile = {
        bin["label"]: {
            "time": timedelta(),

            "speed_time": 0.0,
            "grade_time": 0.0,

            "gravity_time": 0.0,
            "rolling_time": 0.0,
            "aero_time": 0.0,
            "acceleration_time": 0.0,

            "samples": 0,
        }
        for bin in bins
    }

    for current, next_record in zip(
        ride.records,
        ride.records[1:],
    ):

        power = current.get("estimated_power")

        if power is None:
            continue

        speed = current.get("speed")

        if (
            speed is None
            or speed <= config.THRESHOLD_MOVING_SPEED
        ):
            continue

        dt = (
            next_record["time"]
            - current["time"]
        )

        dt_seconds = dt.total_seconds()

        if dt_seconds <= 0:
            continue

        # Convert speed to configured display unit.
        speed_display = unit_converter.convert(
            speed,
            ride.units["speed"],
            config.FIT_FIELDS["speed"]["display_unit"],
        )

        #
        # Find the power bin.
        #
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

            if minimum <= power <= maximum:

                entry = profile[bin["label"]]

                entry["time"] += dt

                #
                # Time-weighted values
                #
                entry["speed_time"] += (
                    speed_display * dt_seconds
                )

                grade = current.get("grade")

                if grade is not None:
                    entry["grade_time"] += (
                        grade * dt_seconds
                    )

                gravity = current.get("power_gravity")

                if gravity is not None:
                    entry["gravity_time"] += (
                        gravity * dt_seconds
                    )

                rolling = current.get("power_rolling")

                if rolling is not None:
                    entry["rolling_time"] += (
                        rolling * dt_seconds
                    )

                aero = current.get("power_aero")

                if aero is not None:
                    entry["aero_time"] += (
                        aero * dt_seconds
                    )

                acceleration = current.get(
                    "power_acceleration"
                )

                if acceleration is not None:
                    entry["acceleration_time"] += (
                        acceleration * dt_seconds
                    )

                entry["samples"] += 1

                break

    #
    # Convert accumulated values into averages.
    #
    for entry in profile.values():

        total_seconds = entry["time"].total_seconds()

        if total_seconds <= 0:
            entry["avg_speed"] = None
            entry["avg_grade"] = None
            entry["avg_gravity"] = None
            entry["avg_rolling"] = None
            entry["avg_aero"] = None
            entry["avg_acceleration"] = None
            continue

        entry["avg_speed"] = (
            entry["speed_time"]
            / total_seconds
        )

        entry["avg_grade"] = (
            entry["grade_time"]
            / total_seconds
        )

        entry["avg_gravity"] = (
            entry["gravity_time"]
            / total_seconds
        )

        entry["avg_rolling"] = (
            entry["rolling_time"]
            / total_seconds
        )

        entry["avg_aero"] = (
            entry["aero_time"]
            / total_seconds
        )

        entry["avg_acceleration"] = (
            entry["acceleration_time"]
            / total_seconds
        )

    return profile


def print_power_profile(profile, bins):
    """
    Print the power profile report.
    """

    print()
    print("Power Analysis")
    print("-" * 100)

    print(
        f"{'Power Range':<14}"
        f"{'Time':>10}"
        f"{'%':>8}"
        f"{'Avg Speed':>12}"
        f"{'Grade':>10}"
        f"{'Gravity':>11}"
        f"{'Rolling':>11}"
        f"{'Aero':>10}"
        f"{'Accel':>10}"
    )

    print("-" * 100)

    total_time = sum(
        (
            entry["time"]
            for entry in profile.values()
        ),
        timedelta(),
    )

    total_seconds = total_time.total_seconds()

    for bin in bins:

        label = bin["label"]
        entry = profile[label]

        duration = entry["time"]

        if duration.total_seconds() == 0:
            continue

        percent = (
            duration / total_time
            if total_seconds > 0
            else 0
        )

        speed = (
            f"{entry['avg_speed']:.2f}"
            if entry["avg_speed"] is not None
            else "-"
        )

        grade = (
            f"{entry['avg_grade']:+.2f}%"
            if entry["avg_grade"] is not None
            else "-"
        )

        gravity = (
            f"{entry['avg_gravity']:.1f}"
            if entry["avg_gravity"] is not None
            else "-"
        )

        rolling = (
            f"{entry['avg_rolling']:.1f}"
            if entry["avg_rolling"] is not None
            else "-"
        )

        aero = (
            f"{entry['avg_aero']:.1f}"
            if entry["avg_aero"] is not None
            else "-"
        )

        acceleration = (
            f"{entry['avg_acceleration']:.1f}"
            if entry["avg_acceleration"] is not None
            else "-"
        )

        print(
            f"{label:<14}"
            f"{duration.total_seconds()/60:8.1f} min"
            f"{percent:8.1%}"
            f"{speed:>12}"
            f"{grade:>10}"
            f"{gravity:>11}"
            f"{rolling:>11}"
            f"{aero:>10}"
            f"{acceleration:>10}"
        )

    print("-" * 100)

    print(
        f"{'Total':<14}"
        f"{total_time.total_seconds()/60:8.1f} min"
        f"{'100.0%':>8}"
    )