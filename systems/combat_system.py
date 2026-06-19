import math

SWING_HIGH = "swing_high"
SWING_LOW  = "swing_low"
THRUST     = "thrust"

IDLE     = "idle"
WINDUP   = "windup"
ACTIVE   = "active"
RECOVERY = "recovery"
DELAY    = "delay"

WINDUP_TIME   = 0.15
ACTIVE_TIME   = 0.08
RECOVERY_TIME = 0.20
DELAY_TIME    = 0.30

class ArmState:
    def __init__(self):
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
        self.timer      = WINDUP_TIME
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

        for arm_a in (combat_a["right"], combat_a["left"]):
            for arm_b in (combat_b["right"], combat_b["left"]):
                if arm_a.is_active() and not arm_a.hit_landed:
                    resolve_hit(arm_a, arm_b)
                    if not arm_a.blocked:
                        self._apply_damage(eid_b, arm_a)
                        arm_a.hit_landed = True

                if arm_b.is_active() and not arm_b.hit_landed:
                    resolve_hit(arm_b, arm_a)
                    if not arm_b.blocked:
                        self._apply_damage(eid_a, arm_b)
                        arm_b.hit_landed = True

    def _apply_damage(self, target_eid, arm):
        health = self.world.get_component(target_eid, "Health")
        if health is None:
            return

        dmg = 10
        self.bus.publish("entity_hit", {
            "eid":    target_eid,
            "damage": dmg,
            "attack": arm.attack,
        })

        health["hp"] -= dmg
        if health["hp"] <= 0:
            self.bus.publish("entity_died", {"eid": target_eid})

    def attack(self, eid, hand, attack_type):
        combat = self.world.get_component(eid, "Combat")
        if combat is None:
            return
        combat[hand].try_attack(attack_type)
