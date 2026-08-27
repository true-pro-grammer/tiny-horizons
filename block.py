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

class Block(pygame.sprite.Sprite):
    def __init__(self, pos, id, assets):
        super().__init__()

        self.pos = pygame.Vector2(pos)
        self.size = (64,64)
        self.image = assets.atlas_texture("blocks", id)
        self.rect = self.image.get_rect(center=self.pos)
        self.hardness = HARDNESS_LOOKUP[id]

        self.integrity = 1.0

    def erode(self, dt):
        self.integrity -= dt / self.hardness
        if self.integrity <= 1e-9:
            self.integrity = 0
            return -1
        if self.integrity == 1:
            return 5
        return 4 - int(self.integrity / 0.2)

    def reset_integrity(self):
        self.integrity = 1.0

    def fetch_overlay(self):
        return self.integrity * 5 - 1

    def update(self):
        pass