import pygame

from assets import Assets
from utils import Event

class StartMenu:
    
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
    
        self.assets = Assets()

        self.button = pygame.Rect(960,700,200,75)

    def check(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.button.collidepoint(event.pos):
                    return Event.START_GAME
    
    def tick(self, dt, events):
        report = self.check(events)

        self.screen.fill("gray")
        mouse_pos = pygame.mouse.get_pos()
        current_colour = "orange" if self.button.collidepoint(mouse_pos) else "yellow"
        pygame.draw.rect(self.screen, current_colour, self.button)

        return report
    
        #self.screen.blit()