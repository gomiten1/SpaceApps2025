import pygame
import sys
import json

from player import Player
from world import WorldGeneration
from topbar import TopBar

DARK_GRAY = (40, 40, 40)

def main():
    pygame.init()
    SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tile Placement with Import/Export")
    clock = pygame.time.Clock()

    topbar = TopBar(SCREEN_WIDTH)
    topbar_height = topbar.height

    size_map = {
        "1x1": (1, 1),
        "2x2": (2, 2),
        "3x1": (3, 1),
        "4x4": (4, 4)
    }

    cost_map = {
        (1, 1): 5,
        (2, 2): 10,
        (3, 1): 7,
        (4, 4): 20
    }

    money = 200

    world = WorldGeneration(screen_width=SCREEN_WIDTH,
                            screen_height=SCREEN_HEIGHT,
                            topbar_height=topbar_height,
                            grid_size=25)
    player = Player(0, 0, tile_size=world.tile_size)

    topbar.toggle_button.current_index = topbar.toggle_button.options.index("4x4")

    placed_tiles_values = []

    def get_ui_rects():
        rects = [
            topbar.draw_remove_toggle.rect,
            topbar.type_dropdown.rect,
            topbar.toggle_button.rect,
            topbar.export_button.rect,
            topbar.import_button.rect
        ]
        if topbar.type_dropdown.is_open:
            for i in range(len(topbar.type_dropdown.options)):
                rect = pygame.Rect(
                    topbar.type_dropdown.rect.x,
                    topbar.type_dropdown.rect.y + topbar.type_dropdown.rect.height * (i + 1),
                    topbar.type_dropdown.rect.width,
                    topbar.type_dropdown.rect.height,
                )
                rects.append(rect)
        if topbar.toggle_button.is_open:
            for i in range(len(topbar.toggle_button.options)):
                rect = pygame.Rect(
                    topbar.toggle_button.rect.x,
                    topbar.toggle_button.rect.y + topbar.toggle_button.rect.height * (i + 1),
                    topbar.toggle_button.rect.width,
                    topbar.toggle_button.rect.height,
                )
                rects.append(rect)
        return rects

    def click_on_ui(mouse_pos):
        for rect in get_ui_rects():
            if rect.collidepoint(mouse_pos):
                return True
        return False

    def is_menu_open():
        return topbar.type_dropdown.is_open or topbar.toggle_button.is_open

    running = True
    while running:
        mouse_grid_pos = None
        export_clicked = False
        import_clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            topbar.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if topbar.export_button.rect.collidepoint(mouse_pos):
                    export_clicked = True
                    continue
                elif topbar.import_button.rect.collidepoint(mouse_pos):
                    import_clicked = True
                    continue
                if is_menu_open() or click_on_ui(mouse_pos):
                    pass
                else:
                    if mouse_pos[1] > topbar_height:
                        tile_size = world.tile_size
                        grid_pixel_width = tile_size * world.grid_size
                        x_offset = (SCREEN_WIDTH - grid_pixel_width) // 2
                        wx = mouse_pos[0] + player.camera.x - x_offset
                        wy = mouse_pos[1] - topbar_height + player.camera.y
                        grid_x = int(wx // tile_size)
                        grid_y = int(wy // tile_size)
                        if 0 <= grid_x < world.grid_size and 0 <= grid_y < world.grid_size:
                            current_action = topbar.draw_remove_toggle.get_current_option().lower() + "_tile"
                            player.action = current_action
                            selected_shape = topbar.toggle_button.get_current_option()
                            current_shape = size_map.get(selected_shape, (1, 1))
                            width, height = current_shape
                            cost = cost_map.get(current_shape, 5)
                            selected_type = topbar.type_dropdown.get_current_option()
                            if player.action == "draw_tile":
                                if money >= cost:
                                    placed = world.add_tile_block(grid_x, grid_y, width, height, selected_type, cost)
                                    if placed:
                                        money -= cost
                                    else:
                                        print("Tile placement failed: overlapping tiles")
                                else:
                                    print("Not enough money!")
                            elif player.action == "remove_tile":
                                block = world.get_block_at(grid_x, grid_y)
                                if block:
                                    world.remove_tile_at(grid_x, grid_y)
                                    money += cost_map.get((block.width, block.height), 5)

        if export_clicked:
            placed_tiles_values.clear()
            for block in world.tile_blocks:
                cell = {
                    "x": block.gx,
                    "y": block.gy,
                    "type": block.type.upper(),
                    "props": {
                        "masa": getattr(block, "masa", 0.0),
                        "volumen": getattr(block, "volumen", 0.0),
                        "costo": getattr(block, "costo", 0.0),
                        "limpieza": getattr(block, "limpieza", 1.0),
                        "permanencia": getattr(block, "permanencia", 1)
                    }
                }
                placed_tiles_values.append(cell)

            # Add the "contexto" outside of "cells"
            contexto = {
                "contexto": {
                    "cantidadTripulacion": 1,
                    "materialEstructural": "compuesto",
                    "resistenciaRadiacion": 8
                }
            }
            # Compose the overall data with "cells" and "contexto" as separate top-level lists
            data = {
                "cells": placed_tiles_values,
                "contexto": [contexto["contexto"]]  # Wrap in list to keep structure consistent
            }

            with open("exported_tiles.json", "w") as f:
                json.dump(data, f, indent=2)

            print("Exported tiles saved to exported_tiles.json")

        if import_clicked:
            try:
                with open("imported_tiles.json", "r") as f:
                    data = json.load(f)
                world.tile_blocks.clear()
                for cell in data.get("cells", []):
                    gx = cell.get("x", 0)
                    gy = cell.get("y", 0)
                    tile_type = cell.get("type", "PRIVATE").lower()
                    props = cell.get("props", {})
                    width, height = 1, 1
                    world.add_tile_block(gx, gy, width, height, tile_type, cost=0)
                    block = world.get_block_at(gx, gy)
                    if block:
                        block.masa = props.get("masa", 0.0)
                        block.volumen = props.get("volumen", 0.0)
                        block.costo = props.get("costo", 0.0)
                        block.limpieza = props.get("limpieza", 1.0)
                        block.permanencia = props.get("permanencia", 1)
                print("Imported tiles loaded from imported_tiles.json")
            except Exception as e:
                print("Error importing tiles:", e)

        selected_shape = topbar.toggle_button.get_current_option()
        current_shape = size_map.get(selected_shape, (1, 1))
        keys = pygame.key.get_pressed()
        player.update_position(keys)

        mx, my = pygame.mouse.get_pos()
        if my > topbar_height:
            tile_size = world.tile_size
            grid_pixel_width = tile_size * world.grid_size
            x_offset = (SCREEN_WIDTH - grid_pixel_width) // 2
            wx = mx + player.camera.x - x_offset
            wy = my - topbar_height + player.camera.y
            grid_x = int(wx // tile_size)
            grid_y = int(wy // tile_size)
            if 0 <= grid_x < world.grid_size and 0 <= grid_y < world.grid_size:
                mouse_grid_pos = (grid_x, grid_y)

        screen.fill(DARK_GRAY)
        world.draw_grid(screen, player.camera, topbar_height)
        world.draw_tiles(screen, player.camera, topbar_height)
        player.draw(screen)

        if mouse_grid_pos:
            width, height = current_shape
            px = mouse_grid_pos[0] * world.tile_size
            py = mouse_grid_pos[1] * world.tile_size
            sx, sy = player.camera.transform_coordinate((px + x_offset, py + topbar_height))
            hover_rect = pygame.Rect(sx, sy, width * world.tile_size, height * world.tile_size)
            hover_surface = pygame.Surface(hover_rect.size, pygame.SRCALPHA)
            hover_surface.fill((255, 255, 0, 100))
            screen.blit(hover_surface, hover_rect.topleft)

        topbar.draw(screen, money)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
