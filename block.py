import pygame
from enum import IntEnum

class BlockType(IntEnum):
    GRASS = 0
    DIRT = 1
    STONE = 2
    COAL = 3
    LOG = 4
    LEAF = 5

HARDNESS_LOOKUP = {
    BlockType.GRASS: 1,
    BlockType.DIRT: 1,
    BlockType.STONE: 10,
    BlockType.COAL: 15,
    BlockType.LOG: 5,
    BlockType.LEAF: 0.5,
}

class BreakState(IntEnum):
    INTACT = -1
    BROKEN_0 = 0
    BROKEN_1 = 1
    BROKEN_2 = 2
    BROKEN_3 = 3
    BROKEN_4 = 4
    DESTROYED = 5

class Block(pygame.sprite.Sprite):
    def __init__(self, pos, block_id, assets, block_size=64):
        super().__init__()

        self.pos = pygame.Vector2(pos)
        self.size = (block_size, block_size)
        if block_id is BlockType.LEAF:
            self.image = assets.atlas_texture("blocks", block_id, alpha=True)
        else:
            self.image = assets.atlas_texture("blocks", block_id)
        self.rect = self.image.get_rect(center=self.pos)
        self.hardness = HARDNESS_LOOKUP[block_id]

        self.integrity = 1.0

    def erode(self, dt):
        self.integrity -= dt / self.hardness
        if self.integrity <= 1e-9:
            self.integrity = 0
            return BreakState.DESTROYED
        return 4 - int(self.integrity / 0.2 + 1e-9)

    def reset_integrity(self):
        self.integrity = 1.0

    def update(self):
        pass