import pygame
from enum import IntEnum

class BlockType(IntEnum):
    GRASS = 0
    DIRT = 1
    STONE = 2
    COAL = 3
    LOG = 4
    LEAF = 5

class Block(pygame.sprite.Sprite):
    def __init__(self, pos, id, assets):
        super().__init__()

        self.pos = pygame.Vector2(pos)
        self.size = (64,64)
        self.image = assets.atlas_texture("blocks", id)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self):
        pass