import pygame
from tile import TileBlock

GRAY = (180, 180, 180)

class WorldGeneration:
    def __init__(self, screen_width=800, screen_height=600, topbar_height=40, grid_size=25):
        self._screen_width = screen_width
        self._screen_height = screen_height
        self.topbar_height = topbar_height
        self.grid_size = grid_size

        available_height = self._screen_height - self.topbar_height
        tile_size_vert = available_height / self.grid_size
        tile_size_horz = self._screen_width / self.grid_size
        self._tile_size = int(min(tile_size_vert, tile_size_horz))

        self.tile_blocks = []

    def check_overlap(self, gx, gy, width, height):
        for block in self.tile_blocks:
            if (gx + width <= block.gx or gx >= block.gx + block.width or
                gy + height <= block.gy or gy >= block.gy + block.height):
                continue
            else:
                return True
        return False

    def add_tile_block(self, gx, gy, width, height, type_override=None, cost=0):
        if self.check_overlap(gx, gy, width, height):
            print("Cannot place block: Overlaps existing block")
            return False
        block = TileBlock(gx, gy, width, height, self._tile_size, type_override, cost)
        self.tile_blocks.append(block)
        return True

    def remove_tile_at(self, gx, gy):
        for block in self.tile_blocks:
            if block.covers(gx, gy):
                self.tile_blocks.remove(block)
                break

    def get_block_at(self, gx, gy):
        for block in self.tile_blocks:
            if block.covers(gx, gy):
                return block
        return None

    def draw_grid(self, surface, camera, topbar_height):
        tile_size = self._tile_size
        grid_pixel_width = tile_size * self.grid_size
        x_offset = (self._screen_width - grid_pixel_width) // 2  # Center horizontally

        for gx in range(self.grid_size):
            for gy in range(self.grid_size):
                wx = gx * tile_size + x_offset
                wy = gy * tile_size + topbar_height
                sx, sy = camera.transform_coordinate((wx, wy))
                rect = pygame.Rect(sx, sy, tile_size, tile_size)
                pygame.draw.rect(surface, GRAY, rect, 1)

    def draw_tiles(self, surface, camera, topbar_height):
        tile_size = self._tile_size
        grid_pixel_width = tile_size * self.grid_size
        x_offset = (self._screen_width - grid_pixel_width) // 2  # Center horizontally

        for block in self.tile_blocks:
            wx = block.gx * tile_size + x_offset
            wy = block.gy * tile_size + topbar_height
            sx, sy = camera.transform_coordinate((wx, wy))
            block.rect.topleft = (sx, sy)
            surface.blit(block.image, block.rect)

    @property
    def tile_size(self):
        return self._tile_size

    @property
    def screen_size(self):
        return (self._screen_width, self._screen_height)
