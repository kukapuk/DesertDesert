import math

class Camera:
    def __init__(self, window_w, window_h, smoothing=8.0):
        self.window_w = window_w
        self.window_h = window_h
        self.smoothing = smoothing
        self.x = 0.0
        self.y = 0.0

    def update(self, target_x, target_y, dt):
        target_cam_x = target_x - self.window_w / 2
        target_cam_y = target_y - self.window_h / 2

        t = 1.0 - math.exp(-self.smoothing * dt)

        self.x += (target_cam_x - self.x) * t
        self.y += (target_cam_y - self.y) * t
