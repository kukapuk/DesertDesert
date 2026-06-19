import pyglet
from core.event_bus import EventBus
from core.world import World
from systems.input_system import InputSystem
from systems.movement_system import MovementSystem
from systems.render_system import RenderSystem
from level_loader import LevelLoader

WINDOW_W = 1280
WINDOW_H = 720
TITLE = "DesertDesert"

class Game(pyglet.window.Window):
    def __init__(self):
        super().__init__(WINDOW_W, WINDOW_H, caption=TITLE)

        self.bus = EventBus()
        self.world = World()

        self.render_system = RenderSystem(self.world, self)

        self.loader = LevelLoader(self.world, self.bus)
        self.loader.load("levels/level_1.tmx")

        self.render_system.load_tilemap(self.loader.tilemap)

        spawn = self.loader.get_spawn()
        player = self.world.create_entity()
        self.world.add_component(player, "Position", {"x": spawn["x"], "y": spawn["y"]})
        self.world.add_component(player, "Velocity", {"x": 0.0, "y": 0.0})
        self.world.add_component(player, "Input", {})
        self.player_id = player

        self.keys = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.keys)

        self.input_system = InputSystem(self.world, self.bus, self.keys)
        self.movement_system = MovementSystem(self.world)

        self.bus.subscribe("level_loaded", self._on_level_loaded)

        pyglet.clock.schedule_interval(self.on_update, 1 / 60)

    def _on_level_loaded(self, data):
        self.render_system.load_tilemap(self.loader.tilemap)

    def on_update(self, dt):
        self.input_system.update(dt)
        self.movement_system.update(dt)

    def on_draw(self):
        self.clear()

        pos = self.world.get_component(self.player_id, "Position")
        cam_x = pos["x"] - WINDOW_W / 2
        cam_y = pos["y"] - WINDOW_H / 2

        self.render_system.draw(cam_x, cam_y)

        pyglet.shapes.Rectangle(
            WINDOW_W / 2 - 16, WINDOW_H / 2 - 16, 32, 32,
            color=(120, 200, 120)
        ).draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            self.close()

if __name__ == "__main__":
    game = Game()
    pyglet.app.run()
