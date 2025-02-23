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
        self.cubes = self.create_cube()
        self.selected_cube = None
        self.last_move_time = pygame.time.get_ticks()
        
    def create_cube(self) -> List[Cube]:
        cubes = []
        my_cube = Cube(0, 540, CELL_SIZE, (4,2))  #destination should be changed later to be passed as a parameter
        # my_cube = Cube(0, 540, CELL_SIZE, (480 // CELL_SIZE, 60 // CELL_SIZE))
        cubes.append(my_cube)
        return cubes
    
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
            
        if self.cubes:
            for cube in self.cubes:  # Highlight all cubes' destinations
                destination_x, destination_y = cube.destination  
                destination_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                destination_surface.fill((0, 255, 0, 100))  
                pygame.draw.rect(destination_surface, (0, 200, 0, 180), (0, 0, CELL_SIZE, CELL_SIZE), border_radius=10)
                self.screen.blit(destination_surface, (destination_x * CELL_SIZE, destination_y * CELL_SIZE))
                pygame.draw.rect(self.screen, (0, 255, 0), 
                                pygame.Rect(destination_x * CELL_SIZE, destination_y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 
                                width=3, border_radius=10)

    
    def update_grid(self, cubes):
        self.draw_grid()
        for cube in cubes:
            cube.draw(self.screen)
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            current_time = pygame.time.get_ticks()
            
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
            
            # Automatic movement
            if current_time - self.last_move_time >= MOVE_INTERVAL:
                for cube in self.cubes:
                    if not cube.is_reached() and not self.selected_cube:
                        cube.move()
                self.last_move_time = current_time
            
            self.draw_grid()
            for cube in self.cubes:
                cube.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()