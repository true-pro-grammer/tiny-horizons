import pygame
from collections import deque
from enum import Enum, auto
from time import perf_counter

from game import Game
from menu import StartMenu, PauseMenu
from utils import Event
from logger import Logger
from assets import Assets
from renderer import Renderer

#MOUSE = (BUTTONS, POS)

class AppState(Enum):
    START = auto()
    PLAY = auto()
    PAUSE = auto()

class App:
    NAME = "Bloop's Saga"
    WIDTH = 1920
    HEIGHT = 1080
    FRAME_STATS_UPDATE_INTERVAL = 0.25

    def __init__(self):
        self.started_at = perf_counter()
        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.WIDTH, self.HEIGHT),
            pygame.FULLSCREEN | pygame.OPENGL | pygame.DOUBLEBUF,
            vsync=0,
        )
        self.renderer = Renderer(self.WIDTH, self.HEIGHT)
        pygame.display.set_caption(self.NAME)
        self.state = AppState.START

        self.font = pygame.font.Font(None, 30)
        self.last_frame_started_at = perf_counter()
        self.frame_times = deque(maxlen=120)
        self.frame_stats_surface = None
        self.last_frame_stats_update_at = 0.0
        self.total_frame_time = 0.0
        self.frame_count = 0
        self.logger = Logger()
        self.assets = Assets()
        self.game = Game(self.renderer, self.logger, self.WIDTH, self.HEIGHT, self.assets)
        self.start_menu = StartMenu(self.renderer, self.WIDTH, self.HEIGHT, self.assets)
        self.pause_menu = PauseMenu(self.renderer, self.WIDTH, self.HEIGHT, self.assets)
        self.running = True

    def tick(self, events, keys, mouse):
        frame_started_at = perf_counter()
        frame_dt = frame_started_at - self.last_frame_started_at
        self.last_frame_started_at = frame_started_at
        self.frame_times.append(frame_dt)
        self.total_frame_time += frame_dt
        self.frame_count += 1
        dt = min(frame_dt, 0.1)

        match self.state:
            case AppState.PLAY:
                report = self.game.tick(dt, keys, mouse, events)
            case AppState.START:
                report = self.start_menu.tick(mouse, events)
            case AppState.PAUSE:
                zero_keys = tuple(False for _ in range(512))
                self.game.tick(0, zero_keys, mouse, [])
                report = self.pause_menu.tick(mouse, events)

        match report:
            case Event.QUIT_GAME:
                self.state = AppState.START
            case Event.START_GAME:
                self.state = AppState.PLAY
            case Event.TERMINATE:
                self.running = False
            case Event.PAUSE_GAME:
                self.state = AppState.PAUSE

        if (
            self.frame_stats_surface is None
            or frame_started_at - self.last_frame_stats_update_at
            >= self.FRAME_STATS_UPDATE_INTERVAL
        ):
            average_frame_time = sum(self.frame_times) / len(self.frame_times)
            average_fps = 1 / average_frame_time if average_frame_time else 0
            if self.frame_stats_surface is not None:
                self.renderer.invalidate_surface(self.frame_stats_surface)
            self.frame_stats_surface = self.font.render(
                f"FPS: {average_fps:.0f} | Frame: {frame_dt * 1000:.2f} ms",
                True,
                "orange",
            )
            self.last_frame_stats_update_at = frame_started_at

        self.renderer.draw_surface(self.frame_stats_surface, (10, 10))
        self.renderer.present()

    def terminate(self, exception=None):
        if exception:
            self.logger.error(exception)
        average_fps = (
            self.frame_count / self.total_frame_time
            if self.total_frame_time else 0
        )
        alive_seconds = perf_counter() - self.started_at
        alive_time = f"{alive_seconds // 60:.0f}m {alive_seconds % 60:04.1f}s"
        self.logger.close(
            f"Terminating application (alive: {alive_time}, average FPS: {average_fps:.1f})"
        )
        self.renderer.close()
        pygame.quit()

    def run(self):
        try:
            while self.running:
                events = pygame.event.get()
                keys = pygame.key.get_pressed()
                mouse = (pygame.mouse.get_pressed(),pygame.mouse.get_pos())
                for event in events:
                    if event.type == pygame.QUIT:
                        self.running = False
                self.tick(events, keys, mouse)
        except Exception as exception:
            self.terminate(exception)
            raise
        finally:
            if not self.logger.dmp.closed:
                self.terminate()
