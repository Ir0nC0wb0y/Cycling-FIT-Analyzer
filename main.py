import argparse
from src.fit_reader import load_fit
from src.fit_reader import get_available_fields
from src.ride import Ride
from pathlib import Path
from src.file_utils import find_input_file
import src.reports.distribution_report as distribution_report
import src.analysis.distribution as distribution
from src.analysis import speed_analysis
#from src.reports import speed_profile
from src.analysis import effort_analysis
import src.performance_logger as performance_logger

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
    #distribution_report.print_distribution_speed(ride)

    #profile = speed_profile.build_speed_profile(ride)
    #speed_profile.print_speed_profile(profile)

    speed_bins = distribution.generate_bins(ride, "speed", width=2)
    speed_profile = speed_analysis.build_speed_profile(ride, speed_bins)
    speed_analysis.print_speed_profile(speed_profile, speed_bins)

    #effort_profile = effort_analysis.build_effort_profile(ride)
    #effort_analysis.print_effort_profile(effort_profile)

    ride.performance.report()

    print()
    print("Program End")


if __name__ == "__main__":
    main()
