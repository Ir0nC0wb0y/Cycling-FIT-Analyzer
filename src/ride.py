import config
from datetime import timedelta
from functools import cached_property
import statistics
from src import units as unit_converter
from src.performance_logger import PerformanceLogger

class Ride:

    def __init__(self, records, field_units):
        self.records = records
        self.units = field_units
        self.performance = PerformanceLogger()
        self.calculate_grade()
        

    def get_unit(self, field):
        return self.field_units.get(field)

    def get_display_unit(self, field):
        definition = config.FIT_FIELDS.get(field)

        if definition is None:
            return None

        return definition["display_unit"]

    #def display_value(self, field, value):
    #    definition = config.FIT_FIELDS[field]
    #
    #    return units.convert(value, self.units[field.lower()], definition["display_unit"])

    def is_moving(self, record):
        return record["speed"] > config.THRESHOLD_MOVING_SPEED
    
    def moving_records(self):
        return [
            record for record in self.records
            if self.is_moving(record)
        ]

    def get_auto_pauses(self):
        pauses = []
        for previous, current in zip(self.records, self.records[1:]):
            gap = current["time"] - previous["time"]
            if gap > config.AUTO_PAUSE_GAP_SECONDS:
                pauses.append({"start":previous["time"],
                               "resume":current["time"],
                               "duration":gap,
                               "distance":previous.get("distance",0),
                              })
        return pauses

    def validate(self):
        # Test Time
        total_time = self.duration_elapsed
        moving_time = self.duration_moving
        stopped_time = self.duration_stopped
        missing_time = total_time - moving_time - stopped_time
        if abs(missing_time) > config.TIME_VALIDATION:
            print("Duration issues exist, missing: {missing_time.total_seconds():.3f} seconds")
        
        # Auto Pause Info
        pauses = self.get_auto_pauses()
        if pauses:
            total_pause_time = sum(
                (pause["duration"] for pause in pauses),
                timedelta()
            )

            longest_pause = max(
                pause["duration"]
                for pause in pauses
            )
            print(f"Ride had {len(pauses)} auto pauses")
            print(f"Total pause time: {total_pause_time}")
            print(f"Longest pause time: {longest_pause}")
        else:
            print("No auto pauses detected")
            
        
        
        # Test HR Coverage
        hr_coverage = self.heart_rate_coverage
        print(f"Heart Rate Coverage: {hr_coverage:.1%} of moving time")
        
        # Test Cadence Coverage
        cad_coverage = self.cadence_coverage
        print(f"Cadence Coverage: {cad_coverage:.1%} of moving time")

        
    ## Time Metrics ##
    @cached_property
    def start_time(self):
        for record in self.records:
            if self.is_moving:
                return record["time"]
            
        return None
    
    @cached_property
    def end_time(self):
        for record in reversed(self.records):
            if self.is_moving:
                return record["time"]
            
        return None
    
    @cached_property
    def duration_elapsed(self):
        return self.end_time - self.start_time
    
    @cached_property
    def duration_moving(self):
        total_time = timedelta(0)

        for current, next_record in zip(self.records, self.records[1:]):
            if self.is_moving(current):
                time_delta = next_record["time"] - current["time"]
                total_time += time_delta
        return total_time
    
    @cached_property
    def duration_stopped(self):
        total_time = timedelta(0)
        start = self.start_time
        end = self.end_time

        for current, next_record in zip(self.records, self.records[1:]):
            # Ignore anything before start or after end
            if current["time"] < start:
                continue

            if current["time"] >= end:
                continue

            if not self.is_moving(current):
                time_delta = next_record["time"] - current["time"]
                total_time += time_delta
        return total_time

    ## Distance Metrics ##
    @cached_property
    def distance(self):
        for record in reversed(self.records):
            if self.is_moving(record):
                return record["distance"]

    @cached_property
    def speed_avg(self):
        return (self.distance / self.duration_moving.total_seconds())
    
    ## Cadence Metrics ##
    @cached_property
    def active_cadence_values(self):
        return [
            record.get("cadence", -1)
            for record in self.moving_records()
            if record.get("cadence", -1) > config.THRESHOLD_INACTIVE_CADENCE
        ]
    
    @cached_property
    def active_cadence_avg(self):
        # Collects all cadences greater than zero
        values = self.active_cadence_values

        if not values:
            return 0

        return sum(values) / len(values)

    @cached_property
    def active_cadence_std(self):
        """
        Standard deviation of active cadence.
        """

        values = self.active_cadence_values

        if len(values) < 2:
            return 0.0

        return statistics.stdev(values)
    
    ## Heart Rate Metrics ##
    @cached_property
    def heart_rate_max(self):
        return max(
                (
                    record.get("heart_rate", config.MISSING_DATA_VALUE)
                    for record in self.records
                ),
                default=None,
            )
    
    @cached_property
    def heart_rate_avg(self):
        heart_rates = [
            record["heart_rate"]
            for record in self.records
            if record.get("heart_rate", config.MISSING_DATA_VALUE) > 0
        ]
        return sum(heart_rates) / len(heart_rates)

    @cached_property
    def heart_rate_coverage(self):
        moving = self.moving_records()
        if not moving:
            return 0.0

        valid = [
            record
            for record in moving
            if record.get("heart_rate", config.MISSING_DATA_VALUE) > 0
        ]
        return len(valid) / len(moving)

    @cached_property
    def cadence_coverage(self):
        moving = self.moving_records()
        if not moving:
            return 0.0

        valid = [
            record
            for record in moving
            if record.get("cadence", 0) > 0
        ]
        return len(valid) / len(moving)

    def calculate_grade(self):
        """
        Calculate grade using a centered linear regression.

        Grade is estimated by fitting a straight line to the
        altitude profile over a window centered on the current
        record.
        """

        self.performance.tic("Grade")

        half_window = config.GRADE_WINDOW_DISTANCE / 2

        # Sliding window implementation.
        #
        # 'left' and 'right' only move forward through the ride.
        # This avoids searching the entire record list for every
        # center point, reducing complexity from O(n²) to O(n).

        left = 0
        right = 0

        for center in range(len(self.records)):

            current = self.records[center]

            
            center_distance = current.get("distance")

            if center_distance is None:
                current["grade"] = None
                continue

            start_distance = center_distance - half_window
            end_distance = center_distance + half_window

            #
            # Advance the left edge of the window
            #
            while (
                left < center
                and self.records[left]["distance"] < start_distance
            ):
                left += 1

            #
            # Advance the right edge of the window
            #
            while (
                right + 1 < len(self.records)
                and self.records[right + 1]["distance"] <= end_distance
            ):
                right += 1

            #
            # Build regression arrays
            #
            x = []
            y = []

            for i in range(left, right + 1):

                record = self.records[i]

                altitude = record.get("altitude")

                if altitude is None:
                    continue

                x.append(record["distance"])
                y.append(altitude)

            # Need at least 3 points to perform a regression
            if len(x) < 3:
                current["grade"] = None
                continue

            x_mean = sum(x) / len(x)
            y_mean = sum(y) / len(y)

            numerator = 0.0
            denominator = 0.0

            for xi, yi in zip(x, y):

                dx = xi - x_mean

                numerator += dx * (yi - y_mean)
                denominator += dx * dx

            if denominator == 0:
                current["grade"] = None
                continue

            slope = numerator / denominator

            # Convert rise/run to percent grade
            current["grade"] = slope * 100

        self.performance.toc("Grade")

    def get(self, record, field, unit=None):
        value = record.get(field)

        if value is None:
            return None

        if field not in self.units:
            return value

        source = self.units[field]

        if unit is None:
            unit = config.FIT_FIELDS[field]["display_unit"]

        return unit_converter.convert(
            value,
            source,
            unit,
        )