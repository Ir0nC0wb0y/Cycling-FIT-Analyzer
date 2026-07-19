import argparse
from src.fit_reader import load_fit
from src.fit_reader import get_available_fields
from src.ride import Ride
from pathlib import Path
from src.file_utils import find_input_file

print("Running program")

def main():
    # Set up command line arguments
    parser = argparse.ArgumentParser(
        description="Analyze a FIT ride file."
    )

    parser.add_argument(
    "filename",
    nargs="?",
    default=None,
    help="Path to the FIT file"
)

    args = parser.parse_args()

    filename = find_input_file(args.filename)

    # print FIT file record headers and units
    fields = get_available_fields(filename)
    

    # Load the FIT file
    records = load_fit(filename)
    ride = Ride(records)

    # print()
    # print(f"Start: {ride.start_time}")
    # print(f"End: {ride.end_time}")
    # print(f"Duration: {ride.duration_elapsed}")
    # print(f"Moving Time [minutes]: {ride.duration_moving}")
    # print(f"Stopped Time: {ride.duration_stopped}")
    # print(f"Duration (calc): {ride.duration_moving + ride.duration_stopped}")

    distance_converted = ride.distance / 1609.34
    moving_time_hrs = ride.duration_moving.total_seconds() / 3600

    print()
    print("Coach Report v2")
    print(f"Moving Time [minutes]: {ride.duration_moving.total_seconds() / 60:.1f}")
    print(f"Moving Time %: {ride.duration_moving / ride.duration_elapsed:.1%}")
    print(f"Distance [miles]: {distance_converted:.2f}")
    print(f"Moving Average Speed: {distance_converted / moving_time_hrs:.2f}")
    print(f"Avg Active Cadence: {ride.active_cadence_avg:.1f}")
    print(f"Avg Heart Rate: {ride.heart_rate_avg:.1f}")
    print(f"Max Heart Rate: {ride.heart_rate_max}")

    # Coach Report (v2):
    #   +Moving Time (minutes)
    #   +Moving Time %
    #   +Distance
    #   +Moving Average Speed
    #   +Average Active Cadence
    #   +Average HR
    #   +Max HR

    print()
    print("Program End")


if __name__ == "__main__":
    main()
