import config
from datetime import timedelta


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

    ## Time Metrics ##
    @property
    def start_time(self):
        for record in self.records:
            if self.is_moving:
                return record["timestamp"]
            
        return None
    
    @property
    def end_time(self):
        for record in reversed(self.records):
            if self.is_moving:
                return record["timestamp"]
            
        return None
    
    @property
    def duration_elapsed(self):
        return self.end_time - self.start_time
    
    @property
    def duration_moving(self):
        total_time = timedelta(0)

        for current, next_record in zip(self.records, self.records[1:]):
            if self.is_moving(current):
                time_delta = next_record["timestamp"] - current["timestamp"]
                total_time += time_delta
        return total_time
    
    @property
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
    @property
    def distance(self):
        for record in reversed(self.records):
            if self.is_moving(record):
                return record["distance"]
    
    ## Cadence Metrics ##
    @property
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
    @property
    def heart_rate_max(self):
        return max(
            record["heart_rate"]
            for record in self.moving_records()
            )
    
    @property
    def heart_rate_avg(self):
        heart_rates = [
            record["heart_rate"]
            for record in self.records
            if record["heart_rate"] > 0
        ]
        return sum(heart_rates) / len(heart_rates)