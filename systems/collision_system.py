class CollisionSystem:
    def __init__(self, world, loader):
        self.world = world
        self.loader = loader
        self.player_hw = 12
        self.player_hh = 12

    def update(self, dt):
        for eid in self.world.get_entities_with("Position", "Velocity"):
            pos = self.world.get_component(eid, "Position")
            vel = self.world.get_component(eid, "Velocity")

            next_x = pos["x"] + vel["x"] * dt
            next_y = pos["y"] + vel["y"] * dt

            if not self._collides(next_x, pos["y"]):
                pos["x"] = next_x
            
            if not self._collides(pos["x"], next_y):
                pos["y"] = next_y

    def _collides(self, wx, wy):
        hw = self.player_hw
        hh = self.player_hh

        corners = [
            (wx - hw, wy - hh),
            (wx + hw, wy - hh),
            (wx - hw, wy + hh),
            (wx + hw, wy + hh),
        ]

        for cx, cy in corners:
            tx, ty = self.loader.world_to_tile(cx, cy)
            if self.loader.is_wall(tx, ty):
                return True

        return False
