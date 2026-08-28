import pygame
from collections import deque
from noise import pnoise1
from time import perf_counter

from block import Block, BlockType, BreakState
from chunk import Chunk
from utils import split_evenly

class World:
    def __init__(self, assets, logger, block_size, chunk_size):
        self.assets = assets
        self.logger = logger

        self.BLOCK_SIZE = block_size
        self.CHUNK_SIZE = chunk_size
        self.GOD_SEED = "99999"
        self.SEEDLINGS = split_evenly(self.GOD_SEED, 1)
        self.SEED = 1

        self.RENDER_DISTANCE = 1

        self.BASE_HEIGHT = 0
        self.HEIGHT_SCALE = 30
        self.ROCK_HEIGHT = 5
        self.ROCK_SCALE = 5
        
        self.SCALE = 0.008
        self.OCTAVES = 4
        self.PERSISTENCE = 0.5
        self.LACUNARITY = 2.0

        self.chunks = {}
        self.chunk_queue = deque()
        self.queued_chunks = set()
        self._blocks_revision = 0
        self._nearby_blocks_cache = None
        self.benchmark_timing_enabled = False
        self.benchmark_timings = {}
        self.logger.info("Initialised world")

    def _grid_to_chunk(self, grid_x, grid_y):
        chunk_pos = (
            grid_x // self.CHUNK_SIZE,
            grid_y // self.CHUNK_SIZE,
        )
        local_pos = (
            grid_x % self.CHUNK_SIZE,
            grid_y % self.CHUNK_SIZE,
        )
        return chunk_pos, local_pos

    def _get_chunk_at(self, grid_x, grid_y):
        chunk_pos, local_pos = self._grid_to_chunk(grid_x, grid_y)
        return self.chunks.get(chunk_pos), local_pos

    def _get_or_create_chunk(self, chunk_pos):
        if chunk_pos not in self.chunks:
            chunk_x, chunk_y = chunk_pos
            self.chunks[chunk_pos] = Chunk(
                chunk_x,
                chunk_y,
                self.BLOCK_SIZE,
                self.logger,
            )
        return self.chunks[chunk_pos]

    def _get_or_create_chunk_at(self, grid_x, grid_y):
        chunk_pos, local_pos = self._grid_to_chunk(grid_x, grid_y)
        return self._get_or_create_chunk(chunk_pos), local_pos

    def _get_block(self, grid_x, grid_y):
        chunk, local_pos = self._get_chunk_at(grid_x, grid_y)
        if chunk is None:
            return None
        return chunk.blocks.get(local_pos)

    def add_block(self, grid_x, grid_y, block_type):
        chunk, local_pos = self._get_or_create_chunk_at(grid_x, grid_y)

        neighbours = ((grid_x + 1, grid_y), (grid_x - 1, grid_y),
                      (grid_x, grid_y + 1), (grid_x, grid_y - 1))
        not_suspended = False
        for neighbour_x, neighbour_y in neighbours:
            if isinstance(self._get_block(neighbour_x, neighbour_y), Block):
                not_suspended = True
                break
        
        if chunk.blocks.get(local_pos) is None and not_suspended:
            x = grid_x * self.BLOCK_SIZE + self.BLOCK_SIZE // 2
            y = grid_y * self.BLOCK_SIZE + self.BLOCK_SIZE // 2

            block = Block((x, y), block_type, self.assets)

            chunk.blocks[local_pos] = block
            chunk.modified = True
            chunk.bake()
            self._blocks_revision += 1

    def fetch_surface_height(self, grid_x, mode="surface"):
        if mode == "surface":
            surface_y = int(self.BASE_HEIGHT + pnoise1(grid_x*self.SCALE,octaves=self.OCTAVES,persistence=self.PERSISTENCE,lacunarity=self.LACUNARITY,base=self.SEED) * self.HEIGHT_SCALE)
        elif mode == "rock":
            surface_y = int(self.ROCK_HEIGHT + pnoise1(grid_x*self.SCALE,octaves=self.OCTAVES,persistence=self.PERSISTENCE,lacunarity=self.LACUNARITY,base=self.SEED+1) * self.ROCK_SCALE)
        return surface_y

    def delete_block(self, grid_x, grid_y):
        chunk, local_pos = self._get_or_create_chunk_at(grid_x, grid_y)
        if chunk.blocks.pop(local_pos, None) is not None:
            chunk.modified = True
            chunk.bake()
            self._blocks_revision += 1

    def erode_block(self, grid_x, grid_y, dt):
        chunk, local_pos = self._get_chunk_at(grid_x, grid_y)
        if chunk is None:
            return

        block = chunk.blocks.get(local_pos)

        if block is None:
            return

        state = block.erode(dt)
        if state == BreakState.DESTROYED:
            chunk.blocks.pop(local_pos)
            chunk.modified = True
            chunk.bake()
            self._blocks_revision += 1
            return
        if state == BreakState.INTACT:
            return
        return state

    def reset_block_integrity(self, grid_x, grid_y):
        block = self._get_block(grid_x, grid_y)

        if block is not None:
            block.reset_integrity()

    def get_nearby_blocks(self, rect):
        cache_key = (
            (rect.left - self.BLOCK_SIZE) // self.BLOCK_SIZE,
            (rect.right + self.BLOCK_SIZE) // self.BLOCK_SIZE,
            (rect.top - self.BLOCK_SIZE) // self.BLOCK_SIZE,
            (rect.bottom + self.BLOCK_SIZE) // self.BLOCK_SIZE,
            self._blocks_revision,
        )
        if self._nearby_blocks_cache is not None and self._nearby_blocks_cache[0] == cache_key:
            return self._nearby_blocks_cache[1]

        blocks = []

        left, right, top, bottom, _ = cache_key

        for grid_y in range(top, bottom + 1):
            for grid_x in range(left, right + 1):
                chunk, local_pos = self._get_chunk_at(grid_x, grid_y)

                if chunk is None:
                    continue

                block = chunk.blocks.get(local_pos)

                if block is not None:
                    blocks.append(block)

        self._nearby_blocks_cache = (cache_key, blocks)
        return blocks

    def draw(self, renderer, camera):
        if self.benchmark_timing_enabled:
            self._benchmark_chunk_generation_time = 0.0
            self._benchmark_chunk_baking_time = 0.0
            world_started_at = perf_counter()
            generation_started_at = perf_counter()

        self.generate_around(pygame.Rect(camera.x, camera.y, camera.width, camera.height))
        self.load_next_chunk()
        self.unload_far_chunks(camera, renderer)

        if self.benchmark_timing_enabled:
            generation_time = perf_counter() - generation_started_at
            rendering_started_at = perf_counter()

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

                if chunk is None or not chunk.blocks:
                    continue
                if chunk.texture_dirty:
                    renderer.invalidate_surface(chunk.image)
                    chunk.texture_dirty = False
                renderer.draw_surface(
                    chunk.image,
                    (chunk.x * self.CHUNK_SIZE * self.BLOCK_SIZE - camera.x,
                     chunk.y * self.CHUNK_SIZE * self.BLOCK_SIZE - camera.y),
                )

        if self.benchmark_timing_enabled:
            self.benchmark_timings = {
                "world_time": perf_counter() - world_started_at,
                "world_generation_time": generation_time,
                "chunk_generation_time": self._benchmark_chunk_generation_time,
                "chunk_baking_time": self._benchmark_chunk_baking_time,
                "world_render_time": perf_counter() - rendering_started_at,
            }

    def generate_chunk(self, chunk_x, chunk_y):
        generation_started_at = perf_counter() if self.benchmark_timing_enabled else None
        chunk_pos = (chunk_x, chunk_y)

        if chunk_pos in self.chunks:
            return

        self.chunks[chunk_pos] = Chunk(chunk_x, chunk_y, self.BLOCK_SIZE, self.logger)

        start_x = chunk_x * self.CHUNK_SIZE
        end_x = start_x + self.CHUNK_SIZE

        start_y = chunk_y * self.CHUNK_SIZE
        end_y = start_y + self.CHUNK_SIZE

        for grid_x in range(start_x, end_x):
            surface_y = self.fetch_surface_height(grid_x)
            rock_y = self.fetch_surface_height(grid_x, mode="rock")

            for grid_y in range(surface_y, end_y):
                if grid_y < rock_y:
                    block_type = BlockType.DIRT
                else:
                    block_type = BlockType.STONE

                local_x = grid_x % self.CHUNK_SIZE
                local_y = grid_y % self.CHUNK_SIZE

                x = grid_x * self.BLOCK_SIZE + self.BLOCK_SIZE // 2
                y = grid_y * self.BLOCK_SIZE + self.BLOCK_SIZE // 2

                block = Block(
                    (x, y),
                    block_type,
                    self.assets
                )

                self.chunks[chunk_pos].blocks[(local_x, local_y)] = block
        baking_started_at = perf_counter() if self.benchmark_timing_enabled else None
        self.chunks[chunk_pos].bake()
        self._benchmark_chunk_baking_time = (
            perf_counter() - baking_started_at
            if self.benchmark_timing_enabled else 0.0
        )
        self._benchmark_chunk_generation_time = (
            perf_counter() - generation_started_at
            if self.benchmark_timing_enabled else 0.0
        )
        self._blocks_revision += 1

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
                chunk_pos = (chunk_x, chunk_y)
                if chunk_pos not in self.chunks and chunk_pos not in self.queued_chunks:
                    self.chunk_queue.append(chunk_pos)
                    self.queued_chunks.add(chunk_pos)

    def load_next_chunk(self):
        while self.chunk_queue:
            chunk_pos = self.chunk_queue.popleft()
            self.queued_chunks.discard(chunk_pos)
            if chunk_pos not in self.chunks:
                self.generate_chunk(*chunk_pos)
            return

    def unload_far_chunks(self, camera, renderer):
        center_x = (camera.x + camera.width // 2) // self.BLOCK_SIZE
        center_y = (camera.y + camera.height // 2) // self.BLOCK_SIZE

        center_chunk_x = center_x // self.CHUNK_SIZE
        center_chunk_y = center_y // self.CHUNK_SIZE

        for chunk_pos in list(self.chunks):
            chunk_x, chunk_y = chunk_pos

            if (
                abs(chunk_x - center_chunk_x) > self.RENDER_DISTANCE
                or abs(chunk_y - center_chunk_y) > self.RENDER_DISTANCE
            ) and not self.chunks[chunk_pos].modified:
                renderer.invalidate_surface(self.chunks[chunk_pos].image)
                del self.chunks[chunk_pos]
