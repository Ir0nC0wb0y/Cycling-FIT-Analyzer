# src/power_calc.py
#import math
from src.air_density import air_density

from src.power_enums import (
    SurfaceType,
    TireType,
    AeroPosition,
    DrivetrainLosses,
)


GRAVITY = 9.80665
#AIR_DENSITY = 1.225


ROLLING_RESISTANCE = {
    SurfaceType.CONCRETE: {
        TireType.SLICK: .0020,
        TireType.KNOBBY: .0025,
    },
    SurfaceType.ASPHALT: {
        TireType.SLICK: .0050,
        TireType.KNOBBY: .0063,
    },
    SurfaceType.GRAVEL: {
        TireType.SLICK: .0060,
        TireType.KNOBBY: .0076,
    },
    SurfaceType.GRASS: {
        TireType.SLICK: .0070,
        TireType.KNOBBY: .0089,
    },
    SurfaceType.OFF_ROAD: {
        TireType.SLICK: .0200,
        TireType.KNOBBY: .0253,
    },
    SurfaceType.SAND: {
        TireType.SLICK: .0300,
        TireType.KNOBBY: .0380,
    },
}


CD_A = {
    AeroPosition.TOPS: .408,
    AeroPosition.HOODS: .324,
    AeroPosition.DROPS: .307,
    AeroPosition.AEROBARS: .2914,
}

DRIVETRAIN_LOSS = {
    DrivetrainLosses.NEW: .03,
    DrivetrainLosses.OLD: .04,
    DrivetrainLosses.WORN: .05,
}


def get_crr(surface_type, tire_type):
    return ROLLING_RESISTANCE[surface_type][tire_type]


def get_cd_a(aero_position):
    return CD_A[aero_position]

def power_gravity(mass, speed, grade):
    return mass * GRAVITY * grade * speed

def power_rolling(mass, speed, crr):
    return mass * GRAVITY * crr * speed

def power_aero(air_speed, cd_a, density):
    return 0.5 * density * cd_a * air_speed ** 3

def power_accel(mass, speed, acceleration):
    return mass * acceleration * speed

def get_drivetrain_efficiency(condition):
    return DRIVETRAIN_LOSS[condition]

def calculate_power(
    mass,
    speed,
    grade,
    acceleration,
    temperature,
    altitude,
    surface_type,
    tire_type,
    aero_position,
):
    crr = get_crr(surface_type, tire_type)
    cd_a = get_cd_a(aero_position)

    density = air_density(temperature, altitude)

    gravity = power_gravity(mass, speed, grade)
    rolling = power_rolling(mass, speed, crr)
    aero = power_aero(speed, cd_a, density)
    accel = power_accel(mass, speed, acceleration)

    return {
        "air_density": density,
        "power_gravity": gravity,
        "power_rolling": rolling,
        "power_aero": aero,
        "power_acceleration": accel,
        "estimated_power": (
            gravity
            + rolling
            + aero
            + accel
        ),
    }