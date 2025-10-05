import pygame

class ToggleButton:
    def __init__(self, x, y, width, height, options, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.font = font
        self.current_index = 0
        self.bg_color = (70, 70, 70)
        self.hover_color = (100, 100, 255)
        self.text_color = (255, 255, 255)
        self.is_hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.current_index = (self.current_index + 1) % len(self.options)

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.bg_color
        pygame.draw.rect(surface, color, self.rect)
        text = self.font.render(self.options[self.current_index], True, self.text_color)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)

    def get_current_option(self):
        return self.options[self.current_index]
