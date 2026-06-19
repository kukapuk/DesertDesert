from dataclasses import dataclass

@dataclass
class WeaponData:
    name:          str
    swing_dmg:     float
    thrust_dmg:    float
    swing_radius:  float
    thrust_radius: float
    swing_angle:   float = 110.0
    thrust_angle:  float = 40.0
    windup_time:   float = 0.15
    pierce_mul:    float = 1.0
    flesh_mul:     float = 1.0

SWORD = WeaponData(
    name          = "sword",
    swing_dmg     = 15,
    thrust_dmg    = 15,
    swing_radius  = 65,
    thrust_radius = 80,
    swing_angle   = 110,
    thrust_angle  = 40,
    windup_time   = 0.15,
    pierce_mul    = 1.0,
    flesh_mul     = 1.0,
)

HATCHET = WeaponData(
    name          = "hatchet",
    swing_dmg     = 8,
    thrust_dmg    = 8,
    swing_radius  = 55,
    thrust_radius = 65,
    swing_angle   = 110,
    thrust_angle  = 40,
    windup_time   = 0.18,
    pierce_mul    = 2.5,
    flesh_mul     = 1.0,
)

DAGGER = WeaponData(
    name          = "dagger",
    swing_dmg     = 8,
    thrust_dmg    = 20,
    swing_radius  = 40,
    thrust_radius = 70,
    swing_angle   = 90,
    thrust_angle  = 35,
    windup_time   = 0.08,
    pierce_mul    = 1.0,
    flesh_mul     = 1.0,
)

AXE = WeaponData(
    name          = "axe",
    swing_dmg     = 25,
    thrust_dmg    = 8,
    swing_radius  = 70,
    thrust_radius = 55,
    swing_angle   = 110,
    thrust_angle  = 40,
    windup_time   = 0.22,
    pierce_mul    = 1.0,
    flesh_mul     = 2.0,
)
