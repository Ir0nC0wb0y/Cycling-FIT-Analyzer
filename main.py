import argparse
from src.fit_reader import load_fit
from src.fit_reader import get_available_fields
from src.ride import Ride
from pathlib import Path
from src.file_utils import find_input_file
import src.analysis.distribution as distribution
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

    # HR Bins in Config
    hr_bins = config.HR_BINS
    hr_distribution = distribution.build_distribution(ride.records,"heart_rate", hr_bins)
    distribution.print_distribution(hr_distribution, hr_bins, title="HR Distribution")

    # Cadence Bins centered around average, using std deviation
    cadence_bins = distribution.build_stddev_bins(ride.active_cadence_avg, ride.active_cadence_std, config.CADENCE_STDEV_BINS)
    cadence_distribution = distribution.build_distribution(ride.records, "cadence", cadence_bins)
    distribution.print_distribution(cadence_distribution, cadence_bins, title="Cadence Consistency")

    print()
    print("Program End")


if __name__ == "__main__":
    main()
