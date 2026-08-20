import pygame
from enum import StrEnum, IntEnum

#state,direction,frame no.
#anim speeds in s
#x4 scale from src to screen
#player pos is at feet, i.e. hitbox.midbottom, or (hitbox.centerx, hitbox.bottom)

class Direction(StrEnum):
    LEFT = "_left"
    RIGHT = "_right"
    STATIC = ""

class MovementState(StrEnum):
    IDLE = "idle"
    WALK = "walk"

class AerialState(IntEnum):
    PREPARING = 1
    RISING = 2
    FALLING = 3
    LANDING = 4

class Player(pygame.sprite.Sprite):
    ANIM_SPEEDS = {
        MovementState.IDLE: 0.1,
        MovementState.WALK: 0.1,
    }
    ACCELERATION_CONST = 2000
    MAX_SPEED = 400
    FRICTION = 3000
    GRAVITY = 2000
    JUMP_POWER = -600
    JUMP_PREPARE_TIME = 0.1
    LAND_TIME = 0.1

    def __init__(self, pos, assets):
        super().__init__()

        self.FRAME_LOGGING_DUMP = False
        self.FRAME_LOGGING_SMART = False

        self.assets = assets

        self.size = (96,96)
        self.velocity = pygame.Vector2(0,0)

        self.init_frames()

        self.frame_i = 0
        self.anim_timer = 0
        self.state_timer = 0
        self.state = MovementState.IDLE
        self.jump_state = None
        self.direction = Direction.STATIC

        self.image = self.frames[self.state][0]
        self.rect = self.image.get_rect()
        self.rect.midbottom = pos

        self.hitbox = pygame.Rect(0,0,48,64)
        self.hitbox.midbottom = self.rect.midbottom
    
    def reset_anims(self):
        self.frame_i = 0
        self.anim_timer = 0

    def set_state(self, state):
        if isinstance(state, MovementState):
            if state is not self.state:
                if self.FRAME_LOGGING_SMART:
                    print(f"MovementState changed from {self.state} to {state}")
                self.state = state
                self.frame_i = 0
                self.anim_timer = 0
        elif isinstance(state, AerialState) or state is None:
            if state is not self.jump_state:
                if self.FRAME_LOGGING_SMART:
                    print(f"AerialState changed from {self.jump_state} to {state}")
                self.jump_state = state

    def teleport(self, world_pos):
        self.hitbox.midbottom = world_pos

    def set_image(self, image):
        if self.FRAME_LOGGING_DUMP:
            print(f"Image size: {image.get_size()[0]}x{image.get_size()[1]} AerialState: {self.jump_state} State: {self.state} Frame: {self.frame_i}")
        bottom = self.rect.bottom
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.bottom = bottom
    
    def collider_x(self, blocks):
        for block in blocks:
            if self.hitbox.colliderect(block.rect):
                if self.velocity.x > 0:
                    self.hitbox.right = block.rect.left
                    self.velocity.x = 0
                elif self.velocity.x < 0:
                    self.hitbox.left = block.rect.right
                    self.velocity.x = 0
    
    def collider_y(self, blocks):
        for block in blocks:
            if self.hitbox.colliderect(block.rect):
                if self.velocity.y > 0:
                    self.hitbox.bottom = block.rect.top
                    self.velocity.y = 0
                    if self.jump_state is AerialState.FALLING:
                        self.state_timer = self.LAND_TIME
                        self.set_state(AerialState.LANDING)
                elif self.velocity.y < 0:
                    self.hitbox.top = block.rect.bottom
                    self.velocity.y = 0
            
    
    def init_frames(self):
        self.frames = {
            "idle": self.assets.spritesheet(
                name="idle",
                #path="graphics/idle.png",
                frame_size=(24, 24),
                frame_count=4,
                row=0,
                output_size=self.size,
            ),

            "walk_right": self.assets.spritesheet(
                name="walk",
                #path="graphics/walk.png",
                frame_size=(24, 24),
                frame_count=4,
                row=2,
                output_size=self.size,
            ),

            "walk_left": self.assets.spritesheet(
                name="walk",
                #path="graphics/walk.png",
                frame_size=(24, 24),
                frame_count=4,
                row=2,
                output_size=self.size,
                flip_x=True,
            ),

            "jump": self.assets.spritesheet(
                name="jump",
                frame_size=(24,22),
                frame_count=5,
                row=0,
                output_size=(96,88),
            ),

            "jump_right": self.assets.spritesheet(
                name="jump",
                frame_size=(24,22),
                frame_count=5,
                row=2,
                output_size=(96,88),
            ),

            "jump_left": self.assets.spritesheet(
                name="jump",
                frame_size=(24,22),
                frame_count=5,
                row=2,
                output_size=(96,88),
                flip_x=True,
            ),
        }
    
    def inputs_in(self, keys):
        net_x = keys[pygame.K_d] - keys[pygame.K_a]

        if net_x == -1:
            self.direction = Direction.LEFT
            self.set_state(MovementState.WALK)
        elif net_x == 1:
            self.direction = Direction.RIGHT
            self.set_state(MovementState.WALK)
        else:
            self.direction = Direction.STATIC
            self.set_state(MovementState.IDLE)
        
        if keys[pygame.K_w] and self.jump_state is None:
            self.state_timer = self.JUMP_PREPARE_TIME
            self.set_state(AerialState.PREPARING)

    
    def physics_play(self, dt, blocks):
        acceleration = pygame.Vector2(0,self.GRAVITY)
        if self.direction is Direction.LEFT: acceleration.x -= self.ACCELERATION_CONST
        elif self.direction is Direction.RIGHT: acceleration.x += self.ACCELERATION_CONST
        
        self.velocity += acceleration * dt
        self.velocity.x = pygame.math.clamp(self.velocity.x,-self.MAX_SPEED,self.MAX_SPEED)
        
        if self.direction is Direction.STATIC:
            if self.velocity.x > 0:
                self.velocity.x -= self.FRICTION * dt
                if self.velocity.x < 0:
                    self.velocity.x = 0
            elif self.velocity.x < 0:
                self.velocity.x += self.FRICTION * dt
                if self.velocity.x > 0:
                    self.velocity.x = 0

        self.hitbox.x += self.velocity.x * dt
        self.collider_x(blocks)
        self.hitbox.y += self.velocity.y * dt
        self.collider_y(blocks)

        if self.jump_state is AerialState.PREPARING:
            self.state_timer -= dt
        
            if self.state_timer <= 0:
                self.set_state(AerialState.RISING)
                self.velocity.y = self.JUMP_POWER
        elif self.jump_state is AerialState.LANDING:
            self.state_timer -= dt
        
            if self.state_timer <= 0:
                self.set_state(None)
        if self.velocity.y > 0:
            self.set_state(AerialState.FALLING)

    def anim_play(self, anim_speed, ground_state):
        while self.anim_timer + 1e-9 >= anim_speed:
            old_timer = self.anim_timer
            self.anim_timer -= anim_speed

            old_frame = self.frame_i
            self.frame_i += 1

            if self.frame_i >= len(self.frames[ground_state]):
                self.frame_i = 0

            if self.FRAME_LOGGING_SMART:
                print(
                    f"Frame changed from {old_frame} to {self.frame_i} | "
                    f"duration: {old_timer:.10f}s"
                )

    def update(self, dt, blocks):
        self.physics_play(dt, blocks)
        
        if self.jump_state is not None:
            self.set_image(self.frames["jump"+self.direction][self.jump_state])
        else:
            self.anim_timer += dt
            self.anim_play(self.ANIM_SPEEDS[self.state], self.state+self.direction)
            self.set_image(self.frames[self.state+self.direction][self.frame_i])
        
        self.rect.midbottom = self.hitbox.midbottom