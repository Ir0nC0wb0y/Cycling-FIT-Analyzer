import config
import src.units as unit_converter
from datetime import timedelta

def build_speed_profile(ride):
    """
    Analyze speed distribution using meaningful speed zones.
    """

    speed_zones = [
        {
            "label": "Stopped / Recovery",
            "min": 0,
            "max": 5,
        },
        {
            "label": "Easy",
            "min": 5,
            "max": 12,
        },
        {
            "label": "Endurance",
            "min": 12,
            "max": 16,
        },
        {
            "label": "Tempo",
            "min": 16,
            "max": 18,
        },
        {
            "label": "Fast",
            "min": 18,
            "max": None,
        },
    ]

    return speed_zones

def build_speed_profile(ride):

    zones = [
        {"label": "Stopped / Recovery", "min": 0, "max": 5},
        {"label": "Easy", "min": 5, "max": 12},
        {"label": "Endurance", "min": 12, "max": 16},
        {"label": "Tempo", "min": 16, "max": 18},
        {"label": "Fast", "min": 18, "max": None},
    ]

    profile = {
        zone["label"]: timedelta()
        for zone in zones
    }

    for current, next_record in zip(
        ride.records,
        ride.records[1:]
    ):

        speed = current.get("speed")

        if speed is None:
            continue

        # Convert m/s -> display speed
        speed = unit_converter.convert(
            speed,
            ride.units["speed"],
            config.FIT_FIELDS["speed"]["display_unit"]
        )

        dt = (
            next_record["time"]
            - current["time"]
        )

        for zone in zones:

            minimum = zone["min"]

            maximum = (
                float("inf")
                if zone["max"] is None
                else zone["max"]
            )

            if minimum <= speed < maximum:
                profile[zone["label"]] += dt
                break

    return profile

def print_speed_profile(profile):

    total = sum(
        profile.values(),
        timedelta()
    )

    print()
    print("Speed Profile")
    print("-" * 50)

    for label, duration in profile.items():

        percent = (
            duration / total
            if total.total_seconds()
            else 0
        )

        print(
            f"{label:<20}"
            f"{duration.total_seconds()/60:6.1f} min "
            f"{percent:6.1%}"
        )

    print("-" * 50)