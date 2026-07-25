from pathlib import Path
from datetime import timedelta

MISSING_DATA_VALUE = -1

#FIT_USE_FIELDS = [
#    "timestamp",
#    "distance",
#    "enhanced_speed",
#    "heart_rate",
#    "cadence",
#    "enhanced_altitude",
#    "temperature"
#]

FIT_FIELDS = {
    "time": {
        "fit_field": "timestamp",
        "display_unit": None,
    },
    "distance": {
        "fit_field": "distance",
        "display_unit": "mi",
    },
    "speed": {
        "fit_field": "enhanced_speed",
        "display_unit": "mph",
    },
    "heart_rate": {
        "fit_field": "heart_rate",
        "display_unit": "bpm",
    },
    "cadence": {
        "fit_field": "cadence",
        "display_unit": "rpm",
    },
    "altitude": {
        "fit_field": "enhanced_altitude",
        "display_unit": "ft",
    },
    "temperature": {
        "fit_field": "temperature",
        "display_unit": "F",
    },
}

FIT_DEFAULT_DIRS = [
    "~/downloads/",
    "~/storage/downloads/",
    "data",
]

#DISPLAY_FIELDS = [
#    "timestamp",
#    "distance",
#    "heart_rate",
#    "cadence",
#]

#UNITS = {
#    "unit_distance": "mile",
#    "unit_speed":    "mph",
#    "unit_temperature": "F",
#    "unit_altitude": "feet"
#}

DISPLAY_UNITS = {
    "distance": "mi",
    "speed": "mph",
    "altitude": "ft",
    "temperature": "F",
    "cadence": "rpm",
    "heart_rate": "bpm",
}

#HR_ZONES = {
#    "z1" = 130,
#    "z2" = 145,
#    "z3" = 160,
#    "z4" = 170,
#    "z5" = 220
# }

THRESHOLD_MOVING_SPEED = 0.5
THRESHOLD_INACTIVE_CADENCE = 50
THRESHOLD_COVERAGE = .80

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

CADENCE_STDEV_BINS = [
    {"label": "Low Outlier",       "min": None,  "max": -2.0},
    {"label": "Moderately Low",    "min": -2.0,  "max": -1.0},
    {"label": "Slightly Low",      "min": -1.0,  "max": -0.5},
    {"label": "Core Low",          "min": -0.5, "max": 0},
    {"label": "Core High",         "min": 0,   "max": 0.5},
    {"label": "Slightly High",     "min": 0.5,  "max": 1.0},
    {"label": "Moderately High",   "min": 1.0,   "max": 2.0},
    {"label": "High Outlier",      "min": 2.0,   "max": None},
]

REPORT_BAR_WIDTH = 20
REPORT_BAR_CHARACTER = "#"
REPORT_SHOW_EMPTY_BINS = False
REPORT_MIN_BIN_PERCENT = .005