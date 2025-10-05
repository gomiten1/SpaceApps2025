import pygame

class DropdownMenu:
    def __init__(self, x, y, width, height, options, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.font = font
        self.selected_index = 0
        self.is_open = False
        self.scroll_offset = 0
        self.option_height = 30
        self.max_visible_options = 5
        self.bg_color = (70, 70, 70)
        self.highlight_color = (100, 100, 255)
        self.text_color = (255, 255, 255)

    def handle_event(self, event):
        # Only react to left mouse button clicks (button 1)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.is_open:
                for i in range(self.max_visible_options):
                    option_y = self.rect.y + (i * self.option_height)
                    option_rect = pygame.Rect(self.rect.x, option_y, self.rect.width, self.option_height)
                    if i + self.scroll_offset < len(self.options) and option_rect.collidepoint(mx, my):
                        self.selected_index = i + self.scroll_offset
                        self.is_open = False
                        break
                else:
                    if not self.rect.collidepoint(mx, my):
                        self.is_open = False
            else:
                if self.rect.collidepoint(mx, my):
                    self.is_open = True

        elif event.type == pygame.MOUSEWHEEL and self.is_open:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            open_menu_height = self.option_height * min(self.max_visible_options, len(self.options))
            menu_area_rect = pygame.Rect(
                self.rect.x,
                self.rect.y,
                self.rect.width,
                self.rect.height + open_menu_height
            )
            if menu_area_rect.collidepoint(mouse_x, mouse_y):
                max_scroll = max(0, len(self.options) - self.max_visible_options)
                self.scroll_offset = max(0, min(self.scroll_offset - event.y, max_scroll))

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect)
        selected_text = self.font.render(self.options[self.selected_index], True, self.text_color)
        surface.blit(selected_text, (self.rect.x + 5, self.rect.y + 5))

        if self.is_open:
            menu_height = self.option_height * min(self.max_visible_options, len(self.options))
            menu_rect = pygame.Rect(self.rect.x, self.rect.y + self.rect.height, self.rect.width, menu_height)
            pygame.draw.rect(surface, self.bg_color, menu_rect)

            for i in range(self.max_visible_options):
                option_index = i + self.scroll_offset
                if option_index >= len(self.options):
                    break
                option_rect = pygame.Rect(self.rect.x, self.rect.y + self.rect.height + i * self.option_height, self.rect.width, self.option_height)
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if option_rect.collidepoint(mouse_x, mouse_y):
                    pygame.draw.rect(surface, self.highlight_color, option_rect)
                option_text = self.font.render(self.options[option_index], True, self.text_color)
                surface.blit(option_text, (option_rect.x + 5, option_rect.y + 5))

    def get_selected_option(self):
        return self.options[self.selected_index]
