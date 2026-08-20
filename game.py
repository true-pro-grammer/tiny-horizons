import pygame

from assets import Assets
from player import Player
from world import World
from camera import Camera

class Game:
    BLOCK_SIZE = 64
    CHUNK_SIZE = 16
    FIXED_DT = 1/60

    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height

        self.accumulator = 0

        self.assets = Assets()

        self.player = pygame.sprite.GroupSingle()
        self.player.add(Player((960, 540), self.assets))
        self.player.sprite.teleport((0,0))

        self.camera = Camera(self.width, self.height)

        self.world = World(self.assets)

    def tick(self, dt, keys):
        keys = pygame.key.get_pressed()
        self.player.sprite.inputs_in(keys)

        self.accumulator += dt
        while self.accumulator >= self.FIXED_DT:
            zonal_blocks = self.world.get_nearby_blocks(self.player.sprite.hitbox)
            self.player.update(self.FIXED_DT, zonal_blocks)
        
            self.accumulator -= self.FIXED_DT
        self.camera.update(self.player.sprite)
        
        self.screen.fill("skyblue")
        
        self.world.draw(self.screen, self.camera)
        
        self.screen.blit(self.player.sprite.image, (self.player.sprite.rect.x-self.camera.x, self.player.sprite.rect.y-self.camera.y))

        return None