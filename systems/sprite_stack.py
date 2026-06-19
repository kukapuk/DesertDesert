import pyglet

class SpriteStack:
    def __init__(self, image_path, slice_w, slice_h, scale=1.0, spread=1.5):
        self.slice_w = slice_w
        self.slice_h = slice_h
        self.scale = scale
        self.spread = spread
        self.slices = []

        source = pyglet.image.load(image_path)
        total = source.height // slice_h

        for i in range(total):
            region = source.get_region(
                0,
                source.height - (i + 1) * slice_h,
                slice_w,
                slice_h
            )
            region.anchor_x = slice_w // 2
            region.anchor_y = slice_h // 2
            self.slices.append(region)

        self.slices.reverse()

    def draw(self, x, y, angle=0.0):
        for i, region in enumerate(self.slices):
            sprite = pyglet.sprite.Sprite(region)
            sprite.x = x
            sprite.y = y + i * self.spread * self.scale
            sprite.scale_x = self.scale
            sprite.scale_y = self.scale * 0.5
            sprite.rotation = angle
            sprite.draw()
            sprite.delete()
