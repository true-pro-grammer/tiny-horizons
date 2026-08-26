import pygame

from player import Player
from world import World
from camera import Camera
from utils import Event

class Game:
    BLOCK_SIZE = 64
    CHUNK_SIZE = 16
    FIXED_DT = 1/60
    SHOW_COORDS = False

    def __init__(self, renderer, logger, width, height, assets):
        self.renderer = renderer
        self.logger = logger
        self.width = width
        self.height = height

        self.accumulator = 0

        self.assets = assets

        self.vignette_img = assets.image("vignette")
        self.vignette_default_img = pygame.transform.smoothscale(assets.image("vignette_default"), (self.width, self.height)).convert_alpha()

        self.VIGNETTE_INTENSITY = 1
        self.MIN_REACH = (64, 40)
        self.MAX_REACH = (320, 256)

        self.camera = Camera(self.width, self.height)

        self.font = pygame.font.Font(None, 30)

        self.world = World(self.assets, self.logger, self.BLOCK_SIZE, self.CHUNK_SIZE)

        origin_chunks = {}
        for y in range(-5,5):
            if (0,y) in self.world.chunks.keys():
                origin_chunks[(0,y)] = self.world.chunks[(0,y)]

        self.player = pygame.sprite.GroupSingle()
        self.player.add(Player((960, 540), self.assets, self.logger))
        self.player.sprite.teleport((0, -50))

    def draw_vignette(self):
        width = int(self.width * self.VIGNETTE_INTENSITY)

        scaled = pygame.transform.scale(
            self.vignette_img,
            (width, width)
        )

        x = (self.width - width) // 2
        y = (self.height - width) // 2

        mask = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        mask.fill((0, 0, 0, 255))
        mask.fill((0, 0, 0, 0), scaled.get_rect(center=(self.width//2, self.height//2)))

        self.renderer.draw_surface(scaled, (x, y))
        self.renderer.draw_surface(mask, (0, 0))

    def inputs_in(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return Event.QUIT_GAME
            if event.type == pygame.MOUSEBUTTONDOWN:
                world_pos = (event.pos[0]+self.camera.x, event.pos[1]+self.camera.y)
                if self.player.sprite.rect.inflate(*self.MAX_REACH).collidepoint(world_pos):
                    match event.button:
                        case 1:
                            self.world.delete_block(world_pos[0]//self.BLOCK_SIZE,world_pos[1]//self.BLOCK_SIZE)
                        case 3:
                            if not self.player.sprite.rect.inflate(*self.MIN_REACH).collidepoint(world_pos):
                                self.world.add_block(world_pos[0]//self.BLOCK_SIZE,world_pos[1]//self.BLOCK_SIZE,"dirt")

    def tick(self, dt, keys, events):
        self.player.sprite.inputs_in(keys)
        inputs = self.inputs_in(events)

        self.accumulator += dt
        while self.accumulator >= self.FIXED_DT:
            zonal_blocks = self.world.get_nearby_blocks(self.player.sprite.hitbox)
            self.player.update(self.FIXED_DT, zonal_blocks)
        
            self.accumulator -= self.FIXED_DT
        self.camera.update(self.player.sprite)
        
        self.renderer.begin_frame()
        
        self.world.draw(self.renderer, self.camera)
        
        self.renderer.draw_surface(
            self.player.sprite.image,
            (self.player.sprite.rect.x-self.camera.x, self.player.sprite.rect.y-self.camera.y),
        )

        #if self.VIGNETTE_INTENSITY == 1:
            #self.screen.blit(self.vignette_default_img, (0, 0))
        #else:
            #self.draw_vignette()
        #self.screen.blit(self.vignette_default_img, (0, 0))
        #self.renderer.draw_surface(self.vignette_default_img, (0, 0))

        debug_rect = self.player.sprite.rect.inflate(*self.MAX_REACH)
        debug_2_rect = self.player.sprite.rect.inflate(*self.MIN_REACH)
        debug_rect.x -= self.camera.x
        debug_rect.y -= self.camera.y
        debug_2_rect.x -= self.camera.x
        debug_2_rect.y -= self.camera.y
        self.renderer.draw_rect(debug_rect, "red", 2, skeleton=True)
        self.renderer.draw_rect(debug_2_rect, "red", 2, skeleton=True)

        if self.SHOW_COORDS:
            txt = self.font.render(f"x:{self.player.sprite.hitbox.centerx} y:{self.player.sprite.hitbox.bottom}", True, "red")
            self.renderer.draw_surface(txt, (10,30))

        return inputs
