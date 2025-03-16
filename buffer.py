import numpy as np
from superfice import XYZ, RGB

class Buffer:
    def __init__(self, width, height, background_color=RGB(255, 255, 255)):
        self.width = width
        self.height = height
        self.background_color = background_color
        self.z_buffer = np.full((width, height), np.inf)
        self.image_buffer = np.full((width, height), background_color)

    def reset(self):
        self.z_buffer.fill(np.inf)
        self.image_buffer.fill(self.background_color)

    def test_and_set(self, x, y, depth, cor_pixel):
        depth_in_buffer = self.z_buffer[x, y]
        if depth < depth_in_buffer:
            self.z_buffer[x, y] = depth
            self.image_buffer[x, y] = cor_pixel
