from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.ride import Ride



@dataclass(frozen=True)
class SegmentRequest:
    axis: str          # "distance" or "time"
    interval: float    # numeric interval
    unit: str          # "mi", "km", "min", etc.
    relative: bool     # True for 25%, False for 5 mi

@dataclass(frozen=True)
class Segment:
    start: int
    end: int
    label: str

def segment_ride(ride, request):

    if request.axis == "distance":
        return segment_distance(ride, request)

    if request.axis == "time":
        return segment_time(ride, request)

    raise ValueError(
        f"Unknown segmentation axis: {request.axis}"
    )

def segment_distance(ride, interval):

def segment_time(ride, interval):