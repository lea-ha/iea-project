import pygame
from typing import List, Tuple, Set
from algorithm_selector import AlgorithmSelector
from config import WIDTH, HEIGHT, CELL_SIZE, BACKGROUND, GRID_LINES
from request import Coordinate
from time import time


class DestinationSelector:
    """
    Class to handle destination selection for the game.
    """
    
    def __init__(self) -> None:
        """
        Initialize the destination selector.
        """
        pygame.init()
        
        # Accomodating the algorithm selection panel
        extended_width = WIDTH + 200  
        self.screen = pygame.display.set_mode((extended_width, HEIGHT))
        pygame.display.set_caption("Path Planning Setup")
        self.clock = pygame.time.Clock()
        
        # Grid dimensions 
        self.grid_width = WIDTH // CELL_SIZE
        self.grid_height = HEIGHT // CELL_SIZE
        
        # Fixed origins
        self.fixed_origins = self.generate_fixed_origins()
        
        # Selection state for destinations
        self.selected_destinations: Set[Tuple[int, int]] = set()
        self.max_destinations = len(self.fixed_origins)  # Match number of origins
        
        # Button area
        self.button_height = 40
        self.start_button_rect = pygame.Rect(WIDTH - 210, HEIGHT - self.button_height - 10, 200, self.button_height)
        
        self.algorithm_selector = AlgorithmSelector()
        
    def generate_fixed_origins(self) -> List[Tuple[int, int]]:
        """
        Generate fixed origins from the bottom two rows.
        """
        origins = []
        # Bottom two rows
        for y in range(self.grid_height - 2, self.grid_height):
            for x in range(self.grid_width):
                origins.append((x, y))
        return origins
        
    def handle_click(self, pos: Tuple[int, int]) -> bool:
        """
        Handle mouse clicks during selection.
        Returns True if start button is clicked.
        """
        # Check if this is an algorithm selection click
        if self.algorithm_selector.handle_click(pos):
            return False
            
        grid_x, grid_y = pos[0] // CELL_SIZE, pos[1] // CELL_SIZE
        
        if self.start_button_rect.collidepoint(pos):
            return len(self.selected_destinations) > 0
        
        if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
            grid_pos = (grid_x, grid_y)
            
            # Don't allow selecting the bottom two rows
            if grid_y >= self.grid_height - 2:
                return False
                
            # Toggle destination selection
            if grid_pos in self.selected_destinations:
                self.selected_destinations.remove(grid_pos)
            elif len(self.selected_destinations) < self.max_destinations:
                self.selected_destinations.add(grid_pos)
                
        return False
        
    def run(self) -> Tuple[List[List[int]], List[List[int]]]:
        """
        Run the destination selection interface.
        Returns (origins, destinations) lists in the format needed for the API.
        """
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return [], []  # Empty lists if user quits
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                    if self.handle_click(event.pos):
                        running = False  # Exit if start button clicked
            
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
            
        # Convert to format needed for API
        used_origins = self.fixed_origins[:len(self.selected_destinations)]
        origins = [[x, y] for x, y in used_origins]
        destinations = [[x, y] for x, y in self.selected_destinations]
        
        return origins, destinations
        
    def draw(self) -> None:
        """
        Draw the selection interface.
        """
        self.screen.fill(BACKGROUND)
        self.draw_grid()
        self.draw_selection()
        
        # Draw the algorithm selector
        self.algorithm_selector.draw(self.screen)
        
        pygame.display.flip()
        
    def draw_grid(self) -> None:
        """
        Draw the grid lines.
        """
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_LINES, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_LINES, (0, y), (WIDTH, y))
            
    def draw_selection(self) -> None:
        """
        Draw the selection interface elements.
        """
        for x, y in self.fixed_origins:
            origin_rect = pygame.Rect(x * CELL_SIZE + 5, y * CELL_SIZE + 5, CELL_SIZE - 10, CELL_SIZE - 10)
            pygame.draw.rect(self.screen, (0, 200, 0), origin_rect, border_radius=10)
        
        for i, (x, y) in enumerate(self.selected_destinations):
            dest_rect = pygame.Rect(x * CELL_SIZE + 5, y * CELL_SIZE + 5, CELL_SIZE - 10, CELL_SIZE - 10)
            pygame.draw.rect(self.screen, (200, 0, 0), dest_rect, border_radius=10)
            
            font = pygame.font.SysFont('Arial', 18)
            id_text = font.render(str(i + 1), True, (255, 255, 255))
            text_rect = id_text.get_rect(center=(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2))
            self.screen.blit(id_text, text_rect)
        
        pygame.draw.rect(self.screen, (100, 200, 100), self.start_button_rect, border_radius=5)
        
        font = pygame.font.SysFont('Arial', 18)
        start_text = "Start Simulation"
        start_surf = font.render(start_text, True, (255, 255, 255))
        start_rect = start_surf.get_rect(center=self.start_button_rect.center)
        self.screen.blit(start_surf, start_rect)
        
        status_font = pygame.font.SysFont('Arial', 16)
        status = f"Select destinations: {len(self.selected_destinations)}/{self.max_destinations}"
        status_surf = status_font.render(status, True, (255, 255, 255))
        self.screen.blit(status_surf, (10, 10))
        
        instruction = "Click to select/deselect destinations."
        inst_surf = status_font.render(instruction, True, (255, 255, 255))
        self.screen.blit(inst_surf, (10, 30))
        
        # Display selected algorithm
        # algo_text = f"Algorithm: {self.algorithm_selector.get_selected_algorithm()}"
        # algo_surf = status_font.render(algo_text, True, (255, 255, 255))
        # self.screen.blit(algo_surf, (10, 50))
        
    def get_selected_algorithm(self) -> str:
        """Return the currently selected algorithm."""
        return self.algorithm_selector.get_selected_algorithm()
