from enum import Enum

class SurfaceType(Enum):
    CONCRETE = "Concrete"
    ASPHALT = "Asphalt"
    GRAVEL = "Gravel"
    GRASS = "Grass"
    OFF_ROAD = "Off-Road"
    SAND = "Sand"


class TireType(Enum):
    SLICK = "Slick"
    KNOBBY = "Knobby"


class AeroPosition(Enum):
    TOPS = "Tops"
    HOODS = "Hoods"
    DROPS = "Drops"
    AEROBARS = "Aerobars"


class DrivetrainLosses(Enum):
    NEW = "New"
    OLD = "Old"
    WORN = "Worn"