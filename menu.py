import pygame

from utils import Event

class StartMenu:
    
    def __init__(self, renderer, width, height, assets):
        self.renderer = renderer
        self.width = width
        self.height = height
    
        self.assets = assets

        self.button = pygame.Rect(960,700,200,75)

    def check(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.button.collidepoint(event.pos):
                    return Event.START_GAME
    
    def tick(self, dt, events):
        report = self.check(events)

        self.renderer.clear(1.0,0.75,0.8,1.0)
        mouse_pos = pygame.mouse.get_pos()
        current_colour = "orange" if self.button.collidepoint(mouse_pos) else "yellow"
        self.renderer.draw_rect(self.button, current_colour)

        return report
