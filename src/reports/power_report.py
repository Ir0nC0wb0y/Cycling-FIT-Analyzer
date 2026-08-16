#import config

def print_power_report(ride):


    label_width = 34

    print()
    print("Power Report:")

    print(
        f"{'Average Gravity Power':<{label_width}}"
        f"{ride.get("power_gravity_avg"):.1fu}"
    )

    print(
        f"{'Average Rolling Power':<{label_width}}"
        f"{ride.get("power_rolling_avg"):.1fu}"
    )

    print(
        f"{'Average Aero Power':<{label_width}}"
        f"{ride.get("power_aero_avg"):.1fu}"
    )

    print(
        f"{'Average Gravity Power':<{label_width}}"
        f"{ride.get("power_gravity_avg"):.1fu}"
    )

    print(
        f"{'Average Acceleration Power':<{label_width}}"
        f"{ride.get("power_acceleration_avg"):.1fu}"
    )

    print(
        f"{'Average Estimated Power':<{label_width}}"
        f"{ride.get("power_avg"):.1fu}"
    )