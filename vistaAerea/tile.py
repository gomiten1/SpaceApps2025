import pygame
import random

TILE_TYPES = [
    "private", "hygiene", "waste", "exercise", "food",
    "maintenance", "science", "medical", "social",
    "logistics", "mission planning", "airlock"
]

# Colors assigned to each tile type, including mission planning with teal color
TYPE_COLORS = {
    "private": (255, 0, 0),       # red
    "hygiene": (0, 255, 255),     # cyan
    "waste": (105, 105, 105),     # dim gray
    "exercise": (0, 255, 0),      # green
    "food": (255, 165, 0),        # orange
    "maintenance": (128, 0, 128), # purple
    "science": (0, 0, 255),       # blue
    "medical": (255, 192, 203),   # pink
    "social": (255, 255, 0),      # yellow
    "logistics": (139, 69, 19),   # brown
    "mission planning": (0, 128, 128),  # teal
    "airlock": (192, 192, 192),   # silver
}

# Specific volume options per tile category
TYPE_VOLUMES = {
    "private": [10.76, 4.35, 4.8],
    "hygiene": [4.35, 2.34, 2.18],
    "waste": [2.36, 3.76],
    "exercise": [3.38, 6.12, 3.92],
    "food": [10.09, 4.35, 3.3],
    "maintenance": [4.35, 1.7],
    "science": [4.35, 1.7],
    "medical": [5.8, 3.4, 1.2],
    "social": [18.2, 10.09, 4.62],
    "logistics": [6, 4.35],
    "mission planning": [3.42, 10.09],
    "airlock": [4.62],
}

# Fixed limpieza values per category
TYPE_LIMPIEZA = {
    "private": 1,
    "hygiene": 0,
    "waste": 0,
    "exercise": 0,
    "food": 1,
    "maintenance": 0.5,
    "science": 1,
    "medical": 1,
    "social": 0,
    "logistics": 0,
    "mission planning": 0.5,
    "airlock": 0,
}

# Fixed permanencia values per category
TYPE_PERMANENCIA = {
    "private": 1,
    "hygiene": 0,
    "waste": 0,
    "exercise": 0,
    "food": 1,
    "maintenance": 0,
    "science": 1,
    "medical": 1,
    "social": 0,
    "logistics": 0,
    "mission planning": 0,
    "airlock": 0,
}

class TileBlock(pygame.sprite.Sprite):
    def __init__(self, gx, gy, width, height, tile_size, type_override=None, cost=0):
        super().__init__()
        self.gx = gx
        self.gy = gy
        self.width = width
        self.height = height
        self.tile_size = tile_size

        self.type = type_override if type_override else random.choice(TILE_TYPES)
        self.color = TYPE_COLORS.get(self.type, (255, 255, 255))  # default white

        w_px = width * tile_size
        h_px = height * tile_size
        self.image = pygame.Surface((w_px, h_px))
        self.image.fill(self.color)
        self.rect = self.image.get_rect(topleft=(gx * tile_size, gy * tile_size))

        self.volumen = random.choice(TYPE_VOLUMES.get(self.type, [1.0]))  # volume chosen from type options
        self.costo = cost  # Assigned cost from block size

        self.masa = random.uniform(1, 100)
        self.limpieza = TYPE_LIMPIEZA.get(self.type, 0)
        self.permanencia = TYPE_PERMANENCIA.get(self.type, 0)

        print(
            f"gx = {self.gx}, gy = {self.gy}, width = {self.width}, height = {self.height}, "
            f"type = {self.type}, masa = {self.masa:.2f}, volumen = {self.volumen:.2f}, "
            f"costo = {self.costo:.2f}, limpieza = {self.limpieza:.2f}, permanencia = {self.permanencia}, "
            f"color = {self.color}"
        )

    def covers(self, gx, gy):
        return (self.gx <= gx < self.gx + self.width) and (self.gy <= gy < self.gy + self.height)
