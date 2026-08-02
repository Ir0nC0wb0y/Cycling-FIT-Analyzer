import config
import src.analysis.distribution as distribution


def print_distribution_hr(ride):
    """
    Build and print a time distribution historgram of heart rate
    """

    if ride.heart_rate_coverage.value > config.THRESHOLD_COVERAGE:
        # HR Bins in Config
        hr_bins = config.HR_BINS
        hr_distribution = distribution.build_distribution(ride,"heart_rate", hr_bins)
        distribution.print_distribution(hr_distribution, hr_bins, title="HR Distribution")


def print_distribution_cadence(ride):
    """
    Build and print a time distribution historgram of cadence
    """

    if ride.cadence_coverage.value > config.THRESHOLD_COVERAGE:
        # Cadence Bins centered around average, using std deviation
        cadence_bins = distribution.build_stddev_bins(ride.active_cadence_avg.value, ride.active_cadence_std.value, config.CADENCE_STDEV_BINS)
        cadence_distribution = distribution.build_distribution(ride, "cadence", cadence_bins)
        distribution.print_distribution(cadence_distribution, cadence_bins, title="Cadence Consistency")

def print_distribution_speed(ride):
    """
    Build and print a time distribution historgram of speed
    """

    speed_bins = distribution.generate_bins(ride, "speed", 1)
    speed_distribution = distribution.build_distribution(ride, "speed", speed_bins, moving_only=True)
    distribution.print_distribution(speed_distribution, speed_bins, "Speed Distribution", show_bounds=False)