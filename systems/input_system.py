import pyglet
import pyglet.window.key as key
from systems.combat_system import SWING_HIGH, SWING_LOW, THRUST

class InputSystem:
    def __init__(self, world, bus, key_handler):
        self.world       = world
        self.bus         = bus
        self.keys        = key_handler
        self.alt_held    = False
        self.pending_attacks = []

        self.bus.subscribe("mouse_click", self._on_mouse_click)

    def on_mouse_press(self, button, modifiers):
        alt = modifiers & pyglet.window.key.MOD_ALT
        hand = "left" if alt else "right"

        if button == pyglet.window.mouse.LEFT:
            self.pending_attacks.append((hand, SWING_HIGH))
        elif button == pyglet.window.mouse.RIGHT:
            self.pending_attacks.append((hand, SWING_LOW))
        elif button == pyglet.window.mouse.MIDDLE:
            self.pending_attacks.append((hand, THRUST))

    def _on_mouse_click(self, data):
        pass

    def update(self, dt):
        for eid in self.world.get_entities_with("Input", "Velocity"):
            vel = self.world.get_component(eid, "Velocity")

            import math
            speed = 200
            dx = 0
            dy = 0

            if self.keys[key.W]: dy =  1
            if self.keys[key.S]: dy = -1
            if self.keys[key.A]: dx = -1
            if self.keys[key.D]: dx =  1

            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                dx /= length
                dy /= length

            vel["x"] = dx * speed
            vel["y"] = dy * speed

            self.bus.publish("player_moving", {
                "eid": eid,
                "moving": length > 0,
                "vx": vel["x"],
                "vy": vel["y"],
            })

        for eid in self.world.get_entities_with("Input", "Combat"):
            for hand, attack_type in self.pending_attacks:
                self.bus.publish("player_attack", {
                    "eid": eid,
                    "hand": hand,
                    "attack": attack_type,
                })

        self.pending_attacks.clear()
