import pygame

class Block(pygame.sprite.Sprite):
    def __init__(self, pos, img=None):
        super().__init__()
        self.pos = pos
        if img is None:
            self.image = pygame.Surface((64, 32), pygame.SRCALPHA)
            self.image.fill((255, 255, 255, 0))
        else:
            self.image = img
        self.rect = self.image.get_rect(topleft=(0, 0))  # ← evita el AttributeError
        self._layer = sum(pos)

    def update(self, camera):
        x, y, z = camera.grid_to_iso(self.pos)
        self.rect.topleft = (x, y)


class Previsualization_Block(Block):
    def __init__(self, img=None, alpha=50):
        # crea copia segura de la imagen
        img_copy = img.copy() if img else None
        super().__init__([0, 0, 0], img_copy)

        # aplica transparencia inicial
        if self.image:
            self.image.set_alpha(alpha)
            # aplica filtro azul inicial
            self._apply_blue_tint(alpha)

    def _apply_blue_tint(self, alpha):
        """Aplica un filtro azul semitransparente al sprite."""
        if not self.image:
            return
        blue_tint = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
        blue_tint.fill((0, 0, 255, alpha))  # color azul RGBA
        # usa modo de mezcla aditiva
        self.image.blit(blue_tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    def _apply_red_tint(self, alpha):
        """Aplica un filtro azul semitransparente al sprite."""
        if not self.image:
            return
        blue_tint = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
        blue_tint.fill((255, 0, 0, alpha))  # color azul RGBA
        # usa modo de mezcla aditiva
        self.image.blit(blue_tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


    def update_position_block(self, player_position, camera):
        """Actualiza posición del bloque en coordenadas isométricas."""
        self.pos = player_position
        x, y, z = camera.grid_to_iso(player_position)
        self.rect.topleft = (x, y)

    def update_block_image(self, image, action, alpha=50):
        """Actualiza la imagen del bloque con filtro azul y transparencia."""
        # crea una copia independiente antes de modificar
        self.image = image.copy()

        # aplica tinte azul y transparencia
        if action == "remove_block":
            print("removeblock")
            self._apply_red_tint(alpha)
        else:
            self._apply_blue_tint(alpha)

        # ajusta el rect manteniendo la posición previa
        self.rect = self.image.get_rect(topleft=self.rect.topleft)