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

    distance_display = ride.display_value("distance", ride.distance)
    speed_avg_display = ride.display_value("speed", ride.speed_avg)

    print()
    print("Coach Report v2")

    print(
        f"{'Moving Time [minutes]':<{label_width}}"
        f"{ride.duration_moving.total_seconds() / 60:.1f}"
    )

    print(
        f"{'Moving Time %':<{label_width}}"
        f"{ride.duration_moving / ride.duration_elapsed:.1%}"
    )

    print(
        f"{f'Distance [{config.FIT_FIELDS['distance']['display_unit']}]':<{label_width}}"
        f"{distance_display:.2f}"
    )

    print(
        f"{f'Moving Average Speed [{config.FIT_FIELDS['speed']['display_unit']}]':<{label_width}}"
        f"{speed_avg_display:.2f}"
    )

    print(
        f"{'Avg Active Cadence':<{label_width}}"
        f"{ride.active_cadence_avg:.1f}"
    )

    print(
        f"{'Avg Heart Rate':<{label_width}}"
        f"{ride.heart_rate_avg:.1f}"
    )

    print(
        f"{'Max Heart Rate':<{label_width}}"
        f"{ride.heart_rate_max}"
    )