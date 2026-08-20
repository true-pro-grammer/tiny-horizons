import pygame

class Block(pygame.sprite.Sprite):
    def __init__(self, pos, id, assets):
        super().__init__()

        self.pos = pygame.Vector2(pos)
        self.size = (64,64)
        self.image = assets.atlas_texture("blocks", id)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self):
        pass