import pygame
import math

class RotateButton:
    def __init__(self, x, y, size, font):
        self.rect = pygame.Rect(x, y, size, size)
        self.angle = 0  # Current rotation angle in degrees
        self.bg_color = (70, 70, 70)
        self.hover_color = (100, 100, 255)
        self.arrow_color = (255, 255, 255)
        self.is_hovered = False
        self.font = font

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.angle = (self.angle + 90) % 360

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.bg_color
        pygame.draw.rect(surface, color, self.rect)

        # Draw a simple arrow pointing upwards rotated by self.angle
        center = self.rect.center
        size = self.rect.width // 2

        # Calculate arrow points before rotation (pointing up)
        points = [
            (center[0], center[1] - size // 2),  # Tip of arrow
            (center[0] - size // 3, center[1] + size // 3),
            (center[0], center[1] + size // 6),
            (center[0] + size // 3, center[1] + size // 3)
        ]

        # Rotate points around center
        rotated_points = [self._rotate_point(p, center, math.radians(self.angle)) for p in points]

        pygame.draw.polygon(surface, self.arrow_color, rotated_points)

    def _rotate_point(self, point, origin, angle_rad):
        ox, oy = origin
        px, py = point

        qx = ox + math.cos(angle_rad) * (px - ox) - math.sin(angle_rad) * (py - oy)
        qy = oy + math.sin(angle_rad) * (px - ox) + math.cos(angle_rad) * (py - oy)
        return (qx, qy)

    def get_angle(self):
        return self.angle
