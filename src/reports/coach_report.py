import config
#from src.analysis import distribution


def print_coach_report(ride):
    label_width = 28

    # Coach Report (v2):
    #   +Moving Time (minutes)
    #   +Moving Time %
    #   +Distance
    #   +Moving Average Speed
    #   +Average Active Cadence
    #   +Average HR
    #   +Max HR

    #print("Running report")
    #distance_display = ride.display_value("distance", ride.distance_total.value)
    #speed_avg_display = ride.display_value("speed", ride.speed_avg.value)

    print()
    print("Coach Report v2.1")

    print(
        f"{'Moving Time':<{label_width}}"
        f"{ride.get("duration_moving",unit="min"):.1fu}"
    )

    print(
        f"{'Moving Percentage':<{label_width}}"
        f"{ride.get("duration_moving").value / ride.get("duration_elapsed").value:.1%}"
    )

    print(
        f"{'Distance':<{label_width}}"
        f"{ride.get("distance_total"):.2fu}"
    )

    print(
        f"{'Moving Average Speed':<{label_width}}"
        f"{ride.get("speed_avg"):.2fu}"
    )

    print(
        f"{'Avg Active Cadence':<{label_width}}"
        f"{ride.get("active_cadence_avg"):.1fu}"
    )

    print(
        f"{'Avg Heart Rate':<{label_width}}"
        f"{ride.get("heart_rate_avg"):.1fu}"
    )

    print(
        f"{'Max Heart Rate':<{label_width}}"
        f"{ride.get("heart_rate_max"):.0fu}"
    )

    print(
        f"{'Avg Temperature':<{label_width}}"
        f"{ride.get("temp_avg"):.1fu}"
    )