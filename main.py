import pyglet
from core.event_bus import EventBus
from core.world import World

WINDOW_W = 1280
WINDOW_H = 720
TITLE = "DesertDesert"

class Game(pyglet.window.Window):
    def __init__(self):
        super().__init__(WINDOW_W, WINDOW_H, caption=TITLE)
        
        self.bus = EventBus()
        self.world = World()

        player = self.world.create_entity()
        self.world.add_component(player, "Position", {"x": 640.0, "y": 360.0})
        self.world.add_component(player, "Velocity", {"x": 0.0, "y": 0.0})
        self.world.add_component(player, "Input", {})
        self.player_id = player

        self.keys = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.keys)

        pyglet.clock.schedule_interval(self.on_update, 1 / 60)

    def on_update(self, dt):
        pos = self.world.get_component(self.player_id, "Position")
        vel = self.world.get_component(self.player_id, "Velocity")

        speed = 200
        vel["x"] = 0
        vel["y"] = 0
        if self.keys[pyglet.window.key.W]: vel["y"] =  speed
        if self.keys[pyglet.window.key.S]: vel["y"] = -speed
        if self.keys[pyglet.window.key.A]: vel["x"] = -speed
        if self.keys[pyglet.window.key.D]: vel["x"] =  speed

        pos["x"] += vel["x"] * dt
        pos["y"] += vel["y"] * dt

    def on_draw(self):
        self.clear()
        pos = self.world.get_component(self.player_id, "Position")
        # временно рисуем квадрат вместо спрайта
        pyglet.shapes.Rectangle(
            pos["x"] - 16, pos["y"] - 16, 32, 32,
            color=(120, 200, 120)
        ).draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            self.close()

if __name__ == "__main__":
    game = Game()
    pyglet.app.run()
