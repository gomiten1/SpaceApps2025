import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (150, 150, 150)
LIGHT_GRAY = (230, 230, 230)
SCROLL_BTN_HEIGHT = 20

pygame.init()
font = pygame.font.SysFont(None, 24)

class TopBarLabel:
    def __init__(self, x, y, width, height, initial_text=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = initial_text

    def set_text(self, new_text):
        self.text = new_text

    def draw(self, surface):
        pygame.draw.rect(surface, DARK_GRAY, self.rect)
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

class TopBarButton:
    def __init__(self, x, y, width, height, text, options=None, cycle=False, max_visible=5):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.options = options or []
        self.dropdown_visible = False
        self.dropdown_rects = []
        self.selected_option = None
        self.cycle = cycle
        self.max_visible = max_visible
        self.scroll_index = 0
        self.scroll_up_rect = pygame.Rect(0, 0, width, SCROLL_BTN_HEIGHT)
        self.scroll_down_rect = pygame.Rect(0, 0, width, SCROLL_BTN_HEIGHT)

        if self.cycle and self.options:
            self.selected_option = self.options[0]

    def draw(self, surface):
        pygame.draw.rect(surface, GRAY, self.rect)
        display_text = self.text
        if self.cycle and self.selected_option is not None:
            display_text += f": {self.selected_option}"
        elif self.selected_option and not self.cycle:
            display_text += f": {self.selected_option}"
        text_surf = font.render(display_text, True, BLACK)
        surface.blit(text_surf, (self.rect.x + 10, self.rect.y + 5))

        if self.dropdown_visible and not self.cycle:
            x, y = self.rect.x, self.rect.y + self.rect.height
            width, option_height = self.rect.width, 30

            visible_count = min(self.max_visible, len(self.options))
            self.dropdown_rects = []
            for i in range(visible_count):
                idx = self.scroll_index + i
                if idx >= len(self.options):
                    break
                rect = pygame.Rect(x, y + i * option_height, width, option_height)
                self.dropdown_rects.append(rect)
                pygame.draw.rect(surface, LIGHT_GRAY, rect)
                option_text = font.render(self.options[idx], True, BLACK)
                surface.blit(option_text, (rect.x + 5, rect.y + 5))

            needs_scroll = len(self.options) > self.max_visible
            if needs_scroll:
                self.scroll_up_rect.x = x
                self.scroll_up_rect.y = y - SCROLL_BTN_HEIGHT
                pygame.draw.rect(surface, DARK_GRAY if self.scroll_index > 0 else GRAY, self.scroll_up_rect)
                up_text = font.render('▲', True, BLACK)
                surface.blit(up_text, (self.scroll_up_rect.x + width // 2 - up_text.get_width() // 2,
                                       self.scroll_up_rect.y + 2))

                self.scroll_down_rect.x = x
                self.scroll_down_rect.y = y + visible_count * option_height
                pygame.draw.rect(surface, DARK_GRAY if self.scroll_index + visible_count < len(self.options) else GRAY,
                                 self.scroll_down_rect)
                down_text = font.render('▼', True, BLACK)
                surface.blit(down_text, (self.scroll_down_rect.x + width // 2 - down_text.get_width() // 2,
                                         self.scroll_down_rect.y + 2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.cycle:
                    if self.options:
                        current_index = self.options.index(self.selected_option)
                        next_index = (current_index + 1) % len(self.options)
                        self.selected_option = self.options[next_index]
                        print(f'{self.text} changed to: {self.selected_option}')
                else:
                    self.dropdown_visible = not self.dropdown_visible
                return True
            elif self.dropdown_visible and not self.cycle:
                if self.scroll_up_rect.collidepoint(event.pos) and self.scroll_index > 0:
                    self.scroll_index -= 1
                    return True
                if self.scroll_down_rect.collidepoint(event.pos) and \
                        self.scroll_index + self.max_visible < len(self.options):
                    self.scroll_index += 1
                    return True

                for i, rect in enumerate(self.dropdown_rects):
                    if rect.collidepoint(event.pos):
                        self.selected_option = self.options[self.scroll_index + i]
                        print(f'Selected: {self.selected_option}')
                        self.dropdown_visible = False
                        self.scroll_index = 0
                        return True
                self.dropdown_visible = False
                self.scroll_index = 0

        elif event.type == pygame.MOUSEWHEEL and self.dropdown_visible and not self.cycle:
            if event.y > 0 and self.scroll_index > 0:
                self.scroll_index -= 1
                return True
            elif event.y < 0 and (self.scroll_index + self.max_visible) < len(self.options):
                self.scroll_index += 1
                return True

        return False

class TopBar:
    def __init__(self, width, height, buttons, label):
        self.rect = pygame.Rect(0, 0, width, height)
        self.buttons = buttons
        self.label = label

    def draw(self, surface):
        pygame.draw.rect(surface, DARK_GRAY, self.rect)
        for button in self.buttons:
            button.draw(surface)
        self.label.draw(surface)

    def handle_event(self, event):
        for button in self.buttons:
            if button.handle_event(event):
                break
