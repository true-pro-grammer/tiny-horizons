import pygame
from enum import Enum, auto

from game import Game
from menu import StartMenu
from utils import Event
from logger import Logger

class AppState(Enum):
    START = auto()
    PLAY = auto()

class App:
    NAME = "Bloop's Saga"
    WIDTH = 1920
    HEIGHT = 1080

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption(self.NAME)
        self.state = AppState.START

        self.clock = pygame.time.Clock()
        self.logger = Logger()
        self.game = Game(self.screen, self.logger, self.WIDTH, self.HEIGHT)
        self.start_menu = StartMenu(self.screen, self.WIDTH, self.HEIGHT)
        self.running = True

    def tick(self, events, keys):
        dt = min(self.clock.tick(180)/1000,0.1)

        match self.state:
            case AppState.PLAY:
                report = self.game.tick(dt, keys)
            case AppState.START:
                report = self.start_menu.tick(dt, events)

        match report:
            case Event.QUIT:
                self.running = False
            case Event.START_GAME:
                self.state = AppState.PLAY
        
        pygame.display.flip()

    def run(self):
        try:
            while self.running:
                events = pygame.event.get()
                keys = pygame.key.get_pressed()
                for event in events:
                    if event.type == pygame.QUIT:
                        self.running = False
                self.tick(events, keys)
        finally:
            pygame.quit()