import pygame

from block import Block
from chunk import Chunk

class World:
    def __init__(self, assets):
        self.assets = assets

        self.BLOCK_SIZE = 64
        self.CHUNK_SIZE = 16
        self.SEED = 12345
        self.RENDER_DISTANCE = 3

        self.chunks = {}

    def add_block(self, grid_x, grid_y, block_type):
        chunk_x = grid_x // self.CHUNK_SIZE
        chunk_y = grid_y // self.CHUNK_SIZE

        chunk_pos = (chunk_x, chunk_y)

        if chunk_pos not in self.chunks:
            self.chunks[chunk_pos] = Chunk(chunk_x, chunk_y)

        chunk = self.chunks[chunk_pos]

        local_x = grid_x % self.CHUNK_SIZE
        local_y = grid_y % self.CHUNK_SIZE

        x = grid_x * self.BLOCK_SIZE + self.BLOCK_SIZE // 2
        y = grid_y * self.BLOCK_SIZE + self.BLOCK_SIZE // 2

        block = Block((x, y), block_type, self.assets)

        chunk.blocks[(local_x,local_y)] = block

    def delete_block(self, grid_x, grid_y):
        chunk_x = grid_x // self.CHUNK_SIZE
        chunk_y = grid_y // self.CHUNK_SIZE
        
        chunk_pos = (chunk_x, chunk_y)
        
        if chunk_pos not in self.chunks:
            self.chunks[chunk_pos] = Chunk(chunk_x, chunk_y)
        
        chunk = self.chunks[chunk_pos]
        
        local_x = grid_x % self.CHUNK_SIZE
        local_y = grid_y % self.CHUNK_SIZE
        
        chunk.blocks.pop((local_x,local_y),None)

    def get_nearby_blocks(self, rect):
        blocks = []

        left = (rect.left - self.BLOCK_SIZE) // self.BLOCK_SIZE
        right = (rect.right + self.BLOCK_SIZE) // self.BLOCK_SIZE
        top = (rect.top - self.BLOCK_SIZE) // self.BLOCK_SIZE
        bottom = (rect.bottom + self.BLOCK_SIZE) // self.BLOCK_SIZE

        for grid_y in range(top, bottom + 1):
            for grid_x in range(left, right + 1):

                chunk_x = grid_x // self.CHUNK_SIZE
                chunk_y = grid_y // self.CHUNK_SIZE

                chunk = self.chunks.get((chunk_x, chunk_y))

                if chunk is None:
                    continue

                local_x = grid_x % self.CHUNK_SIZE
                local_y = grid_y % self.CHUNK_SIZE

                block = chunk.blocks.get((local_x, local_y))

                if block is not None:
                    blocks.append(block)

        return blocks

    def draw(self, screen, camera):
        self.generate_around(pygame.Rect(camera.x, camera.y, camera.width, camera.height))

        screen_rect = pygame.Rect(camera.x, camera.y, camera.width, camera.height)

        left = int(camera.x // self.BLOCK_SIZE)
        right = int((camera.x + camera.width) // self.BLOCK_SIZE)

        top = int(camera.y // self.BLOCK_SIZE)
        bottom = int((camera.y + camera.height) // self.BLOCK_SIZE)

        first_chunk_x = left // self.CHUNK_SIZE
        last_chunk_x = right // self.CHUNK_SIZE

        first_chunk_y = top // self.CHUNK_SIZE
        last_chunk_y = bottom // self.CHUNK_SIZE

        for chunk_x in range(first_chunk_x, last_chunk_x + 1):
            for chunk_y in range(first_chunk_y, last_chunk_y + 1):

                chunk = self.chunks.get((chunk_x, chunk_y))

                if chunk is None:
                    continue

                for block in chunk.blocks.values():
                    if block.rect.colliderect(screen_rect):
                        screen.blit(block.image,(block.rect.x - camera.x,block.rect.y - camera.y))

    def generate_chunk(self, chunk_x, chunk_y):
        chunk_pos = (chunk_x, chunk_y)

        if chunk_pos in self.chunks:
            return

        self.chunks[chunk_pos] = Chunk(chunk_x, chunk_y)

        start_x = chunk_x * self.CHUNK_SIZE
        end_x = start_x + self.CHUNK_SIZE

        start_y = chunk_y * self.CHUNK_SIZE
        end_y = start_y + self.CHUNK_SIZE

        for grid_x in range(start_x, end_x):
            surface_y = self.terrain_height(grid_x)

            for grid_y in range(start_y, end_y):
                if grid_y < surface_y:
                    continue

                depth = grid_y - surface_y

                if depth == 0:
                    block_type = "grass"
                elif depth <= 5:
                    block_type = "dirt"
                else:
                    block_type = "stone"

                self.add_block(grid_x, grid_y, block_type)

    def terrain_height(self, x):
        import math

        height = 0

        height += math.sin(x * 0.015) * 10
        height += math.sin(x * 0.035) * 4
        height += math.sin(x * 0.08) * 2

        return int(height)

    def generate_around(self, rect):
        grid_x = int(rect.centerx // self.BLOCK_SIZE)
        grid_y = int(rect.centery // self.BLOCK_SIZE)

        player_chunk_x = grid_x // self.CHUNK_SIZE
        player_chunk_y = grid_y // self.CHUNK_SIZE

        for chunk_x in range(
            player_chunk_x - self.RENDER_DISTANCE,
            player_chunk_x + self.RENDER_DISTANCE + 1
        ):
            for chunk_y in range(
                player_chunk_y - self.RENDER_DISTANCE,
                player_chunk_y + self.RENDER_DISTANCE + 1
            ):
                self.generate_chunk(chunk_x, chunk_y)