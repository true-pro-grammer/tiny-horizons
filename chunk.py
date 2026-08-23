import pygame

class Chunk:
    def __init__(self, x, y, block_size, logger):
        self.SIZE = 16
        self.BLOCK_SIZE = block_size
        self.logger = logger

        self.x = x
        self.y = y
        self.blocks = {}
        self.modified = False
        self.image = pygame.Surface(
            (self.SIZE * self.BLOCK_SIZE, self.SIZE * self.BLOCK_SIZE)
        ).convert()
    
    def bake(self):
        self.image.fill("skyblue")

        for (local_x, local_y), block in self.blocks.items():
            self.image.blit(block.image, (local_x * self.BLOCK_SIZE, local_y * self.BLOCK_SIZE))
        self.logger.debug(f"Baked chunk at ({self.x}, {self.y}) with {len(self.blocks)} blocks")