import pygame
from enum import Flag, auto

from player import Player
from world import World
from camera import Camera
from utils import Event
from block import BlockType
from ui import Hotbar

class DebugMode(Flag):
    SHOW_COORDS = auto()
    SHOW_HITBOX_PLAYER = auto()
    SHOW_HITBOX_NEARBY = auto()
    SHOW_BOUNDING_BOX = auto()
    SHOW_PLACE_RESTRICTION = auto()
    HIDE_VIGNETTE = auto()

#inventory 0-7 inc

class Game:
    BLOCK_SIZE = 64
    CHUNK_SIZE = 16
    FIXED_DT = 1/60

    def __init__(self, renderer, logger, width, height, assets):
        self.renderer = renderer
        self.logger = logger
        self.width = width
        self.height = height
        self.debug = DebugMode.HIDE_VIGNETTE

        self.inventory = [
            BlockType.GRASS,
            BlockType.DIRT,
            BlockType.STONE,
            BlockType.COAL,
            BlockType.LOG,
            BlockType.LEAF,
            None,
            None,
        ]

        self.accumulator = 0
        self.zonal_blocks = []
        self.erode_target = None
        self.block_break_overlay = None
        self.selected_block = 0

        self.assets = assets

        self.vignette_img = assets.image("vignette")
        self.vignette_default_img = pygame.transform.smoothscale(assets.image("vignette_default"), (self.width, self.height)).convert_alpha()

        self.VIGNETTE_INTENSITY = 1
        self.MAX_REACH = (400, 256)

        self.camera = Camera(self.width, self.height)
        self.hotbar = Hotbar(self.renderer, self.width, self.height, self.assets)

        self.font = pygame.font.Font(None, 30)

        self.world = World(self.assets, self.logger, self.BLOCK_SIZE, self.CHUNK_SIZE)

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

    def inputs_in(self, mouse, events):
        previous_target = self.erode_target
        self.erode_target = None
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return Event.QUIT_GAME
                match event.key:
                    case pygame.K_1: self.selected_block = 0
                    case pygame.K_2: self.selected_block = 1
                    case pygame.K_3: self.selected_block = 2
                    case pygame.K_4: self.selected_block = 3
                    case pygame.K_5: self.selected_block = 4
                    case pygame.K_6: self.selected_block = 5
                    case pygame.K_7: self.selected_block = 6
                    case pygame.K_8: self.selected_block = 7
        if mouse[0][0] or mouse[0][2]:
            self.world_pos = (mouse[1][0]+self.camera.x, mouse[1][1]+self.camera.y)
            if self.player.sprite.rect.inflate(*self.MAX_REACH).collidepoint(self.world_pos):
                if mouse[0][0]:
                    self.erode_target = (self.world_pos[0]//self.BLOCK_SIZE,self.world_pos[1]//self.BLOCK_SIZE)
                if mouse[0][2]:
                    grid_x = self.world_pos[0]//self.BLOCK_SIZE
                    grid_y = self.world_pos[1]//self.BLOCK_SIZE
                    block_rect = pygame.Rect(
                        grid_x * self.BLOCK_SIZE,
                        grid_y * self.BLOCK_SIZE,
                        self.BLOCK_SIZE,
                        self.BLOCK_SIZE,
                    )
                    if not block_rect.colliderect(self.player.sprite.hitbox) and self.inventory[self.selected_block] is not None:
                        self.world.add_block(grid_x, grid_y, self.inventory[self.selected_block])

        if self.erode_target != previous_target:
            self.block_break_overlay = None
            if previous_target is not None:
                self.world.reset_block_integrity(*previous_target)

    def handle_addons(self):
        if not DebugMode.HIDE_VIGNETTE in self.debug:
            self.renderer.draw_surface(self.vignette_default_img, (0, 0))
        if DebugMode.SHOW_COORDS in self.debug:
            txt = self.font.render(f"x:{self.player.sprite.hitbox.centerx} y:{self.player.sprite.hitbox.bottom}", True, "red")
            self.renderer.draw_surface(txt, (10,30))
        if DebugMode.SHOW_HITBOX_PLAYER in self.debug:
            hitbox = self.player.sprite.hitbox.move(-self.camera.x, -self.camera.y)
            self.renderer.draw_rect(hitbox, "red", 2, skeleton=True)
        if DebugMode.SHOW_HITBOX_NEARBY in self.debug:
            for block in self.zonal_blocks:
                wireframe = block.rect.move(-self.camera.x, -self.camera.y)
                self.renderer.draw_rect(wireframe, "pink", 2, skeleton=True)
        if DebugMode.SHOW_BOUNDING_BOX in self.debug:
            rect = self.player.sprite.rect.move(-self.camera.x, -self.camera.y)
            self.renderer.draw_rect(rect, "orange", 2, skeleton=True)
        if DebugMode.SHOW_PLACE_RESTRICTION in self.debug:
            outer = self.player.sprite.rect.inflate(*self.MAX_REACH).move(-self.camera.x, -self.camera.y)
            self.renderer.draw_rect(outer, "purple", 2, skeleton=True)
            if not DebugMode.SHOW_HITBOX_PLAYER in self.debug:
                hitbox = self.player.sprite.hitbox.move(-self.camera.x, -self.camera.y)
                self.renderer.draw_rect(hitbox, "purple", 2, skeleton=True)

    def tick(self, dt, keys, mouse, events):
        self.player.sprite.inputs_in(keys)
        inputs = self.inputs_in(mouse, events)

        self.accumulator += dt
        while self.accumulator >= self.FIXED_DT:
            self.zonal_blocks = self.world.get_nearby_blocks(self.player.sprite.hitbox)
            self.player.update(self.FIXED_DT, self.zonal_blocks)

            if self.erode_target is not None:
                self.block_break_overlay = self.world.erode_block(*self.erode_target, self.FIXED_DT)
        
            self.accumulator -= self.FIXED_DT
        self.camera.update(self.player.sprite)
        
        self.renderer.begin_frame()

        self.world.draw(self.renderer, self.camera)

        if self.block_break_overlay is not None and self.erode_target is not None:
            tex = self.assets.atlas_texture("smash", self.block_break_overlay)
            overlay_x = self.erode_target[0] * self.BLOCK_SIZE - self.camera.x
            overlay_y = self.erode_target[1] * self.BLOCK_SIZE - self.camera.y
            self.renderer.draw_surface(tex, (overlay_x, overlay_y))
        
        self.renderer.draw_surface(
            self.player.sprite.image,
            (self.player.sprite.rect.x-self.camera.x, self.player.sprite.rect.y-self.camera.y),
        )

        self.hotbar.draw(self.selected_block, self.inventory)
        self.handle_addons()
        

        return inputs
