import pygame
import random
from config import CUBE_COLORS, CELL_SIZE, GRID_COLS, GRID_ROWS, SHADOW_COLOR, CUBE_HOVER_COLOR

import pygame
from astar import find_path
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
    
    def get_neighbors(self, pos):
        """Get valid neighboring positions"""
        x, y = pos
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # Down, Right, Up, Left
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < GRID_COLS and 0 <= new_y < GRID_ROWS:
                neighbors.append((new_x, new_y))
        return neighbors
    
    def calculate_path(self) -> list:
        """Calculate path using astar package"""
        start = (self.grid_x, self.grid_y)
        goal = self.destination
        
        # Find path using astar package
        path_nodes = find_path(
            start=start,
            goal=goal,
            neighbors_fnct=self.get_neighbors,
            heuristic_cost_estimate_fnct=lambda a, b: abs(b[0] - a[0]) + abs(b[1] - a[1]),
            distance_between_fnct=lambda a, b: 1.0
        )
        
        if not path_nodes:
            return []
        
        # Convert path nodes to movement instructions
        movements = []
        path_nodes = list(path_nodes)
        for i in range(len(path_nodes) - 1):
            current = path_nodes[i]
            next_pos = path_nodes[i + 1]
            dx = next_pos[0] - current[0]
            dy = next_pos[1] - current[1]
            movements.append((dx, dy))
            
        return movements
    
    def is_reached(self) -> bool:
        if self.path:
            return False
        return True
    
    def move(self):
        if self.path:
            dx, dy = self.path.pop(0)
        else:
            dx, dy = (0, 0)
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