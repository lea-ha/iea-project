import pygame
from typing import List, Tuple, Set
from algorithm_selector import AlgorithmSelector
from config import WIDTH, HEIGHT, CELL_SIZE, BACKGROUND, GRID_LINES
from request import Coordinate
from time import time


class DestinationSelector:
    """
    Class to handle destination selection and obstacle placement for the game.
    """
    
    def __init__(self) -> None:
        """
        Initialize the destination selector.
        """
        pygame.init()
        
        # Accomodating the algorithm selection panel
        extended_width = WIDTH + 200  
        self.screen = pygame.display.set_mode((extended_width, HEIGHT))
        pygame.display.set_caption("Shapeshifter")
        self.clock = pygame.time.Clock()
        
        # Grid dimensions 
        self.grid_width = WIDTH // CELL_SIZE
        self.grid_height = HEIGHT // CELL_SIZE
        
        # Fixed origins (bottom two rows)
        self.fixed_origins = self.generate_fixed_origins()
        
        # Selection state for destinations
        self.selected_destinations: Set[Tuple[int, int]] = set()
        self.max_destinations = len(self.fixed_origins)  # Match number of origins
        
        # Obstacles
        self.obstacles: Set[Tuple[int, int]] = set()
        
        # Selection mode
        self.mode = "destination"  # Can be "destination" or "obstacle"
        
        # Button areas
        self.button_height = 40
        self.start_button_rect = pygame.Rect(WIDTH - 210, HEIGHT - self.button_height - 10, 200, self.button_height)
        self.mode_button_rect = pygame.Rect(10, HEIGHT - self.button_height - 10, 200, self.button_height)
        
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
            
        # Check if toggle mode button was clicked
        if self.mode_button_rect.collidepoint(pos):
            self.toggle_mode()
            return False
            
        # Check if start button was clicked
        if self.start_button_rect.collidepoint(pos):
            return len(self.selected_destinations) > 0
        
        grid_x, grid_y = pos[0] // CELL_SIZE, pos[1] // CELL_SIZE
        grid_pos = (grid_x, grid_y)
        
        # Only process valid grid positions
        if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
            # Don't allow selecting the bottom two rows for destinations or obstacles
            if grid_y >= self.grid_height - 2:
                return False
            
            # Handle clicks based on mode
            if self.mode == "destination":
                return self.handle_destination_click(grid_pos)
            elif self.mode == "obstacle":
                return self.handle_obstacle_click(grid_pos)
                
        return False
    
    def handle_destination_click(self, grid_pos: Tuple[int, int]) -> bool:
        """Handle clicks when in destination selection mode."""
        # Don't allow selecting obstacles as destinations
        if grid_pos in self.obstacles:
            return False
            
        # Toggle destination selection
        if grid_pos in self.selected_destinations:
            self.selected_destinations.remove(grid_pos)
        elif len(self.selected_destinations) < self.max_destinations:
            self.selected_destinations.add(grid_pos)
            
        return False
        
    def handle_obstacle_click(self, grid_pos: Tuple[int, int]) -> bool:
        """Handle clicks when in obstacle placement mode."""
        # Don't allow selecting destinations as obstacles
        if grid_pos in self.selected_destinations:
            return False
            
        # Toggle obstacle selection
        if grid_pos in self.obstacles:
            self.obstacles.remove(grid_pos)
        else:
            self.obstacles.add(grid_pos)
            
        return False
        
    def toggle_mode(self) -> None:
        """Toggle between destination and obstacle selection modes."""
        if self.mode == "destination":
            self.mode = "obstacle"
        else:
            self.mode = "destination"
        
    def run(self) -> Tuple[List[List[int]], List[List[int]], List[List[int]]]:
        """
        Run the destination selection interface.
        Returns (origins, destinations, obstacles) lists in the format needed for the API.
        """
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return [], [], []  # Empty lists if user quits
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
        obstacles_list = [[x, y] for x, y in self.obstacles]
        
        return origins, destinations, obstacles_list
        
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
        # Draw origins (green cubes at the bottom)
        for x, y in self.fixed_origins:
            origin_rect = pygame.Rect(x * CELL_SIZE + 5, y * CELL_SIZE + 5, CELL_SIZE - 10, CELL_SIZE - 10)
            pygame.draw.rect(self.screen, (0, 200, 0), origin_rect, border_radius=10)
        
        # Draw selected destinations (red cubes with numbers)
        for i, (x, y) in enumerate(self.selected_destinations):
            dest_rect = pygame.Rect(x * CELL_SIZE + 5, y * CELL_SIZE + 5, CELL_SIZE - 10, CELL_SIZE - 10)
            pygame.draw.rect(self.screen, (200, 0, 0), dest_rect, border_radius=10)
            
            font = pygame.font.SysFont('Arial', 18)
            id_text = font.render(str(i + 1), True, (255, 255, 255))
            text_rect = id_text.get_rect(center=(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2))
            self.screen.blit(id_text, text_rect)
            
        # Draw obstacles (gray blocks)
        for x, y in self.obstacles:
            obstacle_rect = pygame.Rect(x * CELL_SIZE + 2, y * CELL_SIZE + 2, CELL_SIZE - 4, CELL_SIZE - 4)
            pygame.draw.rect(self.screen, (80, 80, 80), obstacle_rect)
            
            # Add a cross pattern to make obstacles more visually distinct
            pygame.draw.line(self.screen, (40, 40, 40), 
                            (x * CELL_SIZE + 2, y * CELL_SIZE + 2),
                            (x * CELL_SIZE + CELL_SIZE - 4, y * CELL_SIZE + CELL_SIZE - 4), 3)
            pygame.draw.line(self.screen, (40, 40, 40), 
                            (x * CELL_SIZE + CELL_SIZE - 4, y * CELL_SIZE + 2),
                            (x * CELL_SIZE + 2, y * CELL_SIZE + CELL_SIZE - 4), 3)
        
        # Draw start button
        pygame.draw.rect(self.screen, (100, 200, 100), self.start_button_rect, border_radius=5)
        
        font = pygame.font.SysFont('Arial', 18)
        start_text = "Start Simulation"
        start_surf = font.render(start_text, True, (255, 255, 255))
        start_rect = start_surf.get_rect(center=self.start_button_rect.center)
        self.screen.blit(start_surf, start_rect)
        
        # Draw mode toggle button
        mode_color = (100, 100, 200) if self.mode == "destination" else (150, 150, 150)
        pygame.draw.rect(self.screen, mode_color, self.mode_button_rect, border_radius=5)
        
        mode_text = "Mode: Destination" if self.mode == "destination" else "Mode: Obstacle"
        mode_surf = font.render(mode_text, True, (255, 255, 255))
        mode_rect = mode_surf.get_rect(center=self.mode_button_rect.center)
        self.screen.blit(mode_surf, mode_rect)
        
        # Status info
        status_font = pygame.font.SysFont('Arial', 16)
        status = f"Select destinations: {len(self.selected_destinations)}/{self.max_destinations}"
        status_surf = status_font.render(status, True, (255, 255, 255))
        self.screen.blit(status_surf, (10, 10))
        
        obstacles_info = f"Obstacles placed: {len(self.obstacles)}"
        obstacles_surf = status_font.render(obstacles_info, True, (255, 255, 255))
        self.screen.blit(obstacles_surf, (10, 30))
        
        # Mode-specific instructions
        if self.mode == "destination":
            instruction = "Click to select/deselect destinations."
        else:
            instruction = "Click to place/remove obstacles."
        inst_surf = status_font.render(instruction, True, (255, 255, 255))
        self.screen.blit(inst_surf, (10, 50))
        
    def get_selected_algorithm(self) -> str:
        """Return the currently selected algorithm."""
        return self.algorithm_selector.get_selected_algorithm()
        
    def is_morphing_enabled(self) -> bool:
        """Return whether morphing is enabled from the algorithm selector."""
        return self.algorithm_selector.is_morphing_enabled()
    
    def get_selected_priority(self) -> str:
        """Return the currently selected priority strategy."""
        return self.algorithm_selector.get_selected_priority()
    
    def get_selected_conflict_resolution(self) -> str:
        """Return the currently selected conflict resolution strategy."""
        return self.algorithm_selector.get_selected_conflict_resolution()
        
    def is_diagonals_enabled(self) -> bool:
        """Return whether diagonal movement is enabled from the algorithm selector."""
        return self.algorithm_selector.is_diagonals_enabled()