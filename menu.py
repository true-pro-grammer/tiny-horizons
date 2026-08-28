import pygame

from utils import Event

class StartMenu:
    
    def __init__(self, renderer, width, height, assets):
        self.renderer = renderer
        self.width = width
        self.height = height
    
        self.assets = assets

        self.play_button = pygame.Rect(0,0,200,75)
        self.play_button.center = (self.width//2, self.height//2)

        self.quit_button = pygame.Rect(0,0,200,75)
        self.quit_button.midtop = self.play_button.midbottom
        self.quit_button.y += 30

    def check(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.play_button.collidepoint(event.pos):
                    return Event.START_GAME
                elif self.quit_button.collidepoint(event.pos):
                    return Event.TERMINATE
    
    def tick(self, dt, mouse, events):
        report = self.check(events)

        self.renderer.clear(1.0,0.75,0.8,1.0)

        mouse_pos = mouse[1]

        play_button_colour = "yellow" if self.play_button.collidepoint(mouse_pos) else "orange"
        quit_button_colour = "pink" if self.quit_button.collidepoint(mouse_pos) else "purple"

        self.renderer.draw_rect(self.play_button, play_button_colour)
        self.renderer.draw_rect(self.quit_button, quit_button_colour)

        return report
