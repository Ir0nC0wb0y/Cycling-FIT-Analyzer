import config
from datetime import timedelta
import src.units as unit_converter

def build_speed_profile(ride, bins):
    """
    Build speed bands with time-weighted HR and cadence data.

    Returns:
        {
            "12-14": {
                "time": timedelta,
                "avg_hr": float,
                "avg_cadence": float,
                "avg_grade": float
            },
            ...
        }
    """

    profile = {
        bin["label"]: {
            "time": timedelta(),
            "hr_sum": 0,
            "cadence_sum": 0,
            "grade_sum": 0,
            "samples": 0,
        }
        for bin in bins
    }

    for current, next_record in zip(
        ride.records,
        ride.records[1:]
    ):

        speed = current.get("speed")

        if speed is None:
            continue

        if speed <= config.THRESHOLD_MOVING_SPEED:
            continue

        speed = unit_converter.convert(
            speed,
            ride.units["speed"],
            config.FIT_FIELDS["speed"]["display_unit"]
        )

        if speed is None:
            continue

        dt = (
            next_record["time"]
            - current["time"]
        )

        #elevation_change = (
        #    next_record["altitude"]
        #    - current["altitude"]
        #)

        #distance_change = (
        #    next_record["distance"]
        #    - current["distance"]
        #)

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

            if minimum <= speed <= maximum:

                entry = profile[bin["label"]]

                entry["time"] += dt
                #entry["elevation_change"] += elevation_change
                #entry["distance_change"] += distance_change

                hr = current.get("heart_rate")
                if hr is not None:
                    entry["hr_sum"] += hr

                cadence = current.get("cadence")
                if cadence is not None:
                    entry["cadence_sum"] += cadence

                grade = current.get("grade")
                if grade is not None:
                    entry["grade_sum"] += grade

                # Elevation change
                #altitude = current.get("altitude")
                #next_altitude = next_record.get("altitude")

                #if (
                #    altitude is not None
                #    and next_altitude is not None
                #):
                #    entry["elevation_change"] += (
                #        next_altitude - altitude
                #    )

                entry["samples"] += 1

                break

    # Convert sums into averages
    for entry in profile.values():

        samples = entry["samples"]

        #if entry["distance_change"] > config.MIN_GRADE_DISTANCE:
        #    entry["grade"] = (
        #        entry["elevation_change"]
        #        /
        #        entry["distance_change"]
        #        * 100
        #    )
        #else:
        #    entry["grade"] = None

        if samples > 0:

            entry["avg_hr"] = (
                entry["hr_sum"] / samples
            )

            entry["avg_cadence"] = (
                entry["cadence_sum"] / samples
            )

            entry["avg_grade"] = (
                entry["grade_sum"] / samples
            )

        else:

            entry["avg_hr"] = None
            entry["avg_cadence"] = None
            entry["avg_grade"] = None


    return profile


def print_speed_profile(profile, bins):
    """
    Print speed profile report.
    """

    print()
    print("Speed Analysis")
    print("-" * 75)

    print(
        f"{'Speed Range':<14}"
        f"{'Time':>10}"
        f"{'%':>8}"
        f"{'Avg HR':>10}"
        f"{'Avg Cad':>12}"
        f"{'Grade':>10}"
    )

    print("-" * 75)

    total_time = sum(
        (
            entry["time"]
            for entry in profile.values()
        ),
        timedelta()
    )

    for bin in bins:

        label = bin["label"]
        entry = profile[label]

        duration = entry["time"]

        if duration.total_seconds() == 0:
            continue

        percent = (
            duration / total_time
        )

        hr = (
            f"{entry['avg_hr']:.0f}"
            if entry["avg_hr"] is not None
            else "-"
        )

        cadence = (
            f"{entry['avg_cadence']:.0f}"
            if entry["avg_cadence"] is not None
            else "-"
        )

        grade = (
            f"{entry['avg_grade']:+.2f}%"
            if entry["avg_grade"] is not None
            else "-"
        )

        print(
            f"{label:<14}"
            f"{duration.total_seconds()/60:8.1f} min"
            f"{percent:8.1%}"
            f"{hr:>10}"
            f"{cadence:>12}"
            f"{grade:>10}"
        )

    print("-" * 75)

    print(
        f"{'Total':<14}"
        f"{total_time.total_seconds()/60:8.1f} min"
        f"{'100.0%':>8}"
    )