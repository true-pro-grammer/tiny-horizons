import pygame
from enum import Enum, auto

from game import Game
from menu import StartMenu
from utils import Event
from logger import Logger
from assets import Assets

class AppState(Enum):
    START = auto()
    PLAY = auto()

class App:
    NAME = "Bloop's Saga"
    WIDTH = 1920
    HEIGHT = 1080

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption(self.NAME)
        self.state = AppState.START

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 30)
        self.logger = Logger()
        self.assets = Assets()
        self.game = Game(self.screen, self.logger, self.WIDTH, self.HEIGHT, self.assets)
        self.start_menu = StartMenu(self.screen, self.WIDTH, self.HEIGHT)
        self.running = True

    def tick(self, events, keys):
        dt = min(self.clock.tick()/1000,0.1)

        match self.state:
            case AppState.PLAY:
                report = self.game.tick(dt, keys, events)
            case AppState.START:
                report = self.start_menu.tick(dt, events)

        match report:
            case Event.QUIT_GAME:
                self.state = AppState.START
            case Event.START_GAME:
                self.state = AppState.PLAY
            case Event.TERMINATE:
                self.running = False

        fps = self.font.render(f"FPS: {self.clock.get_fps():.1f}", True, "orange")
        self.screen.blit(fps, (10, 10))
        pygame.display.flip()

    def terminate(self, exception=None):
        self.logger.info("Terminating application")
        if exception:
            self.logger.error(exception)
        self.logger.close()
        pygame.quit()

    def run(self):
        try:
            while self.running:
                events = pygame.event.get()
                keys = pygame.key.get_pressed()
                for event in events:
                    if event.type == pygame.QUIT:
                        self.running = False
                self.tick(events, keys)
        except Exception as exception:
            self.terminate(exception)
            raise
        finally:
            if not self.logger.dmp.closed:
                self.terminate()