import pygame
from src.player import *

# ============================
# CONFIGURACIÓN INICIAL
# ============================
HEIGHT, WIDTH, FPS = 800, 800, 60
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mars Habitat Builder")

# ============================
# IMÁGENES
# ============================
GROUND  = pygame.image.load("assets/img/MarsTiles.png").convert_alpha()
HABITAT_TILE = pygame.image.load("assets/img/HabitatTile.png").convert_alpha()
HABITAT_LWALL = pygame.image.load("assets/img/HabitatWallTile.png").convert_alpha()
HABITAT_RWALL = pygame.image.load("assets/img/HabitatWallRightTile.png").convert_alpha()
TREADMILL = pygame.image.load("assets/img/TreadMill.png").convert_alpha()
TABLE = pygame.image.load("assets/img/TableTile.png").convert_alpha()
BED = pygame.image.load("assets/img/bedTiles.png").convert_alpha()
WC = pygame.image.load("assets/img/WCTile.png").convert_alpha()
# ============================
# OBJETOS SELECCIONABLES
# ============================
sel = {
    1: {"img": HABITAT_TILE, "type": "Habitat_Tile"},
    2: {"img": HABITAT_LWALL, "type": "Habitat_LWall_Tile"},
    3: {"img": HABITAT_RWALL, "type": "Habitat_RWall_Tile"},
    4: {"img": TREADMILL, "type": "TreadMill"},
    5: {"img": TABLE, "type": "Table"},
    6: {"img": BED, "type": "bead"},
    7: {"img": WC, "type": "wc"}

}

# ============================
# JUGADOR Y ESCENA
# ============================
player = Player()
generate_terrain = True
running = True
selected_tile = 1
selected_key = 0

# ============================
# BUCLE PRINCIPAL
# ============================
while running:
    mx, my = pygame.mouse.get_pos()
    player.isoPosition = (mx, my, 0)
    player.update_player_grid_position()
    events = pygame.event.get()

    # Generar el terreno solo una vez
    if generate_terrain:
        generate_terrain = False
        player.generate_terrain(GROUND)

    # --- EVENTOS ---
    for e in events:
        if e.type == pygame.QUIT:
            running = False

        elif e.type == pygame.KEYDOWN:
            # Selección numérica
            if pygame.K_0 <= e.key <= pygame.K_9:
                numero = e.key - pygame.K_0
                if numero in sel:
                    player.selected_object = sel[numero]
                    selected_tile = numero
                    print(f"Tile seleccionado: {selected_tile}")
            else:
                selected_key = e.key
                if player.selected_object:
                    player.previsualize_action(selected_key)

        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            # Click izquierdo → agregar o quitar
            player.change_action()

    # --- ACTUALIZACIÓN ---
    player.camera.handle_input(events)
    player.update_blocks_position()

    # --- RENDER ---
    screen.fill((15, 15, 15))
    player.layout.draw(screen)
    screen.blit(player.previsualization_block.image, player.previsualization_block.rect)

    pygame.display.flip()
    clock.tick(FPS)
