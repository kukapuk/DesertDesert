import math
from systems.weapon import WeaponData, SWORD

SWING_HIGH = "swing_high"
SWING_LOW  = "swing_low"
THRUST     = "thrust"

IDLE     = "idle"
WINDUP   = "windup"
ACTIVE   = "active"
RECOVERY = "recovery"
DELAY    = "delay"

ACTIVE_TIME   = 0.08
RECOVERY_TIME = 0.20
DELAY_TIME    = 0.30

class ArmState:
    def __init__(self, weapon: WeaponData = None):
        self.weapon     = weapon or SWORD
        self.phase      = IDLE
        self.attack     = None
        self.timer      = 0.0
        self.blocked    = False
        self.hit_landed = False

    def update(self, dt):
        if self.phase == IDLE:
            return

        self.timer -= dt

        if self.timer <= 0:
            if self.phase == WINDUP:
                self.phase      = ACTIVE
                self.timer      = ACTIVE_TIME
                self.hit_landed = False

            elif self.phase == ACTIVE:
                self.phase  = RECOVERY
                self.timer  = RECOVERY_TIME
                self.attack = None

            elif self.phase == RECOVERY:
                if self.blocked:
                    self.phase   = DELAY
                    self.timer   = DELAY_TIME
                    self.blocked = False
                else:
                    self.phase = IDLE

            elif self.phase == DELAY:
                self.phase = IDLE

    def try_attack(self, attack_type):
        if self.phase != IDLE:
            return False
        self.phase      = WINDUP
        self.attack     = attack_type
        self.timer      = self.weapon.windup_time
        self.blocked    = False
        self.hit_landed = False
        return True

    def is_active(self):
        return self.phase == ACTIVE

    def block(self):
        if self.phase in (ACTIVE, RECOVERY):
            self.blocked = True


def resolve_hit(attacker_arm, defender_arm):
    a = attacker_arm.attack
    d = defender_arm.attack

    if not attacker_arm.is_active():
        return

    if defender_arm.is_active():
        if (a == SWING_HIGH and d == SWING_LOW) or \
           (a == SWING_LOW  and d == SWING_HIGH):
            attacker_arm.block()
            defender_arm.block()
            return

        if a == THRUST and d in (SWING_HIGH, SWING_LOW):
            attacker_arm.block()
            return

        if d == THRUST and a in (SWING_HIGH, SWING_LOW):
            defender_arm.block()


def in_attack_range(attacker_pos, attacker_angle, target_pos, arm, target_hw=16, target_hh=16):
    if arm.attack == THRUST:
        radius = arm.weapon.thrust_radius
        angle  = arm.weapon.thrust_angle
    else:
        radius = arm.weapon.swing_radius
        angle  = arm.weapon.swing_angle

    nearest_x = max(target_pos["x"] - target_hw, min(attacker_pos["x"], target_pos["x"] + target_hw))
    nearest_y = max(target_pos["y"] - target_hh, min(attacker_pos["y"], target_pos["y"] + target_hh))

    dx = nearest_x - attacker_pos["x"]
    dy = nearest_y - attacker_pos["y"]
    dist = math.sqrt(dx * dx + dy * dy)

    if dist > radius:
        return False

    angle_to_target = math.degrees(math.atan2(dy, dx))
    diff = (angle_to_target - attacker_angle + 180) % 360 - 180

    return abs(diff) <= angle / 2


def calc_damage(arm, target_armor):
    w = arm.weapon

    if arm.attack == THRUST:
        base = w.thrust_dmg
    else:
        base = w.swing_dmg

    armor = target_armor or {"value": 0, "type": "none"}

    if armor["type"] == "plate":
        dmg = base * w.pierce_mul - armor["value"]
    else:
        dmg = base * w.flesh_mul - armor["value"] * 0.5

    return max(1, dmg)


class CombatSystem:
    def __init__(self, world, bus):
        self.world = world
        self.bus   = bus

    def update(self, dt):
        for eid in self.world.get_entities_with("Combat"):
            combat = self.world.get_component(eid, "Combat")
            combat["right"].update(dt)
            combat["left"].update(dt)

        attackers = self.world.get_entities_with("Combat", "Position")
        for i, eid_a in enumerate(attackers):
            for eid_b in attackers[i+1:]:
                self._check_hit(eid_a, eid_b)

    def _check_hit(self, eid_a, eid_b):
        combat_a = self.world.get_component(eid_a, "Combat")
        combat_b = self.world.get_component(eid_b, "Combat")
        pos_a    = self.world.get_component(eid_a, "Position")
        pos_b    = self.world.get_component(eid_b, "Position")
        rot_a    = self.world.get_component(eid_a, "Rotation")
        rot_b    = self.world.get_component(eid_b, "Rotation")

        angle_a = rot_a["angle"] if rot_a else 0.0
        angle_b = rot_b["angle"] if rot_b else 0.0

        for arm_a in (combat_a["right"], combat_a["left"]):
            if arm_a.is_active() and not arm_a.hit_landed and arm_a.attack:
                if in_attack_range(pos_a, -angle_a, pos_b, arm_a):
                    resolve_hit(arm_a, combat_b["right"])
                    resolve_hit(arm_a, combat_b["left"])
                    if not arm_a.blocked:
                        armor = self.world.get_component(eid_b, "Armor")
                        dmg   = calc_damage(arm_a, armor)
                        self._apply_damage(eid_b, arm_a, dmg)
                        arm_a.hit_landed = True

        for arm_b in (combat_b["right"], combat_b["left"]):
            if arm_b.is_active() and not arm_b.hit_landed and arm_b.attack:
                if in_attack_range(pos_b, -angle_b, pos_a, arm_b):
                    resolve_hit(arm_b, combat_a["right"])
                    resolve_hit(arm_b, combat_a["left"])
                    if not arm_b.blocked:
                        armor = self.world.get_component(eid_a, "Armor")
                        dmg   = calc_damage(arm_b, armor)
                        self._apply_damage(eid_a, arm_b, dmg)
                        arm_b.hit_landed = True

    def _apply_damage(self, target_eid, arm, dmg):
        health = self.world.get_component(target_eid, "Health")
        if health is None:
            return

        self.bus.publish("entity_hit", {
            "eid":    target_eid,
            "damage": dmg,
            "attack": arm.attack,
            "weapon": arm.weapon.name,
        })

        health["hp"] -= dmg
        if health["hp"] <= 0:
            self.bus.publish("entity_died", {"eid": target_eid})

    def attack(self, eid, hand, attack_type):
        combat = self.world.get_component(eid, "Combat")
        if combat is None:
            return
        combat[hand].try_attack(attack_type)
