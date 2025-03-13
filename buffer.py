import numpy as np
from superfice import XYZ

class ZBuffer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.pBuffer = np.full((width, height), np.inf)

    def clear(self):
        self.pBuffer.fill(np.inf)

    def at(self, x, y):

        assert 0 <= x < self.width
        assert 0 <= y < self.height
        if 0 <= x < self.pBuffer.shape[0] and 0 <= y < self.pBuffer.shape[1]:
            return self.pBuffer[x, y]
        else:
            raise IndexError("x or y is out of bounds.")

    def test_and_set(self, x, y, depth):
        depth_in_buffer = self.at(x, y)
        if depth < depth_in_buffer:
            self.pBuffer[x, y] = depth
            return True
        return False

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_min_max(self):
        return self.pBuffer.min(), self.pBuffer.max()

class ImageBuffer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.buffer = np.zeros((width, height, 3), dtype=np.uint8)

    def put_pixel(self, x, y, color):
        assert 0 <= x < self.width
        assert 0 <= y < self.height
        self.buffer[x, y] = color

    def get_pixel(self, x, y):
        assert 0 <= x < self.width
        assert 0 <= y < self.height
        return self.buffer[x, y]

    def clear(self):
        self.buffer = np.zeros((self.buffer.shape[0], self.buffer.shape[1], 3), dtype=np.uint8)
