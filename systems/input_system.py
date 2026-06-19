import pyglet.window.key as key
import math

class InputSystem:
    def __init__(self, world, bus, key_handler):
        self.world = world
        self.bus = bus
        self.keys = key_handler

    def update(self, dt):
        for eid in self.world.get_entities_with("Input", "Velocity"):
            vel = self.world.get_component(eid, "Velocity")

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
