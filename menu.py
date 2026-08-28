import pygame

from utils import Event

class Menu:
    def __init__(self, renderer, width, height, assets, bg_colour):
        self.renderer = renderer
        self.assets = assets
        self.width = width
        self.height = height
        self.bg_colour = bg_colour

        self.buttons = []

    def new_button(self, size, *, position=None, relative_to=None, anchor="center", other_anchor="center", offset=(0,0), colour, hover_colour, event=None):
        if (position is None) == (relative_to is None):
            raise ValueError("Exactly one of position or relative_to must be provided")

        rect = pygame.Rect((0,0), size)

        if position is not None:
            setattr(rect, anchor, position)
        else:
            setattr(rect, anchor, getattr(relative_to, other_anchor))
            rect.x += offset[0]
            rect.y += offset[1]

        self.buttons.append({
            "rect": rect,
            "colour": colour,
            "hover_colour": hover_colour,
            "event": event,
        })

        return rect

    def poll(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in self.buttons:
                    if button["rect"].collidepoint(event.pos):
                        return button["event"]
        return None

    def tick(self, mouse, events):
        report = self.poll(events)

        self.renderer.begin_frame(self.bg_colour)

        mouse_pos = mouse[1]

        for button in self.buttons:
            colour = button["hover_colour"] if button["rect"].collidepoint(mouse_pos) else button["colour"]
            self.renderer.draw_rect(button["rect"], colour)

        return report

class StartMenu(Menu):
    def __init__(self, renderer, width, height, assets):
        super().__init__(renderer, width, height, assets, (173, 217, 230, 255))

        self.play_button = self.new_button(
            (200,75),
            position=(self.width//2, self.height//2),
            colour="orange",
            hover_colour="yellow",
            event=Event.START_GAME
        )

        self.quit_button = self.new_button(
            (200,75),
            relative_to=self.play_button,
            anchor="midtop",
            other_anchor="midbottom",
            offset=(0, 30),
            colour="purple",
            hover_colour="pink",
            event=Event.TERMINATE
        )