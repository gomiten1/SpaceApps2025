import pygame
from src.block import *
from src.camera import *

class Player():
    def __init__(self):
        # q (113) -> add, e (101) -> remove
        self._actions = {113: "add_block", 101: "remove_block"}
        self.action = None

        self.selected_object = None
        self.dimension_selected_object = None

        # Posiciones
        self.gridPosition = [0, 0, 0]   # (i,j,k)
        self.isoPosition  = [0, 0, 0]   # (x,y,z_visual)

        # Un solo layout para todo
        self.layout = pygame.sprite.LayeredUpdates()

        # Mapa lógico del mundo:
        # grid[(i,j,k)] = [ { "type": str, "sprite": Block }, ... ]
        # (lista = pila/overlay en ese mismo z)
        self.grid = {}

        self.camera = Camera()
        self.previsualization_block = Previsualization_Block()

        # Offset de capa por tipo (para ordenar visualmente en el mismo z)
        self.layer_offset = {
            "ground": -1000,            # Terreno al fondo
            "Habitat_Tile": 0,          # Piso
            "Habitat_LWall_Tile": 100,  # Paredes
            "Habitat_RWall_Tile": 100,
            "default": 50
        }

    # =========================================================
    # Helpers internos
    # =========================================================
    def _col_levels(self, i, j):
        """Regresa lista de k existentes en la columna (i,j)."""
        return [k for (x, y, k) in self.grid.keys() if x == i and y == j]

    def _top_k(self, i, j):
        """k más alto en (i,j) o None si vacío."""
        niveles = self._col_levels(i, j)
        return max(niveles) if niveles else None

    def _cell_items(self, i, j, k):
        """Lista (pila) de items en (i,j,k)."""
        return self.grid.get((i, j, k), [])

    def _calc_layer(self, i, j, k, tipo, idx_en_celda):
        """Capa de dibujo estable: i+j+k + offset(tipo) + pequeño offset por índice."""
        base = i + j + k
        off = self.layer_offset.get(tipo, self.layer_offset["default"])
        return base + off + idx_en_celda

    # =========================================================
    # Acciones
    # =========================================================
    def previsualize_action(self, key_pressed):
        if key_pressed not in self._actions:
            return
        self.action = self._actions[key_pressed]
        if self.selected_object:
            self.previsualization_block.update_block_image(
                self.selected_object["img"], self.action
            )

    def change_action(self):
        if not self.action:
            return
        if self.action == "add_block" and self.selected_object:
            self.add_block()
        elif self.action == "remove_block":
            self.remove_block()

    # =========================================================
    # Posición y previsualización
    # =========================================================
    def update_player_grid_position(self):
        """Actualiza gridPosition y coloca la previsualización
           (respeta overlay sobre Habitat_Tile)."""
        self.gridPosition = list(self.camera.iso_to_grid(self.isoPosition))
        i, j, _ = self.gridPosition

        topk = self._top_k(i, j)
        if topk is None:
            # Columna vacía: previsualiza en k derivado de iso/grid (normalmente 0)
            k_prev = self.gridPosition[2]
        else:
            # Por defecto, la primera libre arriba
            k_prev = topk + 1

            # Si estamos agregando y la cima es Habitat_Tile y el seleccionado NO es Habitat_Tile,
            # previsualiza en el MISMO k (overlay)
            if self.action == "add_block" and self.selected_object:
                cima_items = self._cell_items(i, j, topk)
                if cima_items:
                    cima_tipo = cima_items[-1]["type"]
                    sel_tipo  = self.selected_object.get("type")
                    if cima_tipo == "Habitat_Tile" and sel_tipo != "Habitat_Tile":
                        k_prev = topk

            # Si estamos removiendo, muestra en la cima
            if self.action == "remove_block":
                k_prev = topk

        self.previsualization_block.update_position_block((i, j, k_prev), self.camera)

    # =========================================================
    # Bloques (add/remove) — con pila por celda
    # =========================================================
    def add_block(self):
        i, j, _ = self.gridPosition
        sel_tipo = self.selected_object.get("type")

        topk = self._top_k(i, j)
        if topk is None:
            target_k = self.gridPosition[2]  # usa k convertido por la cámara (normalmente 0)
        else:
            # Regla: si la cima es Habitat_Tile y el nuevo NO es Habitat_Tile → mismo k (overlay)
            cima_items = self._cell_items(i, j, topk)
            cima_tipo  = cima_items[-1]["type"] if cima_items else None
            if cima_tipo == "Habitat_Tile" and sel_tipo != "Habitat_Tile":
                target_k = topk
            else:
                target_k = topk + 1

        # Prepara pila en la celda destino
        pila = self.grid.setdefault((i, j, target_k), [])

        # Índice dentro de la pila (para orden visual dentro del mismo z)
        idx = len(pila)

        # Crear sprite y agregar al layout con su capa
        sprite = Block((i, j, target_k), self.selected_object["img"])
        layer  = self._calc_layer(i, j, target_k, sel_tipo, idx)
        self.layout.add(sprite, layer=layer)

        # Registrar en grid
        pila.append({"type": sel_tipo, "sprite": sprite})

        # Actualizar previsualización a donde quedó realmente
        self.previsualization_block.update_position_block((i, j, target_k), self.camera)

    def remove_block(self):
        """Elimina el último elemento de la pila en el k más alto de (i,j)."""
        i, j, _ = self.gridPosition
        topk = self._top_k(i, j)
        if topk is None:
            return

        pila = self._cell_items(i, j, topk)
        if not pila:
            # Inconsistencia defensiva: no debería pasar
            del self.grid[(i, j, topk)]
            return

        # Sacar el último (overlay primero). Esto respeta tu expectativa de delete.
        item = pila.pop()
        sprite = item.get("sprite")
        if sprite:
            sprite.kill()

        # Si la pila quedó vacía, borra la celda
        if not pila:
            del self.grid[(i, j, topk)]

    # =========================================================
    # Terreno y actualización
    # =========================================================
    def generate_terrain(self, terrain):
        """Terreno puramente visual (no entra al grid)."""
        for i in range(5, 30):
            for j in range(-5, 20):
                # z=0 visual, pero capa MUY baja para no tapar nada
                sprite = Block((i, j, 0), terrain)
                layer  = i + j + self.layer_offset["ground"]
                self.layout.add(sprite, layer=layer)

    def update_blocks_position(self):
        """Actualiza todos los sprites con la cámara."""
        self.layout.update(self.camera)
