import pygame
import math
class Camera:
    def __init__(self):
        self.offset = pygame.Vector2(0, 0)
        self.speed = 16
        self.dragging = False
        self._dragStart = None
       
       #Varibles que dependen del bloque unitario
        self._anchor = (0, 0)
        #Longitud en pixeles del bloque unitario
        self._isoWidth = 64
        #Altura en pixeles del bloque unitario 
        self._isoHeight = 32
        self._baseOrigin =  (0, 0)
        self._eps = 1e-6
        self.z_scale = 1

    def handle_input(self, events):
        keys = pygame.key.get_pressed()


        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  self.offset.x += self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.offset.x -= self.speed
        if keys[pygame.K_w] or keys[pygame.K_UP]:    self.offset.y += self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  self.offset.y -= self.speed

        for e in events:  # drag con botón medio (opcional)
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 2:
                self.dragging, self._drag_start = True, pygame.Vector2(e.pos)
            elif e.type == pygame.MOUSEBUTTONUP and e.button == 2:
                self.dragging = False
            elif e.type == pygame.MOUSEMOTION and self.dragging:
                m = pygame.Vector2(e.pos)
                delta = m - self._drag_start
                self.offset += delta     # arrastras la vista
                self._drag_start = m

  # Transforma coordenadas del grid (i, j, k) a vista isométrica (x, y, z)
    def grid_to_iso(self, pos):
        ox, oy = self._baseOrigin
        ax, ay = self._anchor

        # Factor de escala de altura (ajústalo entre 0.25 y 0.6 según se vea mejor)
 

        x = ox + self.offset.x + (self._isoWidth // 2) * (pos[0] - pos[1]) + ax
        y = oy + self.offset.y + (self._isoHeight // 2) * (pos[0] + pos[1]) - pos[2] * self._isoHeight *  self.z_scale  + ay
        z = pos[2] *  self.z_scale   # opcional, solo si manejas un z 3D adicional (profundidad)

        return x, y, z


    # Transforma coordenadas isométricas (x, y, z) de vuelta a grid (i, j, k)
    def iso_to_grid(self, pos):
        ox, oy = self._baseOrigin
        ax, ay = self._anchor


        X = pos[0] - ox - self.offset.x - ax
        Y = pos[1] - oy - self.offset.y - ay

        u = X / (self._isoWidth / 2)
        v = Y / (self._isoHeight / 2)

        i_f = 0.5 * (u + v)
        j_f = 0.5 * (v - u)

        i = math.floor(i_f + self._eps)
        j = math.floor(j_f + self._eps)
        k = math.floor((pos[2] / ( self.z_scale )) + self._eps)

        return i, j, k

