
FIT_USE_FIELDS = [
    "timestamp",
    "distance",
    "enhanced_speed",
    "heart_rate",
    "cadence",
    "enhanced_altitude",
    "temperature"
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