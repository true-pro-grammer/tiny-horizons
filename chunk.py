
class Chunk:
    def __init__(self, x, y):
        self.SIZE = 16

        self.x = x
        self.y = y
        self.blocks = {}
        self.modified = False