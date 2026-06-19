import pyglet
import math

class AttackVFX:
    def __init__(self):
        self.effects = []

    def spawn_swing(self, x, y, angle, radius, arc_angle, attack_type, color=(255, 220, 100)):
        # swing_high: сверху вниз (от +half до -half)
        # swing_low:  снизу вверх (от -half до +half)
        from systems.combat_system import SWING_HIGH
        half      = arc_angle / 2
        start_deg = angle + half if attack_type == SWING_HIGH else angle - half
        end_deg   = angle - half if attack_type == SWING_HIGH else angle + half

        self.effects.append({
            "type":      "swing",
            "x":         x,
            "y":         y,
            "start_deg": start_deg,
            "end_deg":   end_deg,
            "radius":    radius,
            "color":     color,
            "progress":  0.0,
            "alpha":     220,
            "timer":     0.08,
            "max_timer": 0.08,
        })

    def spawn_thrust(self, x, y, angle, radius, color=(255, 220, 100)):
        self.effects.append({
            "type":      "thrust",
            "x":         x,
            "y":         y,
            "angle":     angle,
            "radius":    0.0,
            "max_radius": radius,
            "color":     color,
            "alpha":     220,
            "timer":     0.08,
            "max_timer": 0.08,
        })

    def update(self, dt):
        for e in self.effects:
            e["timer"] -= dt
            t = max(0.0, e["timer"] / e["max_timer"])
            e["alpha"] = int(220 * t)

            progress = 1.0 - t
            if e["type"] == "swing":
                e["progress"] = progress
            elif e["type"] == "thrust":
                e["radius"] = e["max_radius"] * progress

        self.effects = [e for e in self.effects if e["timer"] > 0]

    def draw(self):
        for e in self.effects:
            if e["type"] == "swing":
                self._draw_swing(e)
            elif e["type"] == "thrust":
                self._draw_thrust(e)

    def _draw_swing(self, e):
        x         = e["x"]
        y         = e["y"]
        start_deg = e["start_deg"]
        end_deg   = e["end_deg"]
        progress  = e["progress"]
        radius    = e["radius"]
        alpha     = e["alpha"]
        r, g, b   = e["color"]

        current_end = start_deg + (end_deg - start_deg) * progress

        steps   = 20
        start_a = math.radians(start_deg)
        end_a   = math.radians(current_end)

        if abs(end_a - start_a) < 0.01:
            return

        for i in range(steps):
            t0 = i / steps
            t1 = (i + 1) / steps
            a0 = start_a + (end_a - start_a) * t0
            a1 = start_a + (end_a - start_a) * t1

            x0 = x + math.cos(a0) * radius * 0.4
            y0 = y + math.sin(a0) * radius * 0.4
            x1 = x + math.cos(a0) * radius
            y1 = y + math.sin(a0) * radius
            x2 = x + math.cos(a1) * radius
            y2 = y + math.sin(a1) * radius
            x3 = x + math.cos(a1) * radius * 0.4
            y3 = y + math.sin(a1) * radius * 0.4

            pyglet.shapes.Triangle(
                x0, y0, x1, y1, x2, y2,
                color=(r, g, b, alpha)
            ).draw()
            pyglet.shapes.Triangle(
                x0, y0, x2, y2, x3, y3,
                color=(r, g, b, alpha)
            ).draw()

    def _draw_thrust(self, e):
        x       = e["x"]
        y       = e["y"]
        angle   = math.radians(e["angle"])
        radius  = e["radius"]
        alpha   = e["alpha"]
        r, g, b = e["color"]
        half    = math.radians(20)

        if radius < 1:
            return

        tip_x = x + math.cos(angle) * radius
        tip_y = y + math.sin(angle) * radius
        l_x   = x + math.cos(angle - half) * radius * 0.3
        l_y   = y + math.sin(angle - half) * radius * 0.3
        r_x   = x + math.cos(angle + half) * radius * 0.3
        r_y   = y + math.sin(angle + half) * radius * 0.3

        pyglet.shapes.Triangle(
            tip_x, tip_y, l_x, l_y, r_x, r_y,
            color=(r, g, b, alpha)
        ).draw()
