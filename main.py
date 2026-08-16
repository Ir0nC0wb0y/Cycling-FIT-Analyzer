import argparse
from src.fit_reader import load_fit
from src.fit_reader import get_available_fields
from src.ride import Ride
from pathlib import Path
from src.file_utils import find_input_file
import src.reports.distribution_report as distribution_report
import src.analysis.distribution as distribution
from src.analysis import speed_analysis
from src.reports.power_report import print_power_report
#from src.reports import speed_profile
#from src.analysis import effort_analysis
#import src.performance_logger as performance_logger

from src.environment.wind import create_wind
from src.analysis.wind_power import wind_power_sweep

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

    #fields = get_available_fields(filename, display=True)

    records, field_units = load_fit(filename)

    print()
    print("FIT Record ouptut: ")
    print(records[50].keys())
    print()

    # Create a ride & validate
    ride = Ride(records, field_units)
    ride.validate()
    #print(ride.units)
    #print(ride.list_parameters())

    print()
    print("Direction samples")
    print("-----------------")

    for i in range(0, len(ride.records), 500):
        record = ride.records[i]

        print(
            f"{i:5d}  "
            f"lat={record.get('latitude')}  "
            f"lon={record.get('longitude')}  "
            f"direction={record.get('direction')}"
        )

    #ride.get("distance")
    #print(ride.get("temp_avg"))


    # Run reports
    coach_report.print_coach_report(ride)

    distribution_report.print_distribution_hr(ride)
    distribution_report.print_distribution_cadence(ride)
    #distribution_report.print_distribution_speed(ride)
    #distribution_report.print_distribution_power(ride)

    #profile = speed_profile.build_speed_profile(ride)
    #speed_profile.print_speed_profile(profile)

    speed_bins = distribution.generate_bins(ride, "speed", width=2)
    speed_profile = speed_analysis.build_speed_profile(ride, speed_bins)
    speed_analysis.print_speed_profile(speed_profile, speed_bins)

    #effort_profile = effort_analysis.build_effort_profile(ride)
    #effort_analysis.print_effort_profile(effort_profile)

    print_power_report(ride)

    results = wind_power_sweep(
        ride,
        wind_speeds=[0, 5, 10],
        wind_directions=[0, 90, 180, 270],
    )

    print()
    print("Wind Power Sweep")
    print("----------------")

    for result in results:

        print(
            f"Wind: {result['wind']:<8} "
            f"Aero: {result['aero_power']:6.1f} W"
        )

    ride.performance.report()

    print()
    print("Program End")


if __name__ == "__main__":
    main()


