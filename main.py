import pygame
import random
import math
from typing import List, Tuple, Optional

# Constants
GRID_COLS = 10
GRID_ROWS = 10
CELL_SIZE = 60
WIDTH, HEIGHT = GRID_COLS * CELL_SIZE, GRID_ROWS * CELL_SIZE
CUBE_COUNT = 20
MOVE_INTERVAL = 1000  # Time between moves in milliseconds (1 second)

# Dark theme colors
BACKGROUND = (18, 18, 18)
GRID_LINES = (45, 45, 45)
CUBE_COLORS = [
    (88, 101, 242),    # Discord Blue
    (114, 137, 218),   # Light Discord Blue
    (145, 170, 242),   # Lighter Blue
]
CUBE_HOVER_COLOR = (255, 215, 0)
SHADOW_COLOR = (0, 0, 0, 50)

class Cube:
    def __init__(self, x: int, y: int, size: int):
        self.rect = pygame.Rect(x + 5, y + 5, size - 10, size - 10)
        self.color = random.choice(CUBE_COLORS)
        self.hover = False
        self.grid_x = x // CELL_SIZE
        self.grid_y = y // CELL_SIZE

    def move_random(self):
        # Get possible directions (up, right, down, left)
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        valid_moves = []
        
        for dx, dy in directions:
            new_x = self.grid_x + dx
            new_y = self.grid_y + dy
            if 0 <= new_x < GRID_COLS and 0 <= new_y < GRID_ROWS:
                valid_moves.append((dx, dy))
        
        if valid_moves:
            dx, dy = random.choice(valid_moves)
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

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("IEA")
        self.clock = pygame.time.Clock()
        self.cubes = self.create_cubes()
        self.selected_cube = None
        self.last_move_time = pygame.time.get_ticks()

    def create_cubes(self) -> List[Cube]:
        cubes = []
        for i in range(CUBE_COUNT):
            x = (i % GRID_COLS) * CELL_SIZE
            y = (GRID_ROWS - 1 - (i // GRID_COLS)) * CELL_SIZE
            cubes.append(Cube(x, y, CELL_SIZE))
        return cubes

    def move_all_cubes(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time >= MOVE_INTERVAL:
            for cube in self.cubes:
                cube.move_random()
            self.last_move_time = current_time

    def draw_grid(self):
        # Solid dark background
        self.screen.fill(BACKGROUND)

        # Grid lines
        for i in range(GRID_COLS + 1):
            pygame.draw.line(self.screen, GRID_LINES, 
                           (i * CELL_SIZE, 0), (i * CELL_SIZE, HEIGHT))
        for i in range(GRID_ROWS + 1):
            pygame.draw.line(self.screen, GRID_LINES,
                           (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    for cube in self.cubes:
                        if cube.rect.collidepoint(mouse_pos):
                            self.selected_cube = cube
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.selected_cube = None
                elif event.type == pygame.MOUSEMOTION:
                    mouse_pos = pygame.mouse.get_pos()
                    for cube in self.cubes:
                        cube.hover = cube.rect.collidepoint(mouse_pos)
                    if self.selected_cube:
                        grid_x = (mouse_pos[0] - CELL_SIZE//2) // CELL_SIZE
                        grid_y = (mouse_pos[1] - CELL_SIZE//2) // CELL_SIZE
                        if 0 <= grid_x < GRID_COLS and 0 <= grid_y < GRID_ROWS:
                            self.selected_cube.grid_x = grid_x
                            self.selected_cube.grid_y = grid_y
                            self.selected_cube.rect.x = (grid_x * CELL_SIZE) + 5
                            self.selected_cube.rect.y = (grid_y * CELL_SIZE) + 5

            # Move all cubes periodically
            self.move_all_cubes()

            self.draw_grid()
            for cube in self.cubes:
                cube.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()