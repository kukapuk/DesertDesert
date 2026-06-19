import pytiled_parser
from pytiled_parser import parse_map
from pathlib import Path

class LevelLoader:
    def __init__(self, world, bus):
        self.world = world
        self.bus = bus
        self.tilemap = None
        self.spawn_point = {"x": 100.0, "y": 100.0}
        self.wall_tiles = set()
        self.tile_width = 32
        self.tile_height = 32
        self.map_height = 0

        self.bus.subscribe("level_exit", self._on_level_exit)

    def load(self, path: str, keep_entities: list = None):
        full_path = Path(path)
        self.tilemap = parse_map(full_path)
        self.tile_width = self.tilemap.tile_size.width
        self.tile_height = self.tilemap.tile_size.height
        self.map_height = self.tilemap.map_size.height
        self.wall_tiles = set()

        self.world.clear_level(keep=keep_entities or [])

        for layer in self.tilemap.layers:
            if isinstance(layer, pytiled_parser.ObjectLayer):
                self._load_objects(layer)
            elif isinstance(layer, pytiled_parser.TileLayer):
                if layer.name == "walls":
                    self._load_walls(layer)

        self.bus.publish("level_loaded", {"path": path})

    def _load_walls(self, layer):
        for y, row in enumerate(layer.data):
            for x, gid in enumerate(row):
                if gid != 0:
                    self.wall_tiles.add((x, y))

    def is_wall(self, tile_x, tile_y):
        return (tile_x, tile_y) in self.wall_tiles

    def world_to_tile(self, wx, wy):
        tx = int(wx // self.tile_width)
        ty = int(self.map_height - 1 - wy // self.tile_height)
        return tx, ty

    def _load_objects(self, layer):
        for obj in layer.tiled_objects:
            props = obj.properties or {}
            obj_type = props.get("type") or obj.name

            if obj_type == "spawn":
                self.spawn_point = {"x": float(obj.coordinates.x),
                                    "y": float(obj.coordinates.y)}

            elif obj_type == "trigger":
                eid = self.world.create_entity()
                self.world.add_component(eid, "Position", {
                    "x": float(obj.coordinates.x),
                    "y": float(obj.coordinates.y),
                })
                self.world.add_component(eid, "Trigger", {
                    "w": float(obj.size.width),
                    "h": float(obj.size.height),
                    "next": props.get("next", ""),
                })

            elif obj_type == "enemy":
                eid = self.world.create_entity()
                self.world.add_component(eid, "Position", {
                    "x": float(obj.coordinates.x),
                    "y": float(obj.coordinates.y),
                })
                self.world.add_component(eid, "Enemy", {
                    "type": props.get("enemy_type", "basic"),
                })

    def _on_level_exit(self, data):
        next_level = data.get("next", "")
        if next_level:
            self.load(f"levels/{next_level}.tmx")

    def get_spawn(self):
        return self.spawn_point
