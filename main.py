import pyglet
import math
from core.event_bus import EventBus
from core.world import World
from systems.input_system import InputSystem
from systems.collision_system import CollisionSystem
from systems.render_system import RenderSystem
from systems.sprite_stack import SpriteStack
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
        self.world.add_component(player, "Rotation", {"angle": 0.0})
        self.player_id = player

        self.player_sprite = SpriteStack(
            image_path="assets/sprite_stacking/player/player.png",
            slice_w=32,
            slice_h=32,
            scale=1.0,
            spread=0.65,
            y_scale=1.0
        )

        self.mouse_x = WINDOW_W / 2
        self.mouse_y = WINDOW_H / 2

        self.keys = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.keys)

        self.input_system = InputSystem(self.world, self.bus, self.keys)
        self.collision_system = CollisionSystem(self.world, self.loader)

        self.bus.subscribe("level_loaded", self._on_level_loaded)

        pyglet.clock.schedule_interval(self.on_update, 1 / 60)

    def _on_level_loaded(self, data):
        self.render_system.load_tilemap(self.loader.tilemap)

    def on_update(self, dt):
        self.input_system.update(dt)
        self.collision_system.update(dt)

        pos = self.world.get_component(self.player_id, "Position")
        rot = self.world.get_component(self.player_id, "Rotation")

        dx = self.mouse_x - pos["x"]
        dy = self.mouse_y - pos["y"]
        rot["angle"] = -math.degrees(math.atan2(dy, dx))

    def on_draw(self):
        self.clear()
        self.render_system.draw()

        pos = self.world.get_component(self.player_id, "Position")
        rot = self.world.get_component(self.player_id, "Rotation")
        self.player_sprite.draw(pos["x"], pos["y"], angle=rot["angle"])

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            self.close()

if __name__ == "__main__":
    game = Game()
    pyglet.app.run()
