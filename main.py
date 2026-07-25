import argparse
from src.fit_reader import load_fit
from src.fit_reader import get_available_fields
from src.ride import Ride
from pathlib import Path
from src.file_utils import find_input_file
import src.reports.distribution_report as distribution_report

import config
from src import units
from src.reports import coach_report

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

    # Load the FIT file
    filename = find_input_file(args.filename)
    records, field_units = load_fit(filename)

    # Create a ride & validate
    ride = Ride(records, field_units)
    ride.validate()

    # Run reports
    coach_report.print_coach_report(ride)

    distribution_report.print_distribution_hr(ride)
    distribution_report.print_distribution_cadence(ride)
    distribution_report.print_distribution_speed(ride)

    print()
    print("Program End")


if __name__ == "__main__":
    main()
