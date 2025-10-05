import pygame

BLUE = (50, 100, 200)

class Player:
    def __init__(self, x, y, tile_size=32):
        self.x = x
        self.y = y
        self.tile_size = tile_size
        self.rect = pygame.Rect(x, y, tile_size, tile_size)
        self.color = BLUE
        self.speed = 8

        # Assuming a simple camera with x,y offsets for panning
        self.camera = Camera()

        # Current action: "add_tile" or "remove_tile"
        self.action = "add_tile"

    def update_position(self, keys):
        if keys[pygame.K_LEFT]:
            self.camera.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.camera.x += self.speed
        if keys[pygame.K_UP]:
            self.camera.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.camera.y += self.speed

    def draw(self, surface):
        # Comment out or remove the blue square drawing below:
        # center_x = surface.get_width() // 2
        # center_y = surface.get_height() // 2
        # rect = pygame.Rect(center_x - self.tile_size//2, center_y - self.tile_size//2, self.tile_size, self.tile_size)
        # pygame.draw.rect(surface, self.color, rect)
        pass  # No drawing for player

    def execute_action(self, world, grid_pos, mouse_button):
        gx, gy = grid_pos
        if mouse_button == 1:  # Left click
            if self.action == "add_tile":
                world.add_tile(gx, gy)
            elif self.action == "remove_tile":
                world.remove_tile(gx, gy)


class Camera:
    def __init__(self):
        # Camera position in pixels, initial at 0,0
        self.x = 0
        self.y = 0

    def transform_coordinate(self, pos):
        # Adjust world coordinate to screen coordinate by subtracting camera offset
        wx, wy = pos
        return wx - self.x, wy - self.y
