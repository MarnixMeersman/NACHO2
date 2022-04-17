from dataclasses import dataclass
import datetime

@dataclass
class Position:
    date: datetime
    x: float
    y: float
    z: float

@dataclass
class Asteroid:
    name: str
    diameter: float
    H: float
    albedo: float
    date_closest: datetime
    distance_closest: float
    palermo_max: float
    palermo_cumulative: float
    ephemeris: ... # [Position]

