import pygame
from typing import List
from config import WIDTH, HEIGHT, CUBE_COUNT, CELL_SIZE, GRID_COLS, GRID_ROWS, MOVE_INTERVAL, GRID_LINES, BACKGROUND
from cube import Cube

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