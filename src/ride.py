import config
from datetime import timedelta
from functools import cached_property
import statistics
from src import units as unit_converter
from src.performance_logger import PerformanceLogger
from src.quantity import Quantity
import src.power_calc as power_calc

class Ride:

    def __init__(self, records, field_units):
        self.records = records
        self.units = field_units
        self.performance = PerformanceLogger()
        self.calculate_grade()
        self.calculate_acceleration()
        self.calculate_power()
        

    def get_unit(self, field):
        return self.field_units.get(field)

    def get_display_unit(self, field):
        definition = config.FIT_FIELDS.get(field)

        if definition is None:
            return None

        return definition["display_unit"]

    def display_value(self, field, value):
        definition = config.FIT_FIELDS[field]
        return unit_converter.convert(value, self.units[field.lower()], definition["display_unit"])

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
        total_time = self.duration_elapsed.value
        moving_time = self.duration_moving.value
        stopped_time = self.duration_stopped.value
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
        print(f"Heart Rate Coverage: {hr_coverage.value:.1%} of moving time")
        
        # Test Cadence Coverage
        cad_coverage = self.cadence_coverage
        print(f"Cadence Coverage: {cad_coverage.value:.1%} of moving time")

        
    ## Time Metrics ##
    @cached_property
    def start_time(self):
        for record in self.records:
            if self.is_moving:
                return Quantity(
                    value=record["time"],
                    unit="timestamp",
                )
        return None
    
    @cached_property
    def end_time(self):
        for record in reversed(self.records):
            if self.is_moving:
                return Quantity(
                    value=record["time"],
                    unit="timestamp",
                )
        return None
    
    @cached_property
    def duration_elapsed(self):
        return Quantity(
            value=self.end_time.value - self.start_time.value,
            unit="duration",
        )
    
    @cached_property
    def duration_moving(self):
        total_time = timedelta(0)

        for current, next_record in zip(self.records, self.records[1:]):
            if self.is_moving(current):
                time_delta = next_record["time"] - current["time"]
                total_time += time_delta
        return Quantity(
            value=total_time,
            unit="duration",
        )
    
    @cached_property
    def duration_stopped(self):
        total_time = timedelta(0)
        start = self.start_time.value
        end = self.end_time.value

        for current, next_record in zip(self.records, self.records[1:]):
            # Ignore anything before start or after end
            if current["time"] < start:
                continue

            if current["time"] >= end:
                continue

            if not self.is_moving(current):
                time_delta = next_record["time"] - current["time"]
                total_time += time_delta
        return Quantity(
            value=total_time,
            unit="duration",
        )

    ## Distance Metrics ##
    @cached_property
    def distance_total(self):
        for record in reversed(self.records):
            if self.is_moving(record):
                return Quantity(
                    value=record["distance"],
                    unit=self.units["distance"],
                )
            

    @cached_property
    def speed_avg(self):
        #return self.distance / self.duration_moving.total_seconds()
        return Quantity(
            value=(self.distance_total.value / self.duration_moving.value.total_seconds()),
            unit=f"{self.units["distance"]}/s",
            )
    
    ## Cadence Metrics ##
    @cached_property
    def _active_cadence_values(self):
        return [
            record.get("cadence", -1)
            for record in self.moving_records()
            if record.get("cadence", -1) > config.THRESHOLD_INACTIVE_CADENCE
        ]
    
    @cached_property
    def active_cadence_avg(self):
        # Collects all cadences greater than zero
        values = self._active_cadence_values

        if not values:
            return 0

        return Quantity(
            value=sum(values) / len(values),
            unit=self.units["cadence"],
        )

    @cached_property
    def active_cadence_std(self):
        """
        Standard deviation of active cadence.
        """

        values = self._active_cadence_values

        if len(values) < 2:
            return 0.0

        return Quantity(
            value=statistics.stdev(values),
            unit=self.units["cadence"],
        )
    
    
    ## Heart Rate Metrics ##
    @cached_property
    def heart_rate_max(self):
        max_hr = max(
                (
                    record.get("heart_rate", config.MISSING_DATA_VALUE)
                    for record in self.records
                ),
                default=None,
            )
        return Quantity(
            value=max_hr,
            unit=self.units["heart_rate"],
        )
    
    @cached_property
    def heart_rate_avg(self):
        heart_rates = [
            record["heart_rate"]
            for record in self.records
            if record.get("heart_rate", config.MISSING_DATA_VALUE) > 0
        ]
        return Quantity(
            value=sum(heart_rates) / len(heart_rates),
            unit=self.units["heart_rate"],
        )

    @cached_property
    def temp_avg(self):
        temps = [
            record["temperature"]
            for record in self.records
            if record.get("temperature", config.MISSING_DATA_VALUE) > 0
        ]
        return Quantity(
            value=sum(temps) / len(temps),
            unit=self.units["temperature"],
        )

    @property
    def power_avg(self):
        """
        Calculate time-weighted average estimated power
        over moving time.
        """

        power = self.get("estimated_power", "W").value

        power_time = 0.0
        total_time = 0.0

        for current, next_record, current_power in zip(
            self.records,
            self.records[1:],
            power,
        ):

            if current_power is None:
                continue

            dt = (
                next_record["time"]
                - current["time"]
            ).total_seconds()

            if dt <= 0:
                continue

            # Exclude stopped records from average power.
            speed = current.get("speed")

            if speed is None or speed <= 0:
                continue

            power_time += current_power * dt
            total_time += dt

        if total_time <= 0:
            return Quantity(
                value=None,
                unit="W",
            )

        return Quantity(
            value=power_time / total_time,
            unit="W",
        )

    ## Coverage Metrics ##
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
        return Quantity(
            value=len(valid) / len(moving),
            unit="ratio",
        )

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
        return Quantity(
            value=len(valid) / len(moving),
            unit="ratio",
        )

    def calculate_grade(self):
        """
        Calculate grade using a centered linear regression.

        Grade is estimated by fitting a straight line to the
        altitude profile over a window centered on the current
        record.
        """

        self.performance.tic("Grade")

        self.units["grade"] = "%"

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

    def calculate_acceleration(self):
        """
        Calculate acceleration using a centered linear regression.

        Acceleration is estimated by fitting a straight line to
        the speed profile over a time window centered on the
        current record.

        Acceleration = change in speed / change in time
        """

        self.performance.tic("Acceleration")

        self.units["acceleration"] = "m/s^2"

        half_window = config.ACCELERATION_WINDOW / 2

        # Sliding window implementation.
        #
        # 'left' and 'right' only move forward through the ride.
        # This avoids searching the entire record list for every
        # center point, reducing complexity from O(n²) to O(n).

        left = 0
        right = 0

        for center in range(len(self.records)):

            current = self.records[center]

            center_time = current.get("time")

            if center_time is None:
                current["acceleration"] = None
                continue

            start_time = (
                center_time
                - timedelta(seconds=half_window)
            )

            end_time = (
                center_time
                + timedelta(seconds=half_window)
            )

            #
            # Advance the left edge of the window
            #
            while (
                left < center
                and self.records[left]["time"] < start_time
            ):
                left += 1

            #
            # Advance the right edge of the window
            #
            while (
                right + 1 < len(self.records)
                and self.records[right + 1]["time"] <= end_time
            ):
                right += 1

            #
            # Build regression arrays
            #
            x = []
            y = []

            for i in range(left, right + 1):

                record = self.records[i]

                speed = record.get("speed")
                time = record.get("time")

                if (
                    speed is None
                    or time is None
                ):
                    continue

                x.append(
                    (time - center_time).total_seconds()
                )

                y.append(speed)

            # Need at least 3 points to perform a regression
            if len(x) < 3:
                current["acceleration"] = None
                continue

            x_mean = sum(x) / len(x)
            y_mean = sum(y) / len(y)

            numerator = 0.0
            denominator = 0.0

            for xi, yi in zip(x, y):

                dx = xi - x_mean

                numerator += (
                    dx * (yi - y_mean)
                )

                denominator += (
                    dx * dx
                )

            if denominator == 0:
                current["acceleration"] = None
                continue

            # Slope = change in speed / change in time
            current["acceleration"] = (
                numerator / denominator
            )

        self.performance.toc("Acceleration")

    def calculate_power(self):
        """
        Calculate estimated power for each record.
        """

        self.performance.tic("Power")

        rider_mass = unit_converter.convert(
            config.RIDER_MASS.value,
            config.RIDER_MASS.unit,
            "kg",
        )

        bike_mass = unit_converter.convert(
            config.BIKE_MASS.value,
            config.BIKE_MASS.unit,
            "kg",
        )

        mass = rider_mass + bike_mass

        speeds = self.get("speed", "m/s").value
        grades = self.get("grade", "%").value
        accelerations = self.get("acceleration", "m/s^2").value
        temperatures = self.get("temperature", "C").value
        altitudes = self.get("altitude", "m").value

        for current, speed, grade, acceleration, temperature, altitude in zip(
            self.records,
            speeds,
            grades,
            accelerations,
            temperatures,
            altitudes,
        ):

            if (
                speed is None
                or grade is None
                or acceleration is None
                or temperature is None
                or altitude is None
            ):
                current["estimated_power"] = None
                continue

            # Convert grade from percent to decimal.
            grade /= 100

            result = power_calc.calculate_power(
                mass=mass,
                speed=speed,
                grade=grade,
                acceleration=acceleration,
                temperature=temperature,
                altitude=altitude,
                surface_type=config.SURFACE_TYPE,
                tire_type=config.TIRE_TYPE,
                aero_position=config.AERO_POSITION,
            )

            current.update(result)

        self.units["air_density"] = "kg/m^3"
        self.units["power_gravity"] = "W"
        self.units["power_rolling"] = "W"
        self.units["power_aero"] = "W"
        self.units["power_acceleration"] = "W"
        self.units["estimated_power"] = "W"

        self.performance.toc("Power")


    def get(self, field, unit=None, record=None):
        """
        Get ride data. Searches:
            1. Records
            2. Cached Properties
            3. Returns None if unavailable
        """

        value = None

        # 1. record field
        if field in self.records[0]:
            #value = [record.get(field) for record in self.records]
            value = self.get_record_value(field, unit)

        #2 ride property
        elif hasattr(type(self), field):
            #value = getattr(self, field)
            value = self.get_property_value(field,unit)

        else:
            raise KeyError(f"Unknown field '{field}'")


        return value

    def get_record_value(self, field, unit_to=None):
        """
        Collects records with field name in converted units
        """

        #value = self.records.get(field)
        value = [record.get(field) for record in self.records]

        if field not in self.units:
            return None
        else:
            unit_from = self.units[field]

        if value is None:
            return None


        if unit_to is None:
            unit_to = config.FIT_FIELDS[field]["display_unit"]

        value_converted = unit_converter.convert(
                        value,
                        unit_from,
                        unit_to,
                    )

        return Quantity(
            value=value_converted,
            unit=unit_to,
        )
    

    def get_property_value(self, field, unit_to=None):
        """
        Collects property values with field name in converted units
        """
        value = getattr(self, field, None)

        if isinstance(value, Quantity):
            # if the property is a Parameter class
            # collect units
            if unit_to == None:
                #unit_to = config.RIDE_PROPERTIES[field]["display_unit"] # this won't work, as the FIT_FIELDS doesn't list every property name
                unit_to = value.unit
            unit_from = value.unit
            # convert
            value_converted = unit_converter.convert(
                                    value.value,
                                    unit_from,
                                    unit_to,
                                )

            return Quantity(
                value=value_converted,
                unit = unit_to,
            )
        else:
            #return None
            raise KeyError(f"Property ({field}) does not return type Quantity")

    def list_parameters(self):
        from functools import cached_property

        return [
            name
            for name, value in self.__class__.__dict__.items()
            if isinstance(value, cached_property)
        ]