import pyglet
import pytiled_parser

class RenderSystem:
    def __init__(self, world, window, tilemap=None):
        self.world = world
        self.window = window
        self.batch = pyglet.graphics.Batch()
        self.tile_sprites = []
        self.tilemap = tilemap

    def load_tilemap(self, tilemap):
        self.tilemap = tilemap
        self.tile_sprites.clear()
        self.batch = pyglet.graphics.Batch()

        for layer in tilemap.layers:
            if not isinstance(layer, pytiled_parser.TileLayer):
                continue
            self._build_tile_layer(layer, tilemap)

    def _build_tile_layer(self, layer, tilemap):
        for y, row in enumerate(layer.data):
            for x, gid in enumerate(row):
                if gid == 0:
                    continue

                image = self._get_tile_image(gid, tilemap)
                if image is None:
                    continue

                sx = x * tilemap.tile_size.width
                sy = (tilemap.map_size.height - y - 1) * tilemap.tile_size.height

                sprite = pyglet.sprite.Sprite(image, x=sx, y=sy, batch=self.batch)
                self.tile_sprites.append(sprite)

    def _get_tile_image(self, gid, tilemap):
        for tileset_gid, tileset in tilemap.tilesets.items():
            if tileset.image is None:
                continue

            local_id = gid - tileset_gid
            if local_id < 0 or local_id >= tileset.tile_count:
                continue

            try:
                image = pyglet.image.load(str(tileset.image))
            except Exception:
                return None

            cols = tileset.columns
            tw = tileset.tile_width
            th = tileset.tile_height

            col = local_id % cols
            row = local_id // cols

            region = image.get_region(
                col * tw,
                image.height - (row + 1) * th,
                tw,
                th
            )
            return region

        return None

    def draw(self, camera_x=0, camera_y=0):
        view = pyglet.math.Mat4.from_translation(
            pyglet.math.Vec3(-camera_x, -camera_y, 0)
        )
        self.window.view = view
        self.batch.draw()
        self.window.view = pyglet.math.Mat4()
