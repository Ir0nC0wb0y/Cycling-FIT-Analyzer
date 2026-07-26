import config
from datetime import timedelta
import src.units as unit_converter


def calculate_effort(hr, cadence, grade):
    """
    Estimate effort level from heart rate,
    cadence, and grade.

    Returns an effort score.
    """

    score = 0

    # Heart rate contribution
    if hr is not None:
        if hr < 130:
            score += 10
        elif hr < 145:
            score += 25
        elif hr < 160:
            score += 40
        else:
            score += 60


    # Grade contribution
    if grade is not None:
        if grade < -2:
            score -= 10
        elif grade < 1:
            score += 0
        elif grade < 3:
            score += 15
        else:
            score += 30


    # Cadence contribution
    if cadence is not None:
        if cadence < 70:
            score += 10
        elif cadence > 100:
            score += 5


    return score

def classify_effort(score):

    if score < 25:
        return "Recovery"

    elif score < 45:
        return "Endurance"

    elif score < 65:
        return "Tempo"

    else:
        return "Hard"


def build_effort_profile(ride):

    zones = [
        "Recovery",
        "Endurance",
        "Tempo",
        "Hard",
    ]

    profile = {
        zone: {
            "time": timedelta(),
            "hr_sum": 0,
            "cadence_sum": 0,
            "speed_sum": 0,
            "grade_sum": 0,
            "samples": 0,

            # calculated values
            "avg_speed": None,
            "avg_hr": None,
            "avg_cadence": None,
            "avg_grade": None,
        }
        for zone in zones
    }


    for current, next_record in zip(
        ride.records,
        ride.records[1:]
    ):

        dt = (
            next_record["time"]
            - current["time"]
        )


        hr = current.get("heart_rate")
        cadence = current.get("cadence")
        grade = current.get("grade")
        speed = current.get("speed")
        if speed is not None:
            speed = unit_converter.convert(
                speed,
                ride.units["speed"],
                config.FIT_FIELDS["speed"]["display_unit"]
            )


        score = calculate_effort(
            hr,
            cadence,
            grade
        )


        zone = classify_effort(score)

        entry = profile[zone]


        entry["time"] += dt


        if hr is not None:
            entry["hr_sum"] += hr

        if cadence is not None:
            entry["cadence_sum"] += cadence

        if grade is not None:
            entry["grade_sum"] += grade

        if speed is not None:
            entry["speed_sum"] += speed


        entry["samples"] += 1


    # Convert sums to averages
    for entry in profile.values():

        samples = entry["samples"]

        if samples:

            entry["avg_hr"] = (
                entry["hr_sum"] / samples
            )

            entry["avg_cadence"] = (
                entry["cadence_sum"] / samples
            )

            entry["avg_grade"] = (
                entry["grade_sum"] / samples
            )

            entry["avg_speed"] = (
                entry["speed_sum"] / samples
            )

        else:

            entry["avg_hr"] = None
            entry["avg_cadence"] = None
            entry["avg_grade"] = None
            entry["avg_speed"] = None


    return profile

def print_effort_profile(profile):

    zone_width = 18
    time_width = 12
    percent_width = 8
    speed_width = 10
    hr_width = 10
    cad_width = 12
    grade_width = 12

    total_time = sum(
        (
            entry["time"]
            for entry in profile.values()
        ),
        timedelta()
    )


    print()
    print("Effort Analysis")
    print("-" * 70)

    print(
        f"{'Zone':<{zone_width}}"
        f"{'Time':>{time_width}}"
        f"{'%':>{percent_width}}"
        f"{'Avg Speed':>{speed_width}}"
        f"{'Avg HR':>{hr_width}}"
        f"{'Avg Cad':>{cad_width}}"
        f"{'Grade':>{grade_width}}"
    )

    line_width = (
        zone_width
        + time_width
        + percent_width
        + speed_width
        + hr_width
        + cad_width
        + grade_width
    )

    print("-" * line_width)


    for name, entry in profile.items():

        duration = entry["time"]

        if duration.total_seconds() == 0:
            continue


        percent = duration / total_time


        speed = (
            f"{entry['avg_speed']:.1f}"
            if entry["avg_speed"] is not None
            else "-"
        )

        hr = (
            f"{entry['avg_hr']:.0f}"
            if entry["avg_hr"] is not None
            else "-"
        )

        cad = (
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
            f"{name:<{zone_width}}"
            f"{duration.total_seconds()/60:>{time_width-4}.1f} min"
            f"{percent:>{percent_width}.1%}"
            f"{speed:>{speed_width}}"
            f"{hr:>{hr_width}}"
            f"{cad:>{cad_width}}"
            f"{grade:>{grade_width}}"
        )


    print("-" * line_width)

    print(
        f"{'Total':<15}"
        f"{total_time.total_seconds()/60:8.1f} min"
        f"{'100.0%':>8}"
    )