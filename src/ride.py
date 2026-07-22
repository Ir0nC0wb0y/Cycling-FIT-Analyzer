import config
from datetime import timedelta
from functools import cached_property

class Ride:

    def __init__(self, records):
        self.records = records

    def is_moving(self, record):
        return record["enhanced_speed"] > config.THRESHOLD_MOVING_SPEED
    
    def moving_records(self):
        return [
            record for record in self.records
            if self.is_moving(record)
        ]

    def validate(self):
        # Test Time
        total_time = self.duration_elapsed
        moving_time = self.duration_moving
        stopped_time = self.duration_stopped
        missing_time = total_time - moving_time - stopped_time
        if abs(missing_time) > config.TIME_VALIDATION:
            print("Duration issues exist, missing: {missing_time.total_seconds():.3f} seconds")
        
        # Auto Pause Count
        pauses = self.auto_pauses
        print("Ride had {len(pauses)} auto pauses")
        
        # Test HR Coverage
        hr_coverage = self.heart_rate_coverage
        print("Heart Rate Coverage: {hr_coverage:.1%}")
        
        # Test Cadence Coverage
        cad_coverage = self.cadence_coverage
        print("Cadence Coverage: {hr_coverage:.1%}")

        
    ## Time Metrics ##
    @cached_property
    def start_time(self):
        for record in self.records:
            if self.is_moving:
                return record["timestamp"]
            
        return None
    
    @cached_property
    def end_time(self):
        for record in reversed(self.records):
            if self.is_moving:
                return record["timestamp"]
            
        return None
    
    @cached_property
    def duration_elapsed(self):
        return self.end_time - self.start_time
    
    @cached_property
    def duration_moving(self):
        total_time = timedelta(0)

        for current, next_record in zip(self.records, self.records[1:]):
            if self.is_moving(current):
                time_delta = next_record["timestamp"] - current["timestamp"]
                total_time += time_delta
        return total_time
    
    @cached_property
    def duration_stopped(self):
        total_time = timedelta(0)
        start = self.start_time
        end = self.end_time

        for current, next_record in zip(self.records, self.records[1:]):
            # Ignore anything before start or after end
            if current["timestamp"] < start:
                continue

            if current["timestamp"] >= end:
                continue

            if not self.is_moving(current):
                time_delta = next_record["timestamp"] - current["timestamp"]
                total_time += time_delta
        return total_time

    ## Distance Metrics ##
    @cached_property
    def distance(self):
        for record in reversed(self.records):
            if self.is_moving(record):
                return record["distance"]
    
    ## Cadence Metrics ##
    @cached_property
    def active_cadence_avg(self):
        # Collects all cadences greater than zero
        cadences = [
            record.get("cadence", 0)
            for record in self.moving_records()
            if record.get("cadence", 0) > config.THRESHOLD_INACTIVE_CADENCE
        ]

        if not cadences:
            return 0

        return sum(cadences) / len(cadences)
    
    ## Heart Rate Metrics ##
    @cached_property
    def heart_rate_max(self):
        return max(
            record["heart_rate"]
            for record in self.moving_records()
            )
    
    @cached_property
    def heart_rate_avg(self):
        heart_rates = [
            record["heart_rate"]
            for record in self.records
            if record.get("heart_rate", 0) > 0
        ]
        return sum(heart_rates) / len(heart_rates)

    @cached_property
    def auto_pauses(self):
        pauses = []
        for previous, current in zip(self.records, self.records[1:]):
            gap = current["timestamp"] - previous["timestamp"]
            if gap > config.AUTO_PAUSE_GAP_SECONDS:
                pauses.append({"start":previous["timestamp"],
                               "resume":current["timestamp"],
                               "duration":gap,
                               "distance":previous.get("distance",0),
                              })
        return pauses

    @cached_property
    def heart_rate_coverage(self):
        moving = self.moving_records()
        if not moving:
            return 0.0

        valid = [
            record
            for record in moving
            if record.get("heart_rate", 0) > 0
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
