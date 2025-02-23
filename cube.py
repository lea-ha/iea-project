import pygame
import random
from config import CUBE_COLORS, CELL_SIZE, GRID_COLS, GRID_ROWS, SHADOW_COLOR, CUBE_HOVER_COLOR

class Cube:

    def __init__(self, x: int, y: int, size: int, destination: tuple):
        self.rect = pygame.Rect(x + 5, y + 5, size - 10, size - 10)
        self.color = CUBE_COLORS[0]
        self.hover = False
        self.grid_x = x // CELL_SIZE
        self.grid_y = y // CELL_SIZE
        self.destination = destination
        self.path = self.calculate_path()
    
    def calculate_path(self) -> list[tuple]:
        path = []
        current_x, current_y = self.grid_x, self.grid_y
        dest_x, dest_y = self.destination

        while (current_y != dest_y):

            if current_y < dest_y:
                current_y += 1
                path.append((0,1)) # Go down
            elif current_y > dest_y:
                current_y -= 1
                path.append((0,-1)) # Go up

        while (current_x != dest_x):

            if current_x < dest_x:
                current_x += 1
                path.append((1,0)) # Go right
            elif current_x > dest_x:
                current_x -= 1
                path.append((-1,0)) # Go left
        
        return path
    
    def is_reached(self) -> bool:
        if self.path:
            return False
        return True
    
    def move(self):
        if self.path:
            dx, dy = self.path.pop(0)
        else:
            dx, dy = (0,0)
        new_x = self.grid_x + dx
        new_y = self.grid_y + dy
        if 0 <= new_x < GRID_COLS and 0 <= new_y < GRID_ROWS:
            self.grid_x += dx
            self.grid_y += dy
            self.rect.x = (self.grid_x * CELL_SIZE) + 5
            self.rect.y = (self.grid_y * CELL_SIZE) + 5

    def draw(self, screen: pygame.Surface):
        # Shadow
        shadow_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, SHADOW_COLOR, shadow_surface.get_rect(), border_radius=10)
        screen.blit(shadow_surface, (self.rect.x + 4, self.rect.y + 4))
        
        # Cube with gradient
        color = CUBE_HOVER_COLOR if self.hover else self.color
        gradient_rect = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        for i in range(self.rect.height):
            alpha = 255 - (i * 100 // self.rect.height)
            highlight_color = (
                min(255, color[0] + 50),
                min(255, color[1] + 50),
                min(255, color[2] + 50),
                alpha
            )
            pygame.draw.line(gradient_rect, highlight_color, 
                           (0, i), (self.rect.width, i))
        
        base_rect = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(base_rect, color, base_rect.get_rect(), border_radius=10)
        base_rect.blit(gradient_rect, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(base_rect, self.rect)