class MovementSystem:
    def __init__(self, world):
        self.world = world

    def update(self, dt):
        for eid in self.world.get_entities_with("Position", "Velocity"):
            pos = self.world.get_component(eid, "Position")
            vel = self.world.get_component(eid, "Velocity")

            pos["x"] += vel["x"] * dt
            pos["y"] += vel["y"] * dt
