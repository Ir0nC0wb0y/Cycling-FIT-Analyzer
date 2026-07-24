from pathlib import Path
from datetime import timedelta

MISSING_DATA_VALUE = -1

FIT_USE_FIELDS = [
    "timestamp",
    "distance",
    "enhanced_speed",
    "heart_rate",
    "cadence",
    "enhanced_altitude",
    "temperature"
]

FIT_DEFAULT_DIRS = [
    "~/downloads/",
    "~/storage/downloads/",
    "data",
]

DISPLAY_FIELDS = [
    "timestamp",
    "distance",
    "heart_rate",
    "cadence",
]

UNITS = {
    "unit_distance": "mile",
    "unit_speed":    "mph",
    "unit_temperature": "F",
    "unit_altitude": "feet"
}

#HR_ZONES = {
#    "z1" = 130,
#    "z2" = 145,
#     "z3" = 160,
#     "z4" = 170,
#     "z5" = 220
# }

THRESHOLD_MOVING_SPEED = 0.5
THRESHOLD_INACTIVE_CADENCE = 50

TIME_VALIDATION = timedelta(seconds=5)
AUTO_PAUSE_GAP_SECONDS = timedelta(seconds=2)

HR_BINS = [
    {"label": "Below Z1", "min": None, "max": 95},
    {"label": "Z1",       "min":96,    "max":130},
    {"label": "Z2 low",   "min":131,   "max":137},
    {"label": "Z2 focus", "min":138,   "max":143},
    {"label": "Z2 high",  "min":144,   "max":145},
    {"label": "Z3 low",   "min":146,   "max":150},
    {"label": "Z3 mid",   "min":151,   "max":155},
    {"label": "Z3 high",  "min":156,   "max":160},
    {"label": "Z4",       "min":161,   "max":170},
    {"label": "Z5",       "min":171,   "max":193},
    {"label": "Z5+",      "min":194,   "max":None},
]

CADENCE_BINS = [
    {"label": "Below 70",  "min": None, "max": 70},
    {"label": " Low 70s",   "min":71,    "max":75},
    {"label": "High 70s",   "min":76,    "max":79},
    {"label": " Low 80s",   "min":80,    "max":83},
    {"label": " Mid 80s",   "min":84,    "max":86},
    {"label": "High 80s",   "min":87,    "max":89},
    {"label": " Low 90s",   "min":90,    "max":93},
    {"label": " Mid 90s",   "min":94,    "max":96},
    {"label": "High 90s",   "min":97,    "max":99},
    {"label": "    110s",   "min":100,   "max":109},
    {"label": "Over 100s",  "min":110,   "max":None},
]

REPORT_BAR_WIDTH = 20
REPORT_BAR_CHARACTER = "#"